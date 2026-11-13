"""Étape 3 : complète products_prices.csv avec les valeurs relevées à la main.

IMPORTANT (à documenter) : ce script n'a pas été exécuté tel quel pendant la collecte.
Il regroupe, dans l'ordre, les petites commandes pandas lancées une à une
le 12/11/2026 pour remplir le fichier. Les VALEURS ci-dessous ont été relevées
manuellement (voir le README) : ce script ne va rien chercher sur internet.
Il permet seulement de refaire le fichier final à l'identique.

Usage :
    python enrich_products.py products_prices.csv products_prices.csv
(entrée = sortie de select_top30.py, sortie = fichier final à 32 lignes)
"""
import sys
import pandas as pd

src, dst = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, dtype=str, keep_default_na=False)

# 1) Notes /5 lues sur les pages produit de sephora.fr (P04 : aucun avis -> vide)
ratings = {"P01": "4.6", "P02": "4.6", "P03": "4.2", "P05": "4.7", "P06": "4.5", "P07": "4.1",
           "P08": "4.6", "P09": "4.7", "P10": "4.0", "P11": "4.7", "P12": "4.8", "P13": "4.6",
           "P14": "4.5", "P15": "4.6", "P16": "4.8", "P17": "4.6", "P18": "4.3", "P19": "4.7",
           "P20": "4.4", "P21": "4.3", "P22": "4.6", "P23": "4.5", "P24": "4.6", "P25": "4.4",
           "P26": "4.2", "P27": "4.8", "P28": "4.0", "P29": "4.2", "P30": "4.5"}
df["rating_sephora_fr"] = df.product_id.map(ratings).fillna("")

# 2) Prix normaux (hors promotion) relevés sur douglas.nl ("Adviesprijs" ou prix affiché)
#    et iciparisxl.nl ("Productprijs"). Absent du site -> vide.
douglas = {"P02": "25.00", "P08": "24.00", "P12": "33.50", "P15": "28.00", "P16": "39.50",
           "P18": "37.00", "P19": "35.50", "P26": "11.90", "P28": "31.00"}
ici = {"P04": "28.00", "P05": "23.00", "P06": "23.00", "P07": "25.00", "P11": "39.90", "P13": "31.00"}
df["price_douglas_nl_ttc"] = df.product_id.map(douglas).fillna("")
df["price_iciparisxl_nl_ttc"] = df.product_id.map(ici).fillna("")

# 3) Commentaires
comments = {
    "P04": "Note vide : produit sans avis sur sephora.fr",
    "P15": "Douglas : Soft Pinch Liquid Blush (prix 28 EUR, aussi pour la version Matte Liquid 7,5 ml)",
    "P26": "Prix du format mini 6,5 ml, teinte Cuz I'm Black (prix 'a partir de' sur la page) "
           "| Douglas : meme mini 6,5 ml",
}
df["comment"] = df.product_id.map(comments).fillna("")

# 4) Ajout de 2 produits Rhode, hors échantillon top 10 (choix qualitatif)
rhode_comment = ("Ajout hors echantillon top 10 : marque tendance (Rhode), choisie pour son potentiel "
                 "aupres des jeunes clientes NL | Exclusivite verifiee : absent de Douglas NL et d ICI Paris XL NL")
date_col = df.collected_at.iloc[0]
rhode = pd.DataFrame([
    dict(product_id="P31", product_name="Peptide Lip Tint", brand="Rhode", subcategory="Lèvres",
         product_type="Soin des lèvres teinté effet glazed", rank_sephora_fr="", is_lvmh="0",
         price_sephora_fr_ttc="26.00", rating_sephora_fr="4.0", review_count_sephora_fr="3100",
         price_douglas_nl_ttc="", price_iciparisxl_nl_ttc="", collected_at=date_col, comment=rhode_comment),
    dict(product_id="P32", product_name="Pocket Blush", brand="Rhode", subcategory="Teint",
         product_type="Blush crème hydratant modulable", rank_sephora_fr="", is_lvmh="0",
         price_sephora_fr_ttc="33.00", rating_sephora_fr="4.1", review_count_sephora_fr="2100",
         price_douglas_nl_ttc="", price_iciparisxl_nl_ttc="", collected_at=date_col, comment=rhode_comment),
])
df = pd.concat([df, rhode], ignore_index=True)

# 5) Exclusivité : 1 si le produit n'est vendu ni chez Douglas ni chez ICI Paris XL
df["is_verified_exclusive"] = ((df.price_douglas_nl_ttc == "") & (df.price_iciparisxl_nl_ttc == "")).astype(int).astype(str)

df = df[["product_id", "product_name", "brand", "subcategory", "product_type", "rank_sephora_fr", "is_lvmh",
         "price_sephora_fr_ttc", "rating_sephora_fr", "review_count_sephora_fr", "price_douglas_nl_ttc",
         "price_iciparisxl_nl_ttc", "is_verified_exclusive", "collected_at", "comment"]]
df.to_csv(dst, index=False)
print(len(df), "produits ->", dst)
