"""
Modèle de données en constellation (couche Gold) - Groupe 4, Sephora Pays-Bas
=============================================================================

Constellation : plusieurs schémas en étoile partagent les mêmes dimensions ;
deux liens en flocon (dim_produit -> dim_marque, dim_ville -> dim_pays).

Lit les tables nettoyées de data/silver/ et construit :
  - 8 dimensions (tables descriptives, préfixe dim_) ;
  - 10 tables de faits (mesures, préfixe fact_), chacune à un seul niveau de détail ;
  - des vues à plat (data/gold/vues/), prêtes à brancher dans un outil de dashboard ;
  - un tableau de synthèse des KPI (vues/vue_kpi.csv).
Puis lance des contrôles de qualité (clés uniques, aucune clé orpheline, grain unique,
cohérence des calculs).

Bonnes pratiques reprises de feature/etl-star-ai : un grain par table de faits, jamais de
croisement produit × ville, clés numériques stables, contrôles automatiques en fin d'exécution.

Exécution :  python data/gold/build_gold.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"
VUES = GOLD / "vues"

DATE_RELEVE = "2026-11-12"

# Score de désirabilité (formule du projet)
POIDS_TRENDS, POIDS_AVIS, POIDS_EXCLU = 0.40, 0.35, 0.25

# Groupes de marques
GROUPES = {
    "Sephora": "Enseigne étudiée",
    "Sephora Collection": "Marque maison Sephora",
    "Fenty Beauty": "LVMH", "Benefit Cosmetics": "LVMH", "Make Up For Ever": "LVMH",
    "Rhode": "Marque tendance", "Rare Beauty": "Marque tendance", "Huda Beauty": "Marque tendance",
    "Makeup By Mario": "Marque tendance", "Haus Labs": "Marque tendance", "Kylie Cosmetics": "Marque tendance",
    "Too Faced": "Marque classique", "Tarte": "Marque classique",
}

# Hypothèses des scénarios (voir docs/previsions/rentabilite_villes_nl.md et marges_nl.md)
SCENARIOS = pd.DataFrame([
    dict(scenario_id=1, scenario="Pessimiste", ordre=1, part_marche_visee_2029_pct=1.5, taux_marge_france_pct=38.0,
         nb_etp=7, charges_patronales_pct=35, cout_transport_eur_km=2.0, cout_ouverture_eur_m2=1200),
    dict(scenario_id=2, scenario="Central", ordre=2, part_marche_visee_2029_pct=3.0, taux_marge_france_pct=44.0,
         nb_etp=6, charges_patronales_pct=30, cout_transport_eur_km=1.8, cout_ouverture_eur_m2=1000),
    dict(scenario_id=3, scenario="Optimiste", ordre=3, part_marche_visee_2029_pct=5.0, taux_marge_france_pct=48.0,
         nb_etp=5, charges_patronales_pct=25, cout_transport_eur_km=1.6, cout_ouverture_eur_m2=800),
])
HYPOTHESES_COMMUNES = dict(surface_m2=270, salaire_brut_mensuel_eur=2750, pecule_vacances_pct=8,
                           montee_en_charge="2027 : 60 % / 2028 : 85 % / 2029 : 100 %",
                           entrepot="Saran (Loiret)", livraisons_par_an=52)

ENSEIGNES = pd.DataFrame([
    dict(enseigne_id=1, enseigne="Sephora", groupe="LVMH", type_enseigne="Distributeur beauté (enseigne étudiée)"),
    dict(enseigne_id=2, enseigne="Douglas", groupe="Douglas Group", type_enseigne="Parfumerie sélective"),
    dict(enseigne_id=3, enseigne="ICI Paris XL", groupe="A.S. Watson", type_enseigne="Parfumerie sélective"),
    dict(enseigne_id=4, enseigne="De Bijenkorf", groupe="", type_enseigne="Grand magasin"),
])

OUVERTURES_BELGIQUE = {"2026-06-25": "Ouverture Sephora Docks Bruxsel", "2026-07-09": "Ouverture Sephora City2",
                       "2026-09-24": "Ouverture Sephora Médiacité (Liège)"}
VILLES_GEO = {"Amsterdam": "Amsterdam, Netherlands", "Rotterdam": "Rotterdam, Netherlands",
              "Utrecht": "Utrecht, Netherlands", "La Haye": "The Hague, Netherlands"}


def lire(nom):
    return pd.read_csv(SILVER / f"{nom}.csv")


def date_id(d):
    return int(pd.Timestamp(d).strftime("%Y%m%d"))


def id_annee(a):
    return int(a) * 10000 + 101          # 1er janvier de l'année, pour les faits annuels


# ===========================================================================
# Dimensions
# ===========================================================================
def dim_marque(produits, trends):
    marques = sorted(set(produits.brand) | set(trends.marque))
    moy = trends.groupby("marque").score_trends.mean()
    # Option A : échelle 0-100 calculée sur les marques seulement (l'enseigne « Sephora » est exclue)
    max_marques = moy.drop("Sephora").max()
    lvmh = produits.groupby("brand").is_lvmh.first()
    df = pd.DataFrame({"marque": marques})
    df.insert(0, "marque_id", range(1, len(df) + 1))
    df["groupe_marque"] = df.marque.map(GROUPES)
    df["is_enseigne"] = (df.marque == "Sephora").astype(int)
    df["is_lvmh"] = df.marque.map(lvmh).fillna(df.marque.eq("Sephora")).astype(int)
    df["suivie_google_trends"] = df.marque.isin(moy.index).astype(int)
    df["presente_echantillon"] = df.marque.isin(produits.brand).astype(int)
    df["nb_produits_echantillon"] = df.marque.map(produits.brand.value_counts()).fillna(0).astype(int)
    df["score_trends_moyen_12m"] = df.marque.map(moy).round(2)
    df["score_trends_marque_0_100"] = (df.marque.map(moy) / max_marques * 100).round(1)
    df.loc[df.is_enseigne == 1, "score_trends_marque_0_100"] = pd.NA      # l'enseigne n'est pas une marque
    return df


def dim_produit(produits, marques):
    mid = marques.set_index("marque").marque_id
    return pd.DataFrame({
        "produit_id": produits.product_id,
        "produit": produits.product_name,
        "marque_id": produits.brand.map(mid),
        "marque": produits.brand,
        "sous_categorie": produits.subcategory,
        "type_produit": produits.product_type,
        "variante": produits.variant.fillna(""),
        "rang_sephora_fr": produits.rank_sephora_fr.astype("Int64"),
        "is_exclusif": produits.is_verified_exclusive,
        "statut_concurrence": produits.is_verified_exclusive.map({1: "Exclusif", 0: "Partagé"}),
        "is_lvmh": produits.is_lvmh,
        "in_top10_sephora_fr": produits.in_top10_sephora_fr,
        "is_mini_format": produits.is_mini_format,
    })


def dim_ville(villes):
    return pd.DataFrame({
        "ville_id": villes.city_id,
        "ville": villes.ville,
        "ville_geo": villes.ville.map(VILLES_GEO),
        "pays_id": "NL",
        "rue_reference_loyer": villes.rue_reference_loyer,
        "distance_bruxelles_estimee": villes.distance_bruxelles_estimee,
    })


def dim_scenario():
    df = SCENARIOS.copy()
    for k, v in HYPOTHESES_COMMUNES.items():
        df[k] = v
    return df


def dim_canal(canaux):
    c = canaux.drop_duplicates("canal")[["canal", "est_magasin_physique"]].reset_index(drop=True)
    c.insert(0, "canal_id", range(1, len(c) + 1))
    c["est_magasin_physique"] = c.est_magasin_physique.astype(int)
    return c


def dim_pays(pays):
    return pays.rename(columns={"country_code": "pays_id"})


def dim_date(dates):
    d = pd.to_datetime(pd.Series(sorted(set(dates))))
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
            "octobre", "novembre", "décembre"]
    return pd.DataFrame({
        "date_id": d.dt.strftime("%Y%m%d").astype(int),
        "date": d.dt.strftime("%Y-%m-%d"),
        "annee": d.dt.year,
        "trimestre": d.dt.quarter,
        "mois": d.dt.month,
        "mois_libelle": d.dt.month.map(lambda m: mois[m - 1]),
        "semaine_iso": d.dt.isocalendar().week.astype(int),
    })


# ===========================================================================
# Tables de faits
# ===========================================================================
def fact_prix_produit(produits, prix_vente, marques):
    p = produits.merge(prix_vente[["product_id", "price_sephora_nl_ttc", "price_sephora_nl_ht",
                                   "ecart_ht_vs_france_pct"]], on="product_id")
    m = marques.set_index("marque")
    nl_min = p[["price_douglas_nl_ttc", "price_iciparisxl_nl_ttc"]].min(axis=1)
    fr_ht = (p.price_sephora_fr_ttc / 1.20).round(2)
    score_trends = p.brand.map(m.score_trends_marque_0_100)
    score_avis = (p.rating_sephora_fr / 5 * 100).round(1)
    bonus = p.is_verified_exclusive * 100
    desir = (POIDS_TRENDS * score_trends + POIDS_AVIS * score_avis + POIDS_EXCLU * bonus).round(1)
    return pd.DataFrame({
        "produit_id": p.product_id,
        "marque_id": p.brand.map(m.marque_id),
        "date_id": date_id(DATE_RELEVE),
        "prix_sephora_fr_ttc": p.price_sephora_fr_ttc,
        "prix_sephora_fr_ht": fr_ht,
        "prix_douglas_nl_ttc": p.price_douglas_nl_ttc,
        "prix_iciparisxl_nl_ttc": p.price_iciparisxl_nl_ttc,
        "prix_concurrent_nl_min_ttc": nl_min,
        "indice_prix_nl_fr_ttc": (nl_min / p.price_sephora_fr_ttc * 100).round(1),
        "indice_prix_nl_fr_ht": ((nl_min / 1.21) / fr_ht * 100).round(1),
        "prix_sephora_nl_ttc": p.price_sephora_nl_ttc,
        "prix_sephora_nl_ht": p.price_sephora_nl_ht,
        "ecart_prix_sephora_nl_vs_fr_ht_pct": p.ecart_ht_vs_france_pct,
        "note_sephora_fr": p.rating_sephora_fr,
        "nb_avis_sephora_fr": p.review_count_sephora_fr,
        "score_trends_marque_0_100": score_trends,
        "score_avis_0_100": score_avis,
        "bonus_exclusivite_0_100": bonus,
        "score_desirabilite": desir,
        "nb_produits": 1,
    })


def fact_marge_produit(marges, scenarios):
    sid = scenarios.set_index("scenario").scenario_id
    return pd.DataFrame({
        "produit_id": marges.product_id,
        "scenario_id": marges.scenario.map(sid),
        "prix_sephora_nl_ht": marges.price_sephora_nl_ht,
        "cout_achat_ht_eur": marges.cout_achat_ht_eur,
        "marge_brute_eur": marges.marge_brute_nl_eur,
        "taux_marge_brute_pct": marges.taux_marge_brute_nl_pct,
    })


def fact_recherche_google(trends, marques):
    t = trends.copy()
    t["semaine"] = pd.to_datetime(t.semaine)
    sem_evt = {}
    for d, evt in OUVERTURES_BELGIQUE.items():
        debut = t.semaine[t.semaine <= pd.Timestamp(d)].max()      # semaine (débutant le dimanche) contenant la date
        sem_evt[debut] = evt
    pic = t.groupby("semaine").score_trends.sum().idxmax()
    return pd.DataFrame({
        "marque_id": t.marque.map(marques.set_index("marque").marque_id),
        "date_id": t.semaine.dt.strftime("%Y%m%d").astype(int),
        "score_trends": t.score_trends,
        "is_semaine_pic": (t.semaine == pic).astype(int),
        "evenement": t.semaine.map(sem_evt).fillna(""),
    })


def fact_ville(villes, renta):
    marche = renta.drop_duplicates("city_id").set_index("city_id").marche_maquillage_ville_eur
    return pd.DataFrame({
        "ville_id": villes.city_id,
        "date_id": date_id(DATE_RELEVE),
        "population_totale": villes.population_totale,
        "population_15_44": villes.population_15_44,
        "part_15_44_pct": villes.part_15_44_pct,
        "marche_maquillage_ville_eur": villes.city_id.map(marche),
        "nb_douglas": villes.nb_douglas,
        "nb_ici_paris_xl": villes.nb_ici_paris_xl,
        "nb_bijenkorf": villes.nb_bijenkorf,
        "nb_douglas_ici": villes.nb_douglas_ici,
        "nb_concurrents_total": villes.nb_concurrents_total,
        "concurrents_pour_100k_hab": villes.concurrents_pour_100k_hab,
        "pop_15_44_par_concurrent": villes.pop_15_44_par_concurrent,
        "loyer_prime_m2_an_eur": villes.loyer_prime_m2_an_eur,
        "loyer_annuel_270m2_eur": villes.loyer_prime_m2_an_eur * HYPOTHESES_COMMUNES["surface_m2"],
        "distance_saran_km": villes.distance_hub_saran_km,
        "duree_saran_min": villes.duree_route_saran_min,
        "distance_bruxelles_km": villes.distance_bruxelles_km,
    })


def fact_magasin_concurrent(magasins):
    eid = ENSEIGNES.set_index("enseigne").enseigne_id
    return pd.DataFrame({
        "magasin_id": magasins.store_id,
        "enseigne_id": magasins.enseigne.map(eid),
        "ville_id": magasins.city_id.astype("Int64"),
        "ville_magasin": magasins.ville,
        "nom_magasin": magasins.nom_magasin,
        "code_postal": magasins.code_postal,
        "latitude": magasins.latitude,
        "longitude": magasins.longitude,
        "is_ville_cible": magasins.is_ville_cible,
        "has_gps": magasins.has_gps,
        "nb_magasins": 1,
    })


def fact_rentabilite(renta, scenarios):
    sid = scenarios.set_index("scenario").scenario_id
    r = renta.copy()
    out = pd.DataFrame({
        "ville_id": r.city_id,
        "scenario_id": r.scenario.map(sid),
        "date_id": r.annee.map(id_annee),
        "annee": r.annee,
    })
    cols = ["part_de_marche_visee_pct", "ca_ttc_eur", "ca_ht_eur", "taux_marge_pct", "marge_brute_eur", "loyer_eur",
            "personnel_eur", "transport_eur", "resultat_annuel_eur", "cout_ouverture_eur", "resultat_cumule_eur",
            "ca_ht_point_mort_eur", "part_de_marche_point_mort_pct", "rentable"]
    for c in cols:
        out[c] = r[c]
    out["couts_fixes_eur"] = r.loyer_eur + r.personnel_eur + r.transport_eur
    return out


def fact_marche(marche):
    return pd.DataFrame({
        "date_id": marche.annee.map(id_annee),
        "annee": marche.annee,
        "perimetre": marche.perimetre,
        "valeur_meur": marche.valeur_meur,
        "croissance_annuelle_pct": marche.croissance_annuelle_pct,
        "statut": marche.statut,
        "source": marche.source,
    })


def fact_canal(canaux, dcanal):
    eid = ENSEIGNES.set_index("enseigne").enseigne_id
    return pd.DataFrame({
        "canal_id": canaux.canal.map(dcanal.set_index("canal").canal_id),
        "enseigne_id": canaux.enseigne.map(eid).astype("Int64"),
        "date_id": id_annee(2020),
        "ventes_meur": canaux.ventes_meur_2020,
        "part_magasins_physiques_pct": canaux.part_magasins_physiques_pct,
        "part_marche_total_pct": canaux.part_marche_total_pct,
        "statut": canaux.statut,
        "source": canaux.source,
    })


def fact_sephora_indicateur(ind):
    return pd.DataFrame({
        "indicateur_id": ind.indicateur_id,
        "enseigne_id": 1,
        "date_id": ind.annee.map(id_annee),
        "categorie": ind.categorie,
        "indicateur": ind.indicateur,
        "valeur": ind.valeur,
        "unite": ind.unite,
        "perimetre": ind.perimetre,
        "fiabilite": ind.fiabilite,
        "a_reverifier": ind.a_reverifier,
        "source": ind.source,
        "url": ind.url,
    })


def fact_sephora_magasin_belgique(mag):
    d = pd.to_datetime(mag.date_ouverture)
    return pd.DataFrame({
        "magasin_be_id": range(1, len(mag) + 1),
        "enseigne_id": 1,
        "date_id": d.dt.strftime("%Y%m%d").astype("Int64"),
        "magasin": mag.magasin,
        "ville": mag.ville,
        "statut": mag.statut,
        "surface_m2": mag.surface_m2.astype("Int64"),
        "nb_magasins": 1,
        "source": mag.source,
    })


# ===========================================================================
# Vues à plat et KPI
# ===========================================================================
def vues(t):
    d = t
    v = {}
    v["vue_produits"] = (d["fact_prix_produit"]
                         .merge(d["dim_produit"].drop(columns="marque_id"), on="produit_id")
                         .merge(d["dim_marque"][["marque_id", "groupe_marque"]], on="marque_id"))
    v["vue_marges"] = (d["fact_marge_produit"]
                       .merge(d["dim_produit"][["produit_id", "produit", "marque", "sous_categorie", "statut_concurrence"]],
                              on="produit_id")
                       .merge(d["dim_scenario"][["scenario_id", "scenario", "ordre"]], on="scenario_id"))
    v["vue_rentabilite"] = (d["fact_rentabilite"]
                            .merge(d["dim_ville"][["ville_id", "ville", "ville_geo"]], on="ville_id")
                            .merge(d["dim_scenario"], on="scenario_id"))
    v["vue_recherches_google"] = (d["fact_recherche_google"]
                                  .merge(d["dim_marque"][["marque_id", "marque", "groupe_marque", "is_enseigne"]],
                                         on="marque_id")
                                  .merge(d["dim_date"][["date_id", "date", "annee", "mois", "mois_libelle"]], on="date_id"))
    v["vue_villes"] = d["fact_ville"].merge(d["dim_ville"], on="ville_id")
    v["vue_magasins_concurrents"] = d["fact_magasin_concurrent"].merge(
        ENSEIGNES[["enseigne_id", "enseigne", "groupe"]], on="enseigne_id")
    v["vue_parts_de_marche"] = (d["fact_canal"].merge(d["dim_canal"], on="canal_id")
                                .merge(ENSEIGNES[["enseigne_id", "enseigne"]], on="enseigne_id", how="left"))
    v["vue_parts_de_marche"]["libelle"] = v["vue_parts_de_marche"].enseigne.fillna(v["vue_parts_de_marche"].canal)
    return v


def kpi(t):
    p, mq = t["fact_prix_produit"], t["dim_marque"]
    marche = t["fact_marche"]
    mk = marche[marche.perimetre == "Maquillage NL"].set_index("annee").valeur_meur
    tcac = ((mk[2024] / mk[2019]) ** (1 / 5) - 1) * 100
    canaux = t["fact_canal"]
    duo = canaux[canaux.enseigne_id.isin([2, 3])]
    partages = p[p.prix_concurrent_nl_min_ttc.notna()]
    g = t["fact_recherche_google"].merge(t["dim_date"][["date_id", "date"]], on="date_id")
    seph = g[g.marque_id == mq.loc[mq.is_enseigne == 1, "marque_id"].iloc[0]].sort_values("date")
    evol = (seph.score_trends.tail(13).mean() / seph.score_trends.head(13).mean() - 1) * 100
    r = t["fact_rentabilite"]
    r29 = r[r.annee == 2029]
    best = r29.loc[r29.resultat_annuel_eur.idxmax()]
    villes = t["dim_ville"].set_index("ville_id").ville
    scen = t["dim_scenario"].set_index("scenario_id").scenario
    marges = t["fact_marge_produit"]
    m_central = marges[marges.scenario_id == 2]
    rows = [
        ("Réalisable", "Taille du marché du maquillage aux Pays-Bas (2024)", mk[2024], "M€", "fact_marche"),
        ("Réalisable", "Croissance annuelle moyenne du marché du maquillage 2019-2024", round(tcac, 1), "%/an", "fact_marche"),
        ("Réalisable", "Part de marché Douglas + ICI Paris XL (ventes en magasins physiques)",
         round(duo.part_magasins_physiques_pct.sum(), 1), "%", "fact_canal"),
        ("Réalisable", "Indice de prix Pays-Bas / France (produits partagés, TTC)",
         round(partages.indice_prix_nl_fr_ttc.mean(), 1), "base 100 = France", "fact_prix_produit"),
        ("Réalisable", "Part des produits en exclusivité vérifiée", round(t["dim_produit"].is_exclusif.mean() * 100, 1),
         "%", "dim_produit"),
        ("Réalisable", "Évolution des recherches « sephora » aux Pays-Bas (13 dernières vs 13 premières semaines)",
         round(evol, 1), "%", "fact_recherche_google"),
        ("Réalisable", "Score de désirabilité moyen : produits exclusifs",
         round(p[p.bonus_exclusivite_0_100 == 100].score_desirabilite.mean(), 1), "/100", "fact_prix_produit"),
        ("Réalisable", "Score de désirabilité moyen : produits partagés",
         round(p[p.bonus_exclusivite_0_100 == 0].score_desirabilite.mean(), 1), "/100", "fact_prix_produit"),
        ("Rentable", "Marge brute moyenne par produit (scénario central)", round(m_central.marge_brute_eur.mean(), 2),
         "€", "fact_marge_produit"),
        ("Rentable", "Taux de marge brute moyen (scénario central)", round(m_central.taux_marge_brute_pct.mean(), 1),
         "%", "fact_marge_produit"),
        ("Rentable", "Nombre de combinaisons ville × scénario rentables en 2029",
         int(r29.rentable.sum()), f"sur {len(r29)}", "fact_rentabilite"),
        ("Rentable", f"Meilleur résultat annuel 2029 ({villes[best.ville_id]}, {scen[best.scenario_id]})",
         round(best.resultat_annuel_eur), "€", "fact_rentabilite"),
        ("Rentable", "Part de marché minimale nécessaire au point mort",
         round(r.part_de_marche_point_mort_pct.min(), 1), "%", "fact_rentabilite"),
    ]
    out = pd.DataFrame(rows, columns=["axe", "kpi", "valeur", "unite", "table_source"])
    out.insert(0, "kpi_id", range(1, len(out) + 1))
    return out


# ===========================================================================
# Contrôles
# ===========================================================================
def controler(t):
    ok = True

    def check(nom, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'OK ' if cond else '!! '} {nom}")

    print("--- CONTRÔLES DE QUALITÉ ---")
    cles = {"dim_produit": "produit_id", "dim_marque": "marque_id", "dim_ville": "ville_id", "dim_date": "date_id",
            "dim_scenario": "scenario_id", "dim_enseigne": "enseigne_id", "dim_canal": "canal_id", "dim_pays": "pays_id"}
    for dim, k in cles.items():
        check(f"{dim} : clé {k} unique et non vide", t[dim][k].is_unique and t[dim][k].notna().all())

    liens = [
        ("fact_prix_produit", "produit_id", "dim_produit"), ("fact_prix_produit", "marque_id", "dim_marque"),
        ("fact_prix_produit", "date_id", "dim_date"),
        ("fact_marge_produit", "produit_id", "dim_produit"), ("fact_marge_produit", "scenario_id", "dim_scenario"),
        ("fact_recherche_google", "marque_id", "dim_marque"), ("fact_recherche_google", "date_id", "dim_date"),
        ("fact_ville", "ville_id", "dim_ville"), ("fact_ville", "date_id", "dim_date"),
        ("fact_magasin_concurrent", "enseigne_id", "dim_enseigne"), ("fact_magasin_concurrent", "ville_id", "dim_ville"),
        ("fact_rentabilite", "ville_id", "dim_ville"), ("fact_rentabilite", "scenario_id", "dim_scenario"),
        ("fact_rentabilite", "date_id", "dim_date"),
        ("fact_marche", "date_id", "dim_date"),
        ("fact_canal", "canal_id", "dim_canal"), ("fact_canal", "enseigne_id", "dim_enseigne"),
        ("fact_canal", "date_id", "dim_date"),
        ("fact_sephora_indicateur", "enseigne_id", "dim_enseigne"), ("fact_sephora_indicateur", "date_id", "dim_date"),
        ("fact_sephora_magasin_belgique", "enseigne_id", "dim_enseigne"),
        ("fact_sephora_magasin_belgique", "date_id", "dim_date"),
        ("dim_produit", "marque_id", "dim_marque"), ("dim_ville", "pays_id", "dim_pays"),
    ]
    for fact, fk, dim in liens:
        orph = set(t[fact][fk].dropna()) - set(t[dim][cles[dim]])
        check(f"{fact}.{fk} -> {dim} : aucune clé orpheline", not orph)

    grains = {"fact_prix_produit": ["produit_id"], "fact_marge_produit": ["produit_id", "scenario_id"],
              "fact_recherche_google": ["marque_id", "date_id"], "fact_ville": ["ville_id"],
              "fact_magasin_concurrent": ["magasin_id"], "fact_rentabilite": ["ville_id", "scenario_id", "annee"],
              "fact_marche": ["annee", "perimetre"], "fact_canal": ["canal_id", "enseigne_id"],
              "fact_sephora_indicateur": ["indicateur_id"], "fact_sephora_magasin_belgique": ["magasin_be_id"]}
    for fact, g in grains.items():
        check(f"{fact} : grain unique ({' × '.join(g)})", not t[fact].duplicated(g).any())

    r = t["fact_rentabilite"]
    calc = r.marge_brute_eur - r.loyer_eur - r.personnel_eur - r.transport_eur
    check("rentabilité : résultat = marge − loyer − personnel − transport (±1 €)",
          (calc - r.resultat_annuel_eur).abs().max() <= 1)
    mg = t["fact_marge_produit"]
    check("marges : marge = prix NL HT − coût d'achat (±0,01 €)",
          ((mg.prix_sephora_nl_ht - mg.cout_achat_ht_eur) - mg.marge_brute_eur).abs().max() <= 0.011)
    p = t["fact_prix_produit"]
    check("prix : indice de prix renseigné uniquement pour les produits partagés",
          (p.indice_prix_nl_fr_ttc.notna() == (p.bonus_exclusivite_0_100 == 0)).all())
    check("prix : score de désirabilité entre 0 et 100", p.score_desirabilite.dropna().between(0, 100).all())
    mq = t["dim_marque"]
    check("marques : échelle Trends = 100 pour la marque la plus recherchée (hors enseigne)",
          mq.score_trends_marque_0_100.max() == 100)
    v = t["fact_ville"]
    mc = t["fact_magasin_concurrent"]
    cnt = mc[mc.is_ville_cible == 1].groupby("ville_id").size()
    check("villes : nb_douglas_ici = nombre de magasins dans fact_magasin_concurrent",
          (v.set_index("ville_id").nb_douglas_ici == cnt.reindex(v.ville_id).values).all())
    c = t["fact_canal"]
    check("canaux : parts magasins physiques = 100 %", round(c.part_magasins_physiques_pct.sum(), 1) == 100.0)
    check("canaux : parts marché total = 100 %", round(c.part_marche_total_pct.sum(), 1) == 100.0)
    return ok


def main():
    produits, trends, villes = lire("produits_prix"), lire("google_trends_long"), lire("villes_nl")
    magasins, canaux, marche = lire("magasins_concurrents"), lire("parts_de_marche_canaux"), lire("marche_maquillage")
    renta, marges, prix_vente = lire("rentabilite_villes"), lire("marges_nl"), lire("prix_vente_nl")
    ind, mag_be, pays = lire("sephora_indicateurs"), lire("sephora_magasins_belgique"), lire("pays_fiscalite")

    t = {}
    t["dim_marque"] = dim_marque(produits, trends)
    t["dim_produit"] = dim_produit(produits, t["dim_marque"])
    t["dim_ville"] = dim_ville(villes)
    t["dim_scenario"] = dim_scenario()
    t["dim_enseigne"] = ENSEIGNES.copy()
    t["dim_canal"] = dim_canal(canaux)
    t["dim_pays"] = dim_pays(pays)

    t["fact_prix_produit"] = fact_prix_produit(produits, prix_vente, t["dim_marque"])
    t["fact_marge_produit"] = fact_marge_produit(marges, t["dim_scenario"])
    t["fact_recherche_google"] = fact_recherche_google(trends, t["dim_marque"])
    t["fact_ville"] = fact_ville(villes, renta)
    t["fact_magasin_concurrent"] = fact_magasin_concurrent(magasins)
    t["fact_rentabilite"] = fact_rentabilite(renta, t["dim_scenario"])
    t["fact_marche"] = fact_marche(marche)
    t["fact_canal"] = fact_canal(canaux, t["dim_canal"])
    t["fact_sephora_indicateur"] = fact_sephora_indicateur(ind)
    t["fact_sephora_magasin_belgique"] = fact_sephora_magasin_belgique(mag_be)

    dates = set(trends.semaine) | {DATE_RELEVE} | set(mag_be.date_ouverture.dropna())
    for f in ["fact_rentabilite", "fact_marche", "fact_canal", "fact_sephora_indicateur"]:
        dates |= {pd.to_datetime(str(x), format="%Y%m%d").strftime("%Y-%m-%d") for x in t[f].date_id}
    t["dim_date"] = dim_date(dates)

    ordre = [k for k in t if k.startswith("dim_")] + [k for k in t if k.startswith("fact_")]
    GOLD.mkdir(parents=True, exist_ok=True)
    VUES.mkdir(parents=True, exist_ok=True)
    for nom in ordre:
        t[nom].to_csv(GOLD / f"{nom}.csv", index=False)
    v = vues(t)
    v["vue_kpi"] = kpi(t)
    for nom, df in v.items():
        df.to_csv(VUES / f"{nom}.csv", index=False)

    print("--- TABLES ÉCRITES ---")
    for nom in ordre:
        print(f"  data/gold/{nom}.csv : {len(t[nom])} lignes × {len(t[nom].columns)} colonnes")
    for nom, df in v.items():
        print(f"  data/gold/vues/{nom}.csv : {len(df)} lignes × {len(df.columns)} colonnes")
    print("--- KPI ---")
    for _, k in v["vue_kpi"].iterrows():
        print(f"  [{k.axe}] {k.kpi} : {k.valeur} {k.unite}")
    ok = controler(t)
    print("\nRÉSULTAT :", "tous les contrôles sont OK" if ok else "!! au moins un contrôle a échoué")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
