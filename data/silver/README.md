# Couche Silver – Données nettoyées

> Projet Sephora (LVMH) – Étude d'implantation aux Pays-Bas.
> Script : `clean_silver.py`. Exécution : `python data/silver/clean_silver.py` (pandas requis).

Le script lit les fichiers bruts de `data/raw/` et `data/previsions/`, les nettoie, écrit 13 tables dans ce dossier, puis lance 21 contrôles de qualité. Il est déterministe : relancé, il produit exactement les mêmes fichiers.

## Principes

- **Les clés de jointure sont des identifiants** (`product_id`, `city_id`, `store_id`), jamais des noms : La Haye porte plusieurs noms selon les sources (La Haye, Den Haag).
- **Les noms de marques sont harmonisés** entre Google Trends et les produits, pour que les tables puissent être reliées.
- **Aucune valeur n'est inventée** : une donnée absente reste vide ; un produit sans note est retiré plutôt que complété.
- **Chaque correction est documentée** ci-dessous et affichée dans le journal d'exécution du script.

## Tables produites

| Table | Lignes | Contenu | Source brute |
|---|---:|---|---|
| `produits_prix.csv` | 31 | Produits maquillage : prix France, prix concurrents NL, notes, avis, exclusivité | `data/raw/products_prices.csv` |
| `google_trends_long.csv` | 424 | Intérêt de recherche Google aux Pays-Bas, 1 ligne par semaine et par marque | `data/raw/google_trends/google_trends_nl.csv` |
| `villes_nl.csv` | 4 | Villes cibles : population, loyer prime, concurrents, distances | `data/raw/villes/market_cities_nl.csv` |
| `villes_sources.csv` | 4 | Sources et commentaires des données villes | `data/raw/villes/market_cities_nl.csv` |
| `magasins_concurrents.csv` | 130 | Magasins Douglas (111, tout le pays) et ICI Paris XL (19, villes cibles) | `data/raw/concurrents/*.csv` |
| `sephora_indicateurs.csv` | 14 | Chiffres actuels de Sephora (France, LVMH, monde, Belgique) | `data/raw/sephora/sephora_situation_actuelle.csv` |
| `sephora_magasins_belgique.csv` | 5 | Magasins Sephora en Belgique (ouverts, annoncés, en projet) | `data/raw/sephora/sephora_situation_actuelle.csv` |
| `pays_fiscalite.csv` | 2 | TVA, douane, devise, réglementation (France, Pays-Bas) | `data/raw/pays_fiscalite.csv` |
| `marche_maquillage.csv` | 8 | Taille et croissance du marché du maquillage et du marché cosmétique NL | `data/raw/marche/marche_maquillage_nl.csv` |
| `parts_de_marche_canaux.csv` | 8 | Ventes et parts de marché par canal, dont Douglas et ICI Paris XL | `data/raw/marche/parts_de_marche_canaux_nl.csv` |
| `prix_vente_nl.csv` | 31 | Prix de vente prévisionnels de Sephora aux Pays-Bas (option C) | `data/previsions/prix_vente_nl.csv` |
| `marges_nl.csv` | 93 | Marge brute prévisionnelle, 1 ligne par produit et par scénario (31 × 3) | `data/previsions/marges_nl.csv` |
| `rentabilite_villes.csv` | 36 | Rentabilité prévisionnelle par ville, scénario et année (2027-2029) | `data/previsions/rentabilite_villes_nl.csv` |

Fichiers bruts non utilisés : `bestsellers_maquillage.csv` (source de l'échantillon, hors modèle) et `trends_sephora_nl.csv` (identique à la colonne `sephora` de `google_trends_nl.csv`).

## Corrections par table

### `produits_prix.csv`

| Anomalie | Correction |
|---|---|
| P04 (Liquid Matte Mousse) : aucun avis, note absente | Produit retiré |
| Noms en majuscules (GLOSS BALM, 12H COLORFUL…) | Casse harmonisée (13 noms) |
| Symboles ® et ™ (SoftSculpt®, Shape tape™…) | Supprimés |
| P14 : type de produit dans le nom, teinte dans la colonne type | Nom « HD Skin Face Essentials », type « Palette teint », teinte dans la nouvelle colonne `variant` |
| P17 : nom trop vague (« SoftSculpt ») | « SoftSculpt Sérum Bronzant » |
| P22 : nom incomplet (« 12H COLORFUL ») | « 12H Colorful Crayon Yeux » |
| P29 : type en majuscules | « Waterproof crayon yeux » |
| P06 : faute de frappe du site source (« brilliance ») | « Gloss haute brillance » |
| Commentaires sans accents ; commentaire Rhode obsolète | Accents rétablis ; exclusivité Rhode notée comme vérifiée |
| Rang et nombre d'avis stockés en décimal (7.0) | Convertis en entiers |
| Ajouts | `in_top10_sephora_fr` (0 pour les 2 produits Rhode ajoutés hors échantillon), `is_mini_format` (1 pour P26, prix d'un format mini) |

### `google_trends_long.csv`

| Anomalie | Correction |
|---|---|
| Format large (1 colonne par marque) | Format long : `semaine`, `marque`, `score_trends` |
| Semaine du 26/10/2025 hors période d'étude | Retirée (période : 02/11/2025 → 01/11/2026, 53 semaines) |
| Noms de marques différents des produits (HUDA BEAUTY, rhode, makeup by mario) | Harmonisés (Huda Beauty, Rhode, Makeup By Mario) |
| « Sephora » = l'enseigne, pas la marque Sephora Collection | Colonne `is_enseigne` = 1 pour ne pas les confondre |

### `villes_nl.csv`

| Anomalie | Correction |
|---|---|
| Colonnes de texte (sources, commentaire) mêlées aux chiffres | Déplacées dans `villes_sources.csv` |
| Durée de trajet en texte (« 7h04 ») | `duree_route_saran_min` en minutes |
| Distance depuis Bruxelles estimée | Colonne `distance_bruxelles_estimee` = 1 |
| Tranche d'âge | Nom `15_44` conservé : les données CBS portent sur les 15-44 ans |
| `nb_concurrents_total` inclut De Bijenkorf, absent de la liste des magasins | Ajout de `nb_douglas_ici` (Douglas + ICI Paris XL), comparable à `magasins_concurrents` |

### `magasins_concurrents.csv`

| Anomalie | Correction |
|---|---|
| Deux fichiers séparés (Douglas, ICI Paris XL) | Réunis, avec une clé `store_id` |
| « Den Haag » (Douglas) et « La Haye » (ICI, villes) | Harmonisé en « La Haye » + `city_id` |
| Codes postaux « 1811 JG » et « 1077JH » | Format unique « 1234 AB » |
| ICI Paris XL sans coordonnées GPS | Colonne `has_gps` (0 pour ICI) |
| Douglas couvre tout le pays, ICI Paris XL seulement les 4 villes | Colonne `is_ville_cible` (1 pour les 4 villes) |

### `sephora_indicateurs.csv` et `sephora_magasins_belgique.csv`

| Anomalie | Correction |
|---|---|
| Colonne `valeur` mêlant nombres, dates et textes (« annoncé ») | Séparation en 2 tables : indicateurs chiffrés et magasins belges |
| Chiffre d'affaires 2025 marqué « à revérifier » par la source | Colonne `a_reverifier` = 1 |
| Surface des magasins belges | 270 m² (Docks Bruxsel) et 400 m² (Médiacité), sinon vide |

### Prévisions

| Anomalie | Correction |
|---|---|
| P04 présent dans `prix_vente_nl` et `marges_nl` | Retiré, pour rester cohérent avec `produits_prix` |
| Taux de marge moyens de `rentabilite_villes` calculés avec P04 | Table inchangée : sans P04, les moyennes varient de moins de 0,1 point |
| `marges_nl` en format large (1 colonne par scénario) | Format long (1 ligne par produit et par scénario), pour partager la dimension « scénario » avec `rentabilite_villes` |

## Contrôles de qualité (21)

Unicité des clés (`product_id`, `city_id`, `store_id`, semaine × marque) ; absence de P04 ; aucune note manquante ; cohérence entre exclusivité et absence de prix NL ; plus aucun ® ni ™ ; 53 semaines × 8 marques ; 5 marques communes entre Trends et produits ; nombre de magasins Douglas et ICI Paris XL par ville identique à `villes_nl` (par enseigne et au total, via `nb_douglas_ici`) ; parts de marché par canal égales à 100 % ; tables de prévisions reliées aux produits et aux villes ; `marges_nl` à 1 ligne par produit et par scénario, avec les mêmes scénarios que `rentabilite_villes` ; indicateurs Sephora tous numériques.

Résultat attendu en fin d'exécution : `tous les contrôles sont OK`.

## Points d'attention pour le modèle et le dashboard

- **De Bijenkorf** (grand magasin de luxe néerlandais, rayon beauté) est compté comme concurrent dans `villes_nl.nb_concurrents_total` (1 par ville), mais ne figure pas dans `magasins_concurrents` (pas de liste de magasins relevée). Pour comparer avec `magasins_concurrents`, utiliser `nb_douglas_ici` (sans De Bijenkorf) ; `nb_concurrents_total` (avec De Bijenkorf) reste disponible pour la densité concurrentielle.
- **Séparateur décimal** : les fichiers utilisent le point (ex. `4.6`). Dans un outil configuré en français, régler la langue ou les paramètres régionaux de la source de données sur l'anglais si les nombres sont mal lus.
