# rendu-groupe4-sephora-pays-bas

Données **marché Pays-Bas (Membre 2)** + **prix & produits (Membre 1)** — 3 tables nettoyées.

> **Contenu de la branche :** uniquement les tables nettoyées.

## Fichiers

| Fichier | Contenu | Statut |
|---|---|---|
| `data/raw/google_trends/google_trends_nl.csv` | Format **long** : `semaine`, `marque`, `score_trends` (424 lignes = 53 semaines × 8 marques) | **nettoyé** |
| `data/raw/villes/market_cities_nl.csv` | Dim_City_NL — 4 villes (colonnes texte retirées, voir plus bas) | **nettoyé** |
| `data/raw/concurrents/products_prices.csv` | 31 références phares Makeup — prix FR, prix Douglas NL, prix ICI Paris XL, notes, exclusivité | **nettoyé** |
| `data/gold/` | **Modèle en étoile** — 4 dimensions + 3 tables de faits | généré |
| `scripts/build_star_schema.py` | Script de construction du modèle | — |

---

# Nettoyage — marché NL

**`google_trends_nl.csv`**
- Format large → **format long** (une ligne par semaine et par marque) pour permettre les jointures.
- `Time` converti en date. Semaine du **26/10/2025 supprimée** : avant le début de la période étudiée (01/11/2025). Période retenue : 02/11/2025 → 01/11/2026.
- Noms de marques harmonisés (`sephora` → `Sephora`, `HUDA BEAUTY` → `Huda Beauty`, `rhode` → `Rhode`, `makeup by mario` → `Makeup By Mario`…), alignés sur `products_prices.csv` pour que la jointure marque ↔ produit fonctionne.
- Doublons : aucun.

**Score de désirabilité (40 %)** — moyenne 12 mois par marque, ramenée sur 0–100 :

| marque | moyenne_12m | score_trends_0_100 |
|---|---:|---:|
| Sephora | 50.15 | 100.0 |
| Rhode | 24.06 | 48.0 |
| Huda Beauty | 19.02 | 37.9 |
| Rare Beauty | 13.23 | 26.4 |
| Fenty Beauty | 8.49 | 16.9 |
| Makeup By Mario | 3.94 | 7.9 |
| Haus Labs | 2.55 | 5.1 |
| Kylie Cosmetics | 1.43 | 2.9 |

> ⚠️ **Pic de fin août conservé.** La semaine du 30/08/2026 est un pic réel et simultané (Sephora 100, Rare Beauty 53, Fenty Beauty 43, Huda Beauty 37), pas une erreur. Le retirer avec une méthode IQR fausserait les moyennes (−1,1 pt pour Rare Beauty, −1,0 pour Fenty Beauty). Il est donc conservé, simplement mentionné.

**`market_cities_nl.csv`**
- Colonnes texte `source_population`, `source_loyer`, `source_concurrents`, `commentaire` **retirées de la table** et reportées ci-dessous.
- Nommage aligné sur le modèle : `population_15_44` → `population_15_45` (idem `part_15_44_pct`, `pop_15_44_par_concurrent`). Le modèle parle de « population 15-45 ans », le fichier de « 15-44 » : **même cible, un seul nom**.
- La Haye porte 4 noms selon la source : **c'est `city_id` qui sert de clé de jointure**, jamais le nom.
- Doublons : aucun.

---

# Nettoyage — produits & prix

**`products_prices.csv`**

| Problème | Traitement |
|---|---|
| Noms tout en majuscules | `GLOSS BALM` → `Gloss Balm`, `LIP TINT FELT LINER` → `Lip Tint Felt Liner`, `SPECIAL EFFECTS GLITTER SHADOW` → `Special Effects Glitter Shadow`, `CRAYON CONTOUR YEUX 12H` → `Crayon Contour Yeux 12H` (13 noms harmonisés) |
| Symboles ® et ™ | Supprimés : `SoftSculpt®`, `Shape tape™`, `Master Mattes®`… (6 noms) |
| Nom incomplet | `12H COLORFUL` → **`12H Colorful Crayon Yeux`** (le type crayon venait de `product_type`) |
| Nom trop vague | `SoftSculpt®` → **`SoftSculpt Sérum Bronzant`** |
| Type de produit dans le nom | `HD Skin Face Essentials – Palette teint` → nom **`HD Skin Face Essentials`**, `product_type` = **`Palette teint`**, teinte `H1 (26,5 g)` → nouvelle colonne **`variant`** |
| `product_type` | Outliers corrigés : `WATERPROOF CRAYON YEUX` → `Waterproof crayon yeux` |
| Accents absents dans `comment` | P26 (`meme`→`même`, `a partir de`→`à partir de`), P31 et P32 (`echantillon`→`échantillon`, `aupres`→`auprès`, `reverifier`→`révérifier`, `bloque`→`bloqué`, `releve`→`relevé`, `d ICI`→`d'ICI`) |
| Référence sans avis | **P04** (`Liquid Matte Mousse`, Huda Beauty) : 0 avis sur sephora.fr, note réellement manquante → **référence supprimée** plutôt qu'une note inventée. Plus aucune note absente ni 0 avis dans la table |
| Doublons | Aucun |

**Résultat** : 31 références (Lèvres 10 / Teint 11 / Yeux 10), 9 prix Douglas NL, 5 prix ICI Paris XL, 17 références en exclusivité vérifiée.

---

# Sources (colonnes retirées de Dim_City_NL)

| city_id | ville | source population | rue de référence (loyer prime) | source loyer | source concurrents | commentaire |
|---:|---|---|---|---|---|---|
| 1 | Amsterdam | CBS StatLine 03759ned (1er janvier 2026) | Kalverstraat | NOS (classement rues les plus chères — année à vérifier) | Localisateurs douglas.nl et iciparisxl.nl relevés le 2026-11-12 | Saran : Google Maps 2026-11-12 (itinéraire le plus rapide) ; Bruxelles : estimation à vérifier |
| 2 | Rotterdam | CBS StatLine 03759ned (1er janvier 2026) | Lijnbaan | NOS (classement rues les plus chères — année à vérifier) | Localisateurs douglas.nl et iciparisxl.nl relevés le 2026-11-12 | Saran : Google Maps 2026-11-12 (itinéraire le plus rapide) ; Bruxelles : estimation à vérifier |
| 3 | Utrecht | CBS StatLine 03759ned (1er janvier 2026) | Lange Elisabethstraat | NOS (classement rues les plus chères — année à vérifier) | Localisateurs douglas.nl et iciparisxl.nl relevés le 2026-11-12 | Saran : Google Maps 2026-11-12 (itinéraire le plus rapide) ; Bruxelles : estimation à vérifier |
| 4 | La Haye | CBS StatLine 03759ned (1er janvier 2026) | Spuistraat | Cushman & Wakefield nov. 2025 | Localisateurs douglas.nl et iciparisxl.nl relevés le 2026-11-12 | Saran : Google Maps 2026-11-12 (itinéraire le plus rapide) ; Bruxelles : estimation à vérifier |

Autres sources : Google Trends NL (01/11/2025 – 12/11/2026, type « terme de recherche », `rhode` en marque/topic Google pour exclure « Rhode Island »), relevé du 12/11/2026 ; sephora.fr (prix et notes, 12/11/2026) ; douglas.nl et iciparisxl.nl (prix NL, relevés le 12/11/2026).

# Contrôles qualité passés

| Contrôle | Résultat |
|---|---|
| Doublons (exacts et sur clé métier) | 0 sur les 3 tables |
| Espaces parasites / tabulations | 0 |
| Cellules vides inattendues | 0 |
| Notes : aucune absente, aucun 0 avis | OK (P04 supprimé) |
| Cohérence compteurs magasins ↔ table villes | OK (9/5/3/4 Douglas, 6/5/3/5 ICI Paris XL) |

# Limites

- **Loyers** : `loyer_prime_m2_an_eur` est le loyer de **la rue la plus chère** (« prime »), pas un loyer moyen. Les sources n'ont pas la même date (NOS sans millésime confirmé, Cushman & Wakefield nov. 2025) : les valeurs ne sont pas strictement comparables d'une ville à l'autre.
- **Distances depuis Bruxelles** : estimations, à vérifier.
- **Année du classement des loyers NOS** : à vérifier.
- **Saran** (entrepôt central Sephora France) : hypothèse de l'équipe.
- **Google Trends** : volumes normalisés 0–100 dans une requête unique, donc **relatifs** (entre marques et entre semaines), pas absolus.
- **Pic du 30/08/2026** : conservé volontairement (voir plus haut).
- **Alignement des marques** : `Makeup by Mario` → `Makeup By Mario` a été appliqué pour que la jointure avec `products_prices.csv` fonctionne. Restent à trancher : `Haus Labs` (Trends) vs `Haus Labs By Lady Gaga` (autre table) et `Sephora` (Trends, l'enseigne) vs `Sephora Collection` (produits, la marque maison) — deux concepts différents, à ne pas confondre.
- **P04 supprimé** de `products_prices.csv` : le produit (0 avis) reste dans `bestsellers_maquillage.csv` sur la branche `feature/scraping-pricing` — à supprimer également si l'on veut l'éliminer partout.

---

# Modèle en étoile (couche Gold)

Construit par `scripts/build_star_schema.py` à partir des 3 tables nettoyées.

> **UNE seule étoile** : les dimensions sont **partagées** entre les domaines marques, produits et villes.
> Règle appliquée : **un grain par table de faits**, jamais de produit × ville (produit cartésien).

```
                        ┌──────────────┐
                        │  Dim_Date    │  54 dates
                        └──────┬───────┘
                               │
 ┌───────────────┐    ┌─────────┴──────────┐    ┌────────────────────┐
 │  Dim_Product  │───▶│ Fact_Product_Pricing│   │ Fact_City_Expansion│◀─┐
 │  31 produits  │    │  grain : 1 produit  │    │  grain : 1 ville (4)│ │
 └───────┬───────┘    │        (31)        │    └─────────┬──────────┘ │
         │            └──────────┬──────────┘              │            │
         │              ┌────────┴──────────┐      ┌───────┴───────┐    │
         │              │    Dim_Brand      │      │  Dim_City_NL │────┘
         │              │   13 marques      │      │  4 villes    │
         └─────────────▶│                   │      └───────────────┘
                        └────────┬──────────┘
                                 │
                        ┌────────┴───────────────────┐
                        │  Fact_Search_Interest      │
                        │  grain : marque × semaine  │
                        │           (424)            │
                        └────────────────────────────┘
```

## Les 4 dimensions

| Table | Grain | Lignes | Colonnes |
|---|---|---:|---|
| `dim_brand.csv` | 1 marque | 13 | `brand_key`, `brand`, `brand_group`, `is_lvmh`, `in_google_trends`, `in_products_prices`, `moyenne_12m`, `score_trends_0_100` |
| `dim_product.csv` | 1 produit | 31 | `product_key`, `product_id`, `product_name`, `brand`, `brand_key`, `subcategory`, `product_type`, `variant`, `is_verified_exclusive`, `is_lvmh` |
| `dim_city_nl.csv` | 1 ville | 4 | `city_key`, `city_id`, `ville`, `population_totale`, `population_15_45`, `part_15_45_pct`, `loyer_prime_m2_an_eur`, `rue_reference_loyer`, `distance_hub_saran_km`, `duree_route_saran`, `distance_bruxelles_km` |
| `dim_date.csv` | 1 date | 54 | `date_key` (AAAAMMJJ), `date`, `annee`, `trimestre`, `mois`, `semaine_iso`, `jour` |

`Dim_Brand` = union des 8 marques suivies sur Google Trends et des 10 marques produits (13 au total, 5 communes). `brand_group` : LVMH · Sephora (maison) · Marque tendance · Concurrent.

## Les 3 tables de faits

| Table | Grain | Lignes | Contenu |
|---|---|---:|---|
| `fact_product_pricing.csv` | 1 produit | 31 | Prix FR, prix Douglas NL, prix ICI Paris XL, prix concurrent mini, note, nb d'avis, score Trends, score avis, bonus exclusivité, **score de désirabilité**, indice prix relatif, écart de prix HT |
| `fact_search_interest.csv` | 1 marque × 1 semaine | 424 | Score Trends hebdomadaire, flag `is_peak` (8 lignes sur la semaine du 30/08/2026) |
| `fact_city_expansion.csv` | 1 ville | 4 | Nb de concurrents par enseigne, total, concurrents /100k hab, 15-45 par concurrent, distance hub |

## Le Score de désirabilité

```
Score de désirabilité = 0,40 × Google Trends NL (marque)
                      + 0,35 × Score Avis & Notes FR (produit)
                      + 0,25 × Bonus Exclusivité Vérifiée (produit)
```

| Terme | Calcul | Grain |
|---|---|---|
| `score_trends_0_100` | moyenne 12 mois de Google Trends ramenée sur 100 | marque |
| `score_avis_0_100` | `note / 5 × 100` | produit |
| `bonus_exclusivite_0_100` | 100 si `is_verified_exclusive = 1`, sinon 0 | produit |

**Top 10 des 31 références** (16 ont un score ; les 15 autres n'ont pas de score Trends) :

| produit | marque | groupe | score | trends | avis | exclusivité |
|---|---|---|---:|---:|---:|---:|
| Pocket Blush | Rhode | Tendance | **72.9** | 48.0 | 82.0 | 100 |
| Peptide Lip Tint | Rhode | Tendance | **72.2** | 48.0 | 80.0 | 100 |
| Ethereal Eyes Eyeshadow Palette: The Original | Makeup By Mario | Tendance | 61.8 | 7.9 | 96.0 | 100 |
| SoftSculpt Sérum Bronzant | Makeup By Mario | Tendance | 60.4 | 7.9 | 92.0 | 100 |
| Master Mattes Long-Wear Cream Eyeshadow | Makeup By Mario | Tendance | 59.7 | 7.9 | 90.0 | 100 |
| Master Mattes Eyeshadow Palette | Makeup By Mario | Tendance | 59.7 | 7.9 | 90.0 | 100 |
| Master Mattes Eyeshadow Palette: The Neutrals | Makeup By Mario | Tendance | 59.0 | 7.9 | 88.0 | 100 |
| Lip Contour 2.0 | Huda Beauty | Tendance | 48.1 | 37.9 | 94.0 | 0 |
| Easy Bake Loose Baking & Setting Powder | Huda Beauty | Tendance | 48.1 | 37.9 | 94.0 | 0 |
| #FauxFilter Luminous Matte Liquid Concealer | Huda Beauty | Tendance | 47.4 | 37.9 | 92.0 | 0 |

Score moyen par groupe de marque :

| groupe | réf. | score moyen | prix moyen | indice prix moyen |
|---|---:|---:|---:|---:|
| Marque tendance | 13 | **55.6** | 38.5 € | 96.2 |
| LVMH | 5 | 38.1 | 36.2 € | 94.2 |
| Concurrent | 5 | — | 35.5 € | 98.7 |
| Sephora (maison) | 8 | — | 13.0 € | — |

> Les 8 références **Sephora Collection** n'ont pas de score : le terme Google Trends suivi est « sephora » (l'enseigne), pas la marque maison. Sephora n'a pas besoin d'un score de désirabilité de concurrent — c'est l'incumbent. L'indice de prix relatif est également vide pour elles (prix NL non relevés).

## Contrôles qualité passés

| Contrôle | Résultat |
|---|---|
| Unicité des PK des 4 dimensions | OK |
| Intégrité référentielle des 7 clés étrangères | OK (0 orphelin) |
| Unicité du grain déclaré des 3 tables de faits | OK |
| Pas de `city_key` dans `Fact_Product_Pricing` | OK (pas de produit × ville) |
| Score Trends de la table de faits = celui de `Dim_Brand` | OK |
| Notes : aucune absente, aucun 0 avis | OK (P04 supprimé) |
| Compteurs magasins ↔ table villes | OK (9/5/3/4 Douglas, 6/5/3/5 ICI Paris XL) |

## KPI restant à compléter

3 colonnes sont **volontairement vides** : elles dépendent d'hypothèses économiques que l'équipe doit valider, on ne les invente pas.

| KPI | Table | Ce qu'il faut |
|---|---|---|
| `marge_brute_post_vat_21_eur` | `fact_product_pricing` | Hypothèse de coût de revient. L'ingrédient factuel est déjà là : `ecart_prix_ht_eur` = `prix_NL_TTC / 1,21 − prix_FR_TTC / 1,20` |
| `market_size_nl_eur` | `fact_city_expansion` | Hypothèse de taille de marché (makeup NL par ville) |
| `logistics_cost_eur` | `fact_city_expansion` | Coût d'acheminement Saran → NL (distance et durée sont déjà dans `Dim_City_NL`) |

## Rejouer le modèle

```bash
pip install pandas
python scripts/build_star_schema.py
```

Le script relit les 3 tables nettoyées et **réécrit `data/gold/`** à l'identique (génération déterministe), puis affiche les contrôles de cohérence. La constante `SILVER` en tête de script pointe vers le dossier des tables nettoyées : la migration vers `data/silver/` (architecture Bronze → Silver → Gold) ne demande qu'une ligne à changer.
