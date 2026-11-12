"""Classe les best-sellers sephora.fr en Teint / Yeux / Levres et garde les 10 premiers de chaque.
Regles :
- on exclut pinceaux, accessoires, sourcils, ongles, soins des cils, produits multi-zones ambigus ;
- on exclut les doublons de format (mini, format voyage, recharge, duo/set) pour garder 1 ligne par produit ;
- l'ordre = le rang dans le classement 'Meilleures ventes' de sephora.fr.
Usage : python select_top30.py bestsellers_maquillage.csv products_prices.csv
"""
import re, sys, pandas as pd

src, dst = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, dtype=str)
txt = (df.product_name.fillna("") + " " + df.product_type.fillna("")).str.lower()

EXCLURE = [r"\bpinceau", r"\bbrush\b", r"houppette", r"\bcolle\b", r"sourcil", r"\bbrow\b",
           r"soin des cils", r"serum pour cils", r"lash enhancing", r"kit pro", r"multi-usage, fini",
           r"eye & cheek", r"\bmini\b", r"format voyage", r"refill", r"recharge", r"\bduo\b",
           r"\bset\b", r"baby bake"]
LEVRES = ["lèvre", "lip", "gloss", "rouge à lèvres", "lacquer"]
YEUX = ["mascara", "yeux", "paupière", "eyeliner", "eyeshadow", "eye tint", "liner feutre"]

def categorie(t):
    if any(re.search(k, t) for k in EXCLURE):
        return "Exclu"
    if any(k in t for k in LEVRES):
        return "Lèvres"
    if any(k in t for k in YEUX):
        return "Yeux"
    return "Teint"

df["subcategory"] = txt.apply(categorie)
df.to_csv("bestsellers_maquillage_classes.csv", index=False)

LVMH = {"Sephora Collection", "Dior", "Dior Backstage", "Benefit Cosmetics", "Fenty Beauty",
        "Make Up For Ever", "Guerlain"}
top = (df[df.subcategory != "Exclu"].assign(r=lambda d: d.rank_sephora_fr.astype(int))
       .sort_values("r").groupby("subcategory").head(10)
       .sort_values(["subcategory", "r"]))
out = pd.DataFrame({
    "product_id": [f"P{i:02d}" for i in range(1, len(top) + 1)],
    "product_name": top.product_name.values,
    "brand": top.brand.values,
    "subcategory": top.subcategory.values,
    "product_type": top.product_type.values,
    "rank_sephora_fr": top.rank_sephora_fr.values,
    "is_lvmh": top.brand.isin(LVMH).astype(int).values,
    "price_sephora_fr_ttc": top.price_sephora_fr_ttc.values,
    "rating_sephora_fr": "",
    "review_count_sephora_fr": top.review_count_sephora_fr.values,
    "price_douglas_nl_ttc": "", "price_iciparisxl_nl_ttc": "", "is_verified_exclusive": "",
    "collected_at": top.collected_at.values, "comment": "",
})
out.to_csv(dst, index=False)
print(out[["product_id","subcategory","rank_sephora_fr","brand","product_name","price_sephora_fr_ttc","review_count_sephora_fr","is_lvmh"]].to_string(index=False))
print("\nPar categorie :", out.subcategory.value_counts().to_dict())
