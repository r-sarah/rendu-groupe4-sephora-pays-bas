# autres/ — anciennes versions (non utilisées)

Ces fichiers sont la première version de la branche `feature/etl-star-ai`. Ils ont été remplacés par les tables nettoyées de `data/silver/` et le modèle de `data/gold/`, produits par `scripts/etl_nettoyage_modele_etoile.py`. Ils sont conservés pour l'historique uniquement.

| Dossier | Contenu | Remplacé par |
|---|---|---|
| `tables_nettoyees_v1/` | 3 tables nettoyées : `products_prices.csv` (31 produits), `google_trends_nl.csv` (format long, 424 lignes), `market_cities_nl.csv` (4 villes) | `data/silver/produits_prix.csv`, `google_trends_long.csv`, `villes_nl.csv` |
| `modele_etoile_v1/` | Premier modèle en étoile : 4 dimensions (`dim_brand`, `dim_product`, `dim_city_nl`, `dim_date`), 3 tables de faits et `build_star_schema.py` | `data/gold/` (8 dimensions, 10 tables de faits) |

Le script `modele_etoile_v1/build_star_schema.py` lisait ces tables dans `data/raw/` : il ne fonctionne plus depuis leur déplacement.
