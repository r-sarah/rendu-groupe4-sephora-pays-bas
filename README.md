# rendu-groupe4-sephora-pays-bas

Données **marché Pays-Bas (Membre 2)** + **prix & produits (Membre 1)** — 3 tables nettoyées.

> **Contenu de la branche :** uniquement les tables nettoyées.

## Fichiers

| Fichier | Contenu | Statut |
|---|---|---|
| `data/raw/google_trends/google_trends_nl.csv` | Format **long** : `semaine`, `marque`, `score_trends` (424 lignes = 53 semaines × 8 marques) | **nettoyé** |
| `data/raw/villes/market_cities_nl.csv` | Dim_City_NL — 4 villes (colonnes texte retirées, voir plus bas) | **nettoyé** |
| `data/raw/concurrents/products_prices.csv` | 31 références phares Makeup — prix FR, prix Douglas NL, prix ICI Paris XL, notes, exclusivité | **nettoyé** |

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
