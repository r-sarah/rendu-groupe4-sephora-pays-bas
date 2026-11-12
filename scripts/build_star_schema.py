"""
Construction du modele en etoile (couche Gold) - Groupe 4, Sephora Pays-Bas
==========================================================================

Sources : les 3 tables nettoyees de la branche
  1. data/raw/google_trends/google_trends_nl.csv   (424 lignes, marque x semaine)
  2. data/raw/villes/market_cities_nl.csv          (4 villes)
  3. data/raw/concurrents/products_prices.csv      (31 references)

Modele : UNE etoile, 4 dimensions partagees, 3 tables de faits (un grain par
table, jamais de produit x ville).

  Dim_Brand         1 marque          Dim_Product   1 reference produit
  Dim_City_NL       1 ville           Dim_Date      1 date

  Fact_Product_Pricing     1 produit          (31)
  Fact_Search_Interest     1 marque x semaine (424)
  Fact_City_Expansion      1 ville            (4)

Execution :  python scripts/build_star_schema.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SILVER = ROOT / "data" / "raw"
GOLD = ROOT / "data" / "gold"

DATE_RELEVE = "2026-11-12"
DATE_DEBUT = "2025-11-01"

# Regroupement des marques, dans l'esprit de la problematique du projet.
BRAND_GROUP = {
    "Sephora": "Sephora (enseigne etudiee)",
    "Sephora Collection": "Sephora (maison)",
    "Fenty Beauty": "LVMH",
    "Benefit Cosmetics": "LVMH",
    "Make Up For Ever": "LVMH",
    "Rhode": "Marque tendance",
    "Rare Beauty": "Marque tendance",
    "Huda Beauty": "Marque tendance",
    "Makeup By Mario": "Marque tendance",
    "Haus Labs": "Marque tendance",
    "Kylie Cosmetics": "Marque tendance",
}
BRAND_GROUP_DEFAUT = "Concurrent"


def _lire(nom, sous_dossier=""):
    chemin = SILVER / sous_dossier / nom if sous_dossier else SILVER / nom
    return pd.read_csv(chemin, dtype=str, keep_default_na=False)


def _num(s):
    s = str(s).strip()
    return None if s == "" else float(s)


def _ent(s):
    s = str(s).strip()
    return None if s == "" else int(s)


# ===========================================================================
# Dimensions
# ===========================================================================
def dim_brand(gt, pp):
    """Une ligne par marque : union des marques suivies sur Google Trends et
    des marques produits. Le score Trends est recalcule depuis la table long."""
    g = gt.copy()
    g["score_trends"] = g["score_trends"].astype(int)
    moyennes = g.groupby("marque")["score_trends"].mean()
    max_moy = moyennes.max()
    marques = sorted(set(moyennes.index) | set(pp["brand"]))

    lignes = []
    for i, marque in enumerate(marques, start=1):
        lvmh = pp[pp["brand"] == marque]["is_lvmh"]
        if marque in moyennes.index:
            moy = round(float(moyennes[marque]), 2)
            score = round(float(moyennes[marque] / max_moy * 100), 1)
        else:
            moy, score = None, None
        lignes.append({
            "brand_key": i,
            "brand": marque,
            "brand_group": BRAND_GROUP.get(marque, BRAND_GROUP_DEFAUT),
            "is_lvmh": int(lvmh.iloc[0]) if len(lvmh) else None,
            "in_google_trends": 1 if marque in moyennes.index else 0,
            "in_products_prices": 1 if marque in set(pp["brand"]) else 0,
            "moyenne_12m": moy,
            "score_trends_0_100": score,
        })
    return pd.DataFrame(lignes)


def dim_product(pp, brands):
    ref = brands.set_index("brand")["brand_key"].to_dict()
    lignes = []
    for _, r in pp.iterrows():
        lignes.append({
            "product_key": 0,
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "brand": r["brand"],
            "brand_key": ref[r["brand"]],
            "subcategory": r["subcategory"],
            "product_type": r["product_type"],
            "variant": r["variant"],
            "is_verified_exclusive": int(r["is_verified_exclusive"]),
            "is_lvmh": int(r["is_lvmh"]),
        })
    df = pd.DataFrame(lignes).sort_values(["brand", "product_name"]).reset_index(drop=True)
    df["product_key"] = range(1, len(df) + 1)
    return df


def dim_city_nl(mc):
    lignes = []
    for i, (_, r) in enumerate(mc.iterrows(), start=1):
        lignes.append({
            "city_key": i,
            "city_id": int(r["city_id"]),
            "ville": r["ville"],
            "population_totale": _ent(r["population_totale"]),
            "population_15_45": _ent(r["population_15_45"]),
            "part_15_45_pct": _num(r["part_15_45_pct"]),
            "loyer_prime_m2_an_eur": _num(r["loyer_prime_m2_an_eur"]),
            "rue_reference_loyer": r["rue_reference_loyer"],
            "distance_hub_saran_km": _ent(r["distance_hub_saran_km"]),
            "duree_route_saran": r["duree_route_saran"],
            "distance_bruxelles_km": _ent(r["distance_bruxelles_km"]),
        })
    return pd.DataFrame(lignes)


def dim_date(dates):
    d = pd.to_datetime(pd.Series(sorted(set(dates))))
    return pd.DataFrame({
        "date_key": d.dt.strftime("%Y%m%d").astype(int),
        "date": d.dt.strftime("%Y-%m-%d"),
        "annee": d.dt.year,
        "trimestre": d.dt.quarter,
        "mois": d.dt.month,
        "semaine_iso": d.dt.isocalendar().week.astype(int),
        "jour": d.dt.day,
    }).reset_index(drop=True)


# ===========================================================================
# Tables de faits
# ===========================================================================
def fact_product_pricing(pp, products, brands):
    pkey = products.set_index("product_id")["product_key"].to_dict()
    bkey = brands.set_index("brand")["brand_key"].to_dict()
    tscore = brands.set_index("brand")["score_trends_0_100"].to_dict()

    lignes = []
    for _, r in pp.iterrows():
        prix_fr = _num(r["price_sephora_fr_ttc"])
        prix_nl = [v for v in (_num(r["price_douglas_nl_ttc"]),
                               _num(r["price_iciparisxl_nl_ttc"])) if v is not None]
        prix_nl_min = min(prix_nl) if prix_nl else None
        note = _num(r["rating_sephora_fr"])
        st = tscore[r["brand"]]

        score_avis = round(note / 5 * 100, 1) if note is not None else None
        bonus_exclu = 100 if int(r["is_verified_exclusive"]) == 1 else 0

        # Score de desirabilite : 0,40 Trends + 0,35 avis + 0,25 exclusivite
        if st is not None and score_avis is not None:
            desirabilite = round(0.40 * st + 0.35 * score_avis + 0.25 * bonus_exclu, 1)
        else:
            desirabilite = None

        # indice prix relatif NL / FR (base 100 = parite France)
        indice = round(prix_nl_min / prix_fr * 100, 1) if (prix_nl_min and prix_fr) else None
        # ecart de prix HT FR vs NL (TVA 20 % FR / 21 % NL) : ingredient factuel du
        # calcul de marge, qui reste a completing avec l'hypothese de cout de revient
        ecart = round(prix_nl_min / 1.21 - prix_fr / 1.20, 2) if (prix_nl_min and prix_fr) else None

        lignes.append({
            "fact_key": 0,
            "product_key": pkey[r["product_id"]],
            "brand_key": bkey[r["brand"]],
            "date_key": int(DATE_RELEVE.replace("-", "")),
            "rank_sephora_fr": _ent(r["rank_sephora_fr"]),
            "price_sephora_fr_ttc": prix_fr,
            "price_douglas_nl_ttc": _num(r["price_douglas_nl_ttc"]),
            "price_iciparisxl_nl_ttc": _num(r["price_iciparisxl_nl_ttc"]),
            "price_competitor_nl_ttc": prix_nl_min,
            "rating_sephora_fr": note,
            "review_count_sephora_fr": _ent(r["review_count_sephora_fr"]),
            "score_trends_0_100": st,
            "score_avis_0_100": score_avis,
            "bonus_exclusivite_0_100": bonus_exclu,
            "desirability_score": desirabilite,
            "relative_price_index": indice,
            "ecart_prix_ht_eur": ecart,
            "marge_brute_post_vat_21_eur": None,
        })
    df = pd.DataFrame(lignes)
    df["fact_key"] = range(1, len(df) + 1)
    return df


def fact_search_interest(gt, brands):
    bkey = brands.set_index("brand")["brand_key"].to_dict()
    lignes = []
    for _, r in gt.iterrows():
        lignes.append({
            "fact_key": 0,
            "brand_key": bkey[r["marque"]],
            "date_key": int(r["semaine"].replace("-", "")),
            "score_trends": _ent(r["score_trends"]),
            "is_peak": 1 if r["semaine"] == "2026-08-30" else 0,
        })
    df = pd.DataFrame(lignes)
    df["fact_key"] = range(1, len(df) + 1)
    return df


def fact_city_expansion(mc, cities):
    ckey = cities.set_index("city_id")["city_key"].to_dict()
    lignes = []
    for _, r in mc.iterrows():
        lignes.append({
            "fact_key": 0,
            "city_key": ckey[int(r["city_id"])],
            "date_key": int(DATE_RELEVE.replace("-", "")),
            "nb_douglas": _ent(r["nb_douglas"]),
            "nb_ici_paris_xl": _ent(r["nb_ici_paris_xl"]),
            "nb_bijenkorf": _ent(r["nb_bijenkorf"]),
            "nb_concurrents_total": _ent(r["nb_concurrents_total"]),
            "concurrents_pour_100k_hab": _num(r["concurrents_pour_100k_hab"]),
            "pop_15_45_par_concurrent": _ent(r["pop_15_45_par_concurrent"]),
            "part_15_45_pct": _num(r["part_15_45_pct"]),
            "distance_hub_saran_km": _ent(r["distance_hub_saran_km"]),
            "market_size_nl_eur": None,
            "logistics_cost_eur": None,
            "net_profit_projection_eur": None,
        })
    df = pd.DataFrame(lignes)
    df["fact_key"] = range(1, len(df) + 1)
    return df


# ===========================================================================
# Orchestration + controles
# ===========================================================================
def controler(dims, facts):
    print("--- CONTROLES DE COHERENCE ---")
    for nom, dim, cle in [("Dim_Brand", dims["dim_brand"], "brand_key"),
                          ("Dim_Product", dims["dim_product"], "product_key"),
                          ("Dim_City_NL", dims["dim_city_nl"], "city_key"),
                          ("Dim_Date", dims["dim_date"], "date_key")]:
        d = int(dim[cle].duplicated().sum())
        print(f"  {nom:16s} {len(dim):4d} lignes | PK unique : {'OK' if d == 0 else '!! DOUBLONS'}")

    for nom, fact, fk, dim, dk, dn in [
        ("Fact_Product_Pricing", facts["fact_product_pricing"], "product_key", dims["dim_product"], "product_key", "Dim_Product"),
        ("Fact_Product_Pricing", facts["fact_product_pricing"], "brand_key", dims["dim_brand"], "brand_key", "Dim_Brand"),
        ("Fact_Product_Pricing", facts["fact_product_pricing"], "date_key", dims["dim_date"], "date_key", "Dim_Date"),
        ("Fact_Search_Interest", facts["fact_search_interest"], "brand_key", dims["dim_brand"], "brand_key", "Dim_Brand"),
        ("Fact_Search_Interest", facts["fact_search_interest"], "date_key", dims["dim_date"], "date_key", "Dim_Date"),
        ("Fact_City_Expansion", facts["fact_city_expansion"], "city_key", dims["dim_city_nl"], "city_key", "Dim_City_NL"),
        ("Fact_City_Expansion", facts["fact_city_expansion"], "date_key", dims["dim_date"], "date_key", "Dim_Date"),
    ]:
        orphelins = set(fact[fk].dropna().unique()) - set(dim[dk].unique())
        print(f"  {nom:22s}.{fk:12s} -> {dn:14s} : {'OK' if not orphelins else '!! ORPHELINS ' + str(orphelins)}")

    for nom, fact, g in [
        ("Fact_Product_Pricing", facts["fact_product_pricing"], ["product_key"]),
        ("Fact_Search_Interest", facts["fact_search_interest"], ["brand_key", "date_key"]),
        ("Fact_City_Expansion", facts["fact_city_expansion"], ["city_key"]),
    ]:
        d = int(fact.duplicated(subset=g).sum())
        print(f"  grain {nom:22s} {'+'.join(g):24s} : {'OK' if d == 0 else '!! ' + str(d) + ' DOUBLONS'}")

    print(f"  Fact_Product_Pricing sans city_key (pas de cartesian) : "
          f"{'OK' if 'city_key' not in facts['fact_product_pricing'].columns else '!!'}")

    # le score Trends doit etre identique a celui de la dimension marque
    f = facts["fact_product_pricing"].merge(dims["dim_brand"][["brand_key", "score_trends_0_100"]],
                                             on="brand_key", suffixes=("", "_dim"))
    ecart = (f["score_trends_0_100"].fillna(-1) != f["score_trends_0_100_dim"].fillna(-1)).sum()
    print(f"  score Trends coherent avec Dim_Brand : {'OK' if ecart == 0 else '!! ' + str(ecart)}")


def main():
    GOLD.mkdir(parents=True, exist_ok=True)

    gt = _lire("google_trends_nl.csv", "google_trends")
    mc = _lire("market_cities_nl.csv", "villes")
    pp = _lire("products_prices.csv", "concurrents")

    dims = {
        "dim_brand": dim_brand(gt, pp),
        "dim_city_nl": dim_city_nl(mc),
    }
    dims["dim_product"] = dim_product(pp, dims["dim_brand"])
    dims["dim_date"] = dim_date(set(gt["semaine"]) | {DATE_RELEVE})

    facts = {
        "fact_product_pricing": fact_product_pricing(pp, dims["dim_product"], dims["dim_brand"]),
        "fact_search_interest": fact_search_interest(gt, dims["dim_brand"]),
        "fact_city_expansion": fact_city_expansion(mc, dims["dim_city_nl"]),
    }

    for nom, df in list(dims.items()) + list(facts.items()):
        df.to_csv(GOLD / f"{nom}.csv", index=False)

    controler(dims, facts)

    print("\n--- VOLUMES ---")
    for nom, df in list(dims.items()) + list(facts.items()):
        print(f"  data/gold/{nom}.csv : {len(df)} lignes x {len(df.columns)} colonnes")

    f = facts["fact_product_pricing"]
    p = dims["dim_product"][["product_key", "product_name", "brand"]]
    m = f.merge(p, on="product_key").merge(dims["dim_brand"][["brand_key", "brand_group"]], on="brand_key")
    print("\n--- TOP 10 SCORE DE DESIRABILITE ---")
    top = m.dropna(subset=["desirability_score"]).nlargest(10, "desirability_score")
    print(top[["product_name", "brand", "brand_group", "desirability_score", "score_trends_0_100",
               "score_avis_0_100", "bonus_exclusivite_0_100", "price_sephora_fr_ttc",
               "price_competitor_nl_ttc", "relative_price_index"]].to_string(index=False))
    print(f"  references sans score de desirabilite : {int(f['desirability_score'].isna().sum())} / {len(f)}")
    print("\n--- SCORE MOYEN PAR GROUPE DE MARQUE ---")
    print(m.groupby("brand_group").agg(
        nb_ref=("product_key", "size"),
        score_moy=("desirability_score", "mean"),
        prix_moy=("price_sephora_fr_ttc", "mean"),
        indice_prix_moy=("relative_price_index", "mean"),
    ).round(1).to_string())
    print("\n--- VILLES ---")
    c = facts["fact_city_expansion"].merge(dims["dim_city_nl"][["city_key", "ville"]], on="city_key")
    print(c[["ville", "nb_concurrents_total", "concurrents_pour_100k_hab",
              "pop_15_45_par_concurrent", "distance_hub_saran_km"]].to_string(index=False))
    print("\nModele genere ->", GOLD.relative_to(ROOT))


if __name__ == "__main__":
    main()
