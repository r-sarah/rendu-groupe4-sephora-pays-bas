"""Transforme le texte copié (Ctrl+A / Ctrl+C) de la page
sephora.fr > Maquillage > Meilleures ventes en fichier CSV.

Usage :
    python parse_sephora.py sephora_bestsellers_maquillage_168.txt bestsellers_maquillage.csv [AAAA-MM-JJ]

Le 3e argument (facultatif) est la date de collecte écrite dans la colonne
collected_at. Sans lui, c'est la date du jour. Pour reproduire exactement
le fichier du projet : 2026-11-12.

Sortie : un produit par ligne, dans l'ordre du classement de la page (168 produits).
Colonnes : rank_sephora_fr, brand, product_name, product_type,
price_sephora_fr_ttc, original_price_sephora_fr_ttc, from_price,
review_count_sephora_fr, badge, collected_at, source
"""
import csv
import re
import sys
from datetime import date

src, dst = sys.argv[1], sys.argv[2]
collected_at = sys.argv[3] if len(sys.argv) > 3 else date.today().isoformat()

lines = [l.strip() for l in open(src, encoding="utf-8")]
price_re = re.compile(r"^(\d+,\d{2}) €$")
BADGES = {"Best seller", "Exclu", "Hot on social", "Nouveauté", "Clean at Sephora", "Offre fidélité web"}


def nxt(k):
    """Renvoie la prochaine ligne non vide après l'indice k."""
    k += 1
    while k < len(lines) and not lines[k]:
        k += 1
    return lines[k] if k < len(lines) else ""


rows = []
for i, l in enumerate(lines):
    m = price_re.match(l)
    # Une ligne "12,99 €" = un prix. On ignore le prix barré (précédé de "Prix d'origine :").
    if not m or lines[i - 1] == "Prix d'origine :":
        continue
    # On remonte jusqu'à l'en-tête du produit : "MARQUE - Nom", suivi d'une ligne "MARQUE".
    j = i - 1
    while j > 0 and not (nxt(j) and lines[j].startswith(nxt(j) + " - ")):
        j -= 1
    brand, name = lines[j].split(" - ", 1)
    block = [b for b in lines[j + 1:i] if b and b != "À partir de"]
    ptype = block[2] if len(block) > 2 else ""
    # Prix d'origine (si le produit est en promotion) et nombre d'avis
    k, original, nb = i + 1, "", ""
    if k < len(lines) and lines[k] == "Prix d'origine :":
        original = lines[k + 1].replace(" €", "").replace(",", ".")
        k += 3
    for look in lines[k:k + 3]:
        if look.isdigit():
            nb = look
            break
        if look == "Aucun avis":
            nb = "0"
            break
    rows.append({
        "rank_sephora_fr": len(rows) + 1,
        "brand": brand.strip().title(),
        "product_name": name.strip(),
        "product_type": ptype,
        "price_sephora_fr_ttc": m.group(1).replace(",", "."),
        "original_price_sephora_fr_ttc": original,
        "from_price": int(lines[i - 1] == "À partir de"),
        "review_count_sephora_fr": nb,
        "badge": lines[j - 1] if lines[j - 1] in BADGES else "",
        "collected_at": collected_at,
        "source": "sephora.fr > Maquillage > Meilleures ventes",
    })

with open(dst, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "produits ->", dst)
