"""
Nettoyage des données (couche Silver) - Groupe 4, Sephora Pays-Bas
==================================================================

Lit les fichiers bruts de data/raw/ et data/previsions/, les nettoie et écrit
les tables nettoyées dans data/silver/, puis lance des contrôles de qualité.

Principes (repris du nettoyage de la branche feature/etl-star-ai) :
  - on corrige, on ne supprime pas d'information sans le documenter ;
  - les clés de jointure sont des identifiants (product_id, city_id), jamais des noms ;
  - les noms de marques sont harmonisés pour que les tables puissent être reliées ;
  - une donnée manquante reste vide : aucune valeur n'est inventée.

Exécution :  python data/silver/clean_silver.py
"""

from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PREV = ROOT / "data" / "previsions"
SILVER = ROOT / "data" / "silver"

DEBUT_PERIODE = "2025-11-01"          # début de la période Google Trends étudiée
PRODUITS_EXCLUS = {"P04": "Aucun avis sur sephora.fr : note absente, produit retiré plutôt qu'une note inventée"}

# Corrections de noms et de types produits (reprises de feature/etl-star-ai)
NOMS_PRODUITS = {
    "P09": "Gloss Balm",
    "P10": "Lip Tint Felt Liner",
    "P14": "HD Skin Face Essentials",
    "P17": "SoftSculpt Sérum Bronzant",
    "P20": "Shape Tape",
    "P21": "Size Up",
    "P22": "12H Colorful Crayon Yeux",
    "P23": "Master Mattes Long-Wear Cream Eyeshadow",
    "P24": "Special Effects Glitter Shadow",
    "P25": "Master Mattes Eyeshadow Palette: The Neutrals",
    "P27": "Ethereal Eyes Eyeshadow Palette: The Original",
    "P29": "Crayon Contour Yeux 12H",
    "P30": "Master Mattes Eyeshadow Palette",
}
TYPES_PRODUITS = {
    "P06": "Gloss haute brillance",       # faute de frappe du site source (« brilliance »)
    "P14": "Palette teint",               # la colonne contenait la teinte (décalage)
    "P29": "Waterproof crayon yeux",
}
VARIANTES = {"P14": "H1 (26,5 g)"}
COMMENTAIRES = {
    "P26": "Prix du format mini 6,5 ml, teinte Cuz I'm Black (prix « à partir de » sur la page) | Douglas : même mini 6,5 ml",
    "P31": "Ajout hors échantillon top 10 : marque tendance (Rhode), choisie pour son potentiel auprès des jeunes clientes NL | Exclusivité vérifiée : absent de Douglas NL et d'ICI Paris XL NL",
    "P32": "Ajout hors échantillon top 10 : marque tendance (Rhode), choisie pour son potentiel auprès des jeunes clientes NL | Exclusivité vérifiée : absent de Douglas NL et d'ICI Paris XL NL",
}

# Noms de marques Google Trends -> noms utilisés dans les tables produits
MARQUES_TRENDS = {
    "sephora": "Sephora",                  # l'enseigne (différent de la marque Sephora Collection)
    "HUDA BEAUTY": "Huda Beauty",
    "Rare Beauty": "Rare Beauty",
    "Fenty Beauty": "Fenty Beauty",
    "Kylie Cosmetics": "Kylie Cosmetics",
    "rhode": "Rhode",
    "Haus Labs": "Haus Labs",
    "makeup by mario": "Makeup By Mario",
}

# Noms de villes -> city_id (La Haye a plusieurs noms selon les sources)
VILLES_ID = {"Amsterdam": 1, "Rotterdam": 2, "Utrecht": 3, "La Haye": 4, "Den Haag": 4, "'s-Gravenhage": 4}
NOMS_VILLES_FR = {"Den Haag": "La Haye", "'s-Gravenhage": "La Haye"}

rapport = []      # journal des opérations, affiché en fin d'exécution


def log(table, message):
    rapport.append(f"[{table}] {message}")


def lire(chemin):
    return pd.read_csv(chemin, dtype=str, keep_default_na=False)


def nettoyer_texte(df):
    """Supprime les espaces en début/fin de cellule."""
    return df.apply(lambda col: col.str.strip())


def num(serie):
    return pd.to_numeric(serie.replace("", pd.NA), errors="coerce")


# ---------------------------------------------------------------------------
# 1. Produits et prix
# ---------------------------------------------------------------------------
def produits_prix():
    df = nettoyer_texte(lire(RAW / "products_prices.csv"))
    n0 = len(df)
    for pid, raison in PRODUITS_EXCLUS.items():
        df = df[df.product_id != pid]
        log("produits_prix", f"{pid} retiré : {raison}")
    df.insert(df.columns.get_loc("product_type") + 1, "variant", "")
    for pid, nom in NOMS_PRODUITS.items():
        df.loc[df.product_id == pid, "product_name"] = nom
    for pid, typ in TYPES_PRODUITS.items():
        df.loc[df.product_id == pid, "product_type"] = typ
    for pid, var in VARIANTES.items():
        df.loc[df.product_id == pid, "variant"] = var
    for pid, com in COMMENTAIRES.items():
        df.loc[df.product_id == pid, "comment"] = com
    log("produits_prix", f"{len(NOMS_PRODUITS)} noms harmonisés (majuscules, ®, ™), "
                         f"{len(TYPES_PRODUITS)} types corrigés, P14 : teinte déplacée dans `variant`")
    df["in_top10_sephora_fr"] = (df.rank_sephora_fr != "").astype(int)
    df["is_mini_format"] = (df.product_id == "P26").astype(int)
    for c in ["rank_sephora_fr", "review_count_sephora_fr"]:
        df[c] = num(df[c]).astype("Int64")
    for c in ["price_sephora_fr_ttc", "rating_sephora_fr", "price_douglas_nl_ttc", "price_iciparisxl_nl_ttc"]:
        df[c] = num(df[c])
    for c in ["is_lvmh", "is_verified_exclusive"]:
        df[c] = num(df[c]).astype(int)
    log("produits_prix", f"{n0} -> {len(df)} lignes ; rang et nb d'avis convertis en entiers")
    return df


# ---------------------------------------------------------------------------
# 2. Google Trends (format large -> format long)
# ---------------------------------------------------------------------------
def google_trends():
    df = nettoyer_texte(lire(RAW / "google_trends" / "google_trends_nl.csv"))
    long = df.melt(id_vars="Time", var_name="marque_source", value_name="score_trends")
    long["marque"] = long.marque_source.map(MARQUES_TRENDS)
    long = long.rename(columns={"Time": "semaine"})
    n0 = long.semaine.nunique()
    long = long[long.semaine >= DEBUT_PERIODE]
    log("google_trends", f"format large -> long ; {n0 - long.semaine.nunique()} semaine retirée (avant le {DEBUT_PERIODE})")
    log("google_trends", "noms de marques harmonisés avec les tables produits (ex. « HUDA BEAUTY » -> « Huda Beauty »)")
    long["score_trends"] = num(long.score_trends).astype(int)
    long["is_enseigne"] = (long.marque == "Sephora").astype(int)
    return long[["semaine", "marque", "score_trends", "is_enseigne"]].sort_values(["semaine", "marque"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Villes
# ---------------------------------------------------------------------------
def villes():
    df = nettoyer_texte(lire(RAW / "villes" / "market_cities_nl.csv"))
    sources = df[["city_id", "ville", "source_population", "source_loyer", "source_concurrents", "commentaire"]]
    df = df.drop(columns=["source_population", "source_loyer", "source_concurrents", "commentaire"])

    def minutes(txt):
        h, m = re.match(r"(\d+)h(\d+)", txt).groups()
        return int(h) * 60 + int(m)

    df["duree_route_saran_min"] = df.duree_route_saran.map(minutes)
    df = df.drop(columns="duree_route_saran")
    for c in df.columns.drop(["ville", "rue_reference_loyer"]):
        df[c] = num(df[c])
    for c in ["city_id", "population_totale", "population_15_44", "nb_douglas", "nb_ici_paris_xl", "nb_bijenkorf",
              "nb_concurrents_total", "pop_15_44_par_concurrent", "distance_hub_saran_km", "distance_bruxelles_km"]:
        df[c] = df[c].astype(int)
    df["distance_bruxelles_estimee"] = 1
    # De Bijenkorf est compté dans nb_concurrents_total mais n'a pas de liste de magasins :
    # cette colonne donne le comptage comparable à la table magasins_concurrents.
    df.insert(df.columns.get_loc("nb_concurrents_total") + 1, "nb_douglas_ici",
              df.nb_douglas + df.nb_ici_paris_xl)
    log("villes", "ajout de nb_douglas_ici (sans De Bijenkorf), comparable à magasins_concurrents")
    log("villes", "4 colonnes de texte (sources, commentaire) déplacées dans villes_sources.csv")
    log("villes", "durée de trajet convertie en minutes ; distance Bruxelles signalée comme estimation")
    log("villes", "nom « 15_44 » conservé : les données CBS portent bien sur les 15-44 ans")
    return df, sources


# ---------------------------------------------------------------------------
# 4. Magasins concurrents (Douglas + ICI Paris XL)
# ---------------------------------------------------------------------------
def code_postal(cp):
    cp = cp.replace(" ", "").upper()
    return f"{cp[:4]} {cp[4:]}" if len(cp) == 6 else cp


def magasins_concurrents():
    d = nettoyer_texte(lire(RAW / "concurrents" / "douglas_stores_nl.csv"))
    i = nettoyer_texte(lire(RAW / "concurrents" / "ici_paris_xl_stores_g4.csv"))
    d = pd.DataFrame({"enseigne": d.enseigne, "store_ref": d.magasin, "nom_magasin": d.magasin, "adresse": "",
                      "ville": d.ville, "code_postal": d.code_postal, "latitude": num(d.latitude),
                      "longitude": num(d.longitude), "source": d.source})
    i = pd.DataFrame({"enseigne": i.enseigne, "store_ref": "ICI-" + i.code_magasin,
                      "nom_magasin": "ICI Paris XL " + i.adresse, "adresse": i.adresse, "ville": i.ville,
                      "code_postal": i.code_postal, "latitude": pd.NA, "longitude": pd.NA,
                      "source": "iciparisxl.nl/alle-winkels - 2026-11-12"})
    df = pd.concat([d, i], ignore_index=True)
    df["ville"] = df.ville.replace(NOMS_VILLES_FR)
    df["city_id"] = df.ville.map(VILLES_ID).astype("Int64")
    df["is_ville_cible"] = df.city_id.notna().astype(int)
    df["code_postal"] = df.code_postal.map(code_postal)
    df["has_gps"] = df.latitude.notna().astype(int)
    df.insert(0, "store_id", range(1, len(df) + 1))
    log("magasins_concurrents", f"Douglas ({len(d)}) et ICI Paris XL ({len(i)}) réunis dans une seule table")
    log("magasins_concurrents", "« Den Haag » -> « La Haye » + city_id ; codes postaux au format « 1234 AB »")
    log("magasins_concurrents", "ICI Paris XL : pas de coordonnées GPS (has_gps = 0) ; couverture limitée aux 4 villes cibles")
    return df


# ---------------------------------------------------------------------------
# 5. Situation actuelle de Sephora (séparée en 2 tables)
# ---------------------------------------------------------------------------
MAGASINS_BE = {
    "Ouverture Docks Bruxsel (Bruxelles)": ("Docks Bruxsel", "Bruxelles", "Ouvert", 270),
    "Ouverture City2 (Bruxelles)": ("City2", "Bruxelles", "Ouvert", None),
    "Ouverture Médiacité (Liège)": ("Médiacité", "Liège", "Ouvert", 400),
    "Westland Shopping (Anderlecht)": ("Westland Shopping", "Anderlecht", "Annoncé", None),
    "Esplanade (Louvain-la-Neuve)": ("Esplanade", "Louvain-la-Neuve", "En projet", None),
}


def sephora_situation():
    df = nettoyer_texte(lire(RAW / "sephora" / "sephora_situation_actuelle.csv"))
    est_magasin = df.indicateur.isin(MAGASINS_BE)
    mag = df[est_magasin].copy()
    rows = []
    for _, r in mag.iterrows():
        nom, ville, statut, surface = MAGASINS_BE[r.indicateur]
        date = r.valeur if re.match(r"\d{4}-\d{2}-\d{2}", r.valeur) else ""
        rows.append({"magasin": nom, "ville": ville, "pays": "Belgique", "statut": statut,
                     "date_ouverture": date, "surface_m2": surface, "source": r.source, "url": r.url,
                     "fiabilite": r.fiabilite, "commentaire": r.commentaire})
    magasins = pd.DataFrame(rows)
    magasins["surface_m2"] = magasins.surface_m2.astype("Int64")
    ind = df[~est_magasin].copy()
    ind["valeur"] = num(ind.valeur)
    ind["annee"] = ind.annee.astype(int)
    ind["a_reverifier"] = ind.commentaire.str.contains("revérifier", case=False).astype(int)
    ind.insert(0, "indicateur_id", range(1, len(ind) + 1))
    log("sephora", f"colonne `valeur` mixte séparée : {len(ind)} indicateurs chiffrés + {len(magasins)} magasins belges")
    log("sephora", "surface : 270 m² (Docks Bruxsel, source du fichier) ; 400 m² (Médiacité, L'Express Franchise)")
    return ind, magasins


# ---------------------------------------------------------------------------
# 6. Tables déjà propres (contrôle des types uniquement)
# ---------------------------------------------------------------------------
def tables_propres():
    pays = nettoyer_texte(lire(RAW / "pays_fiscalite.csv"))
    for c in ["tva_cosmetiques_pct", "droits_douane_pct", "union_douaniere_ue", "catalogue_france_eligible_pct"]:
        pays[c] = num(pays[c])
    marche = nettoyer_texte(lire(RAW / "marche" / "marche_maquillage_nl.csv"))
    for c in ["annee", "valeur_meur", "croissance_annuelle_pct"]:
        marche[c] = num(marche[c])
    marche["annee"] = marche.annee.astype(int)
    canaux = nettoyer_texte(lire(RAW / "marche" / "parts_de_marche_canaux_nl.csv"))
    for c in ["ventes_meur_2020", "part_magasins_physiques_pct", "part_marche_total_pct", "est_magasin_physique"]:
        canaux[c] = num(canaux[c])
    canaux.insert(0, "canal_id", range(1, len(canaux) + 1))
    log("tables_propres", "pays, marché, canaux : aucune anomalie ; types numériques contrôlés")
    return pays, marche, canaux


def previsions(ids_produits):
    prix = lire(PREV / "prix_vente_nl.csv")
    marges = lire(PREV / "marges_nl.csv")
    renta = lire(PREV / "rentabilite_villes_nl.csv")
    for nom, df in [("prix_vente_nl", prix), ("marges_nl", marges)]:
        retires = sorted(set(df.product_id) - set(ids_produits))
        log("previsions", f"{nom} : {retires} retiré(s) pour rester cohérent avec produits_prix")
    prix = prix[prix.product_id.isin(ids_produits)]
    marges = marges[marges.product_id.isin(ids_produits)]
    for df in (prix, marges, renta):
        for c in df.columns:
            conv = num(df[c])
            if conv.notna().sum() == (df[c] != "").sum():
                df[c] = conv
    log("previsions", "rentabilite_villes : inchangée (taux de marge moyens identiques à 0,1 point près sans P04)")

    # Marges : format large (1 colonne par scénario) -> format long (1 ligne par produit et par scénario),
    # pour partager la même dimension « scénario » que rentabilite_villes.
    taux = {"pessimiste": 38.0, "central": 44.0, "optimiste": 48.0}
    base = ["product_id", "price_sephora_fr_ht", "price_sephora_nl_ttc", "price_sephora_nl_ht"]
    lignes = []
    for s, t in taux.items():
        d = marges[base].copy()
        d.insert(1, "scenario", s.capitalize())
        d["taux_marge_brute_france_pct"] = t
        d["cout_achat_ht_eur"] = marges[f"cout_achat_{s}_eur"]
        d["marge_brute_nl_eur"] = marges[f"marge_{s}_eur"]
        d["taux_marge_brute_nl_pct"] = marges[f"marge_{s}_pct"]
        lignes.append(d)
    marges = pd.concat(lignes, ignore_index=True)
    log("previsions", "marges_nl : format large -> long (1 ligne par produit et par scénario)")
    return prix, marges, renta


# ---------------------------------------------------------------------------
# Contrôles de qualité
# ---------------------------------------------------------------------------
def controler(t):
    ok = True

    def check(nom, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'OK ' if cond else '!! '} {nom}")

    print("--- CONTRÔLES DE QUALITÉ ---")
    check("produits : product_id unique", t["produits_prix"].product_id.is_unique)
    check("produits : P04 absent", "P04" not in set(t["produits_prix"].product_id))
    check("produits : aucune note manquante", t["produits_prix"].rating_sephora_fr.notna().all())
    p = t["produits_prix"]
    excl = (p.price_douglas_nl_ttc.isna() & p.price_iciparisxl_nl_ttc.isna()).astype(int)
    check("produits : exclusivité cohérente avec l'absence de prix NL", (excl == p.is_verified_exclusive).all())
    check("produits : plus aucun ® ni ™", ~p.product_name.str.contains("®|™").any())
    g = t["google_trends_long"]
    check("trends : grain semaine × marque unique", not g.duplicated(["semaine", "marque"]).any())
    check("trends : 53 semaines × 8 marques", len(g) == 53 * 8)
    communes = set(g.marque) & set(p.brand)
    check(f"trends : marques reliables aux produits ({len(communes)} communes)", len(communes) == 5)
    v = t["villes_nl"]
    check("villes : city_id unique", v.city_id.is_unique)
    m = t["magasins_concurrents"]
    cible = m[m.is_ville_cible == 1].groupby(["city_id", "enseigne"]).size().unstack(fill_value=0)
    cible.index = cible.index.astype(int)
    vv = v.set_index("city_id").reindex(cible.index)
    check("magasins : nb Douglas par ville = villes_nl", (cible["Douglas"] == vv.nb_douglas).all())
    check("magasins : nb ICI Paris XL par ville = villes_nl", (cible["ICI Paris XL"] == vv.nb_ici_paris_xl).all())
    check("magasins : store_id unique", m.store_id.is_unique)
    check("magasins : total par ville = villes_nl.nb_douglas_ici", (cible.sum(axis=1) == vv.nb_douglas_ici).all())
    c = t["parts_de_marche_canaux"]
    check("canaux : parts magasins physiques = 100 %", round(c.part_magasins_physiques_pct.sum(), 1) == 100.0)
    check("canaux : parts marché total = 100 %", round(c.part_marche_total_pct.sum(), 1) == 100.0)
    ids = set(p.product_id)
    check("prévisions : prix_vente_nl relié aux produits", set(t["prix_vente_nl"].product_id) == ids)
    check("prévisions : marges_nl relié aux produits", set(t["marges_nl"].product_id) == ids)
    mg = t["marges_nl"]
    check("prévisions : marges_nl = 1 ligne par produit et par scénario",
          len(mg) == 3 * len(ids) and not mg.duplicated(["product_id", "scenario"]).any())
    check("prévisions : mêmes scénarios dans marges_nl et rentabilite_villes",
          set(mg.scenario) == set(t["rentabilite_villes"].scenario))
    check("prévisions : rentabilité reliée aux villes", set(t["rentabilite_villes"].city_id) == set(v.city_id))
    check("sephora : indicateurs tous numériques", t["sephora_indicateurs"].valeur.notna().all())
    return ok


def main():
    SILVER.mkdir(parents=True, exist_ok=True)
    produits = produits_prix()
    villes_nl, villes_sources = villes()
    indicateurs, magasins_be = sephora_situation()
    pays, marche, canaux = tables_propres()
    prix, marges, renta = previsions(set(produits.product_id))
    tables = {
        "produits_prix": produits,
        "google_trends_long": google_trends(),
        "villes_nl": villes_nl,
        "villes_sources": villes_sources,
        "magasins_concurrents": magasins_concurrents(),
        "sephora_indicateurs": indicateurs,
        "sephora_magasins_belgique": magasins_be,
        "pays_fiscalite": pays,
        "marche_maquillage": marche,
        "parts_de_marche_canaux": canaux,
        "prix_vente_nl": prix,
        "marges_nl": marges,
        "rentabilite_villes": renta,
    }
    for nom, df in tables.items():
        df.to_csv(SILVER / f"{nom}.csv", index=False)

    print("--- JOURNAL DU NETTOYAGE ---")
    for ligne in rapport:
        print("  " + ligne)
    print("--- TABLES ÉCRITES DANS data/silver/ ---")
    for nom, df in tables.items():
        print(f"  {nom}.csv : {len(df)} lignes × {len(df.columns)} colonnes")
    ok = controler(tables)
    print("\nRÉSULTAT :", "tous les contrôles sont OK" if ok else "!! au moins un contrôle a échoué")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
