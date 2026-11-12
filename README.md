# # 💄 Stratégie d'Expansion Européenne 2027-2029 : Implantation de Sephora aux Pays-Bas

> **Problématique Comex :** L'implantation de Sephora aux Pays-Bas est-elle réalisable et rentable ?

---

## 1. Présentation de l'Entreprise & de l'Équipe

### Périmètre d'activité

- **Entreprise :** **Sephora** (Groupe LVMH), leader de la distribution sélective de produits de beauté en France.

- **Réseau France :** **~300 magasins physiques** répartis sur le territoire français.

- **Périmètre Produit étudié :** Catégorie **Makeup (Maquillage)** uniquement (segments *Teint*, *Yeux*, *Lèvres*), analysée sur un échantillon stratégique de **30 références phares** (10 par segment) comparant les marques plébiscitées par la Gen Z (*Rare Beauty, Fenty Beauty, Milk Makeup, Sephora Collection*) aux marques classiques.

- **Pays Européen Ciblé :** **Pays-Bas**, avec un focus opérationnel sur les **4 pôles urbains majeurs de la Randstad** : *Amsterdam*, *Rotterdam*, *Utrecht* et *La Haye*.

### Contexte Historique & Thèse Stratégique (2013 vs 2027)

- **Le constat de l'échec (2008-2013) :** Sephora avait tenté une première implantation aux Pays-Bas en 2008 (via des corners au sein des grands magasins V&D) avant de se retirer en 2013. À l'époque, l'enseigne proposait un catalogue de parfumerie classique identique à celui du duopole local (**Douglas** et **ICI PARIS XL**), entraînant une guerre des prix défavorable.

- **L'opportunité 2027-2029 :** Le marché de la beauté a basculé vers les marques virales Gen Z / TikTok (*Rare Beauty, Fenty Beauty, Milk Makeup, Sephora Collection*). Notre étude vise à vérifier empiriquement par les données si **l'exclusivité de ces références aux Pays-Bas** et leur forte **désirabilité** permettent aujourd'hui un retour rentable via un modèle omnicanal ciblé.

### Équipe Projet (Data Analytics)

- **Ludivine Etou Apendi — Membre 1 :** Data Produits/Prix & Page 1 DataViz `feature/products-viz`)

- **Ema Fernandes — Membre 2 :** Data Marché NL & Architecte Slides Comex `feature/market-slides`)

- **Lamyaa Marzouq — Membre 3 :** Data Engineer — ETL, Modèle Étoile, Git & Brique IA `feature/etl-star-ai`)

- **Sarah Ranganadane — Membre 4 :** Lead Documentation `README.md`) & Page 2 DataViz `feature/docs-dashboard`)

---

## 2. Cadrage & Dictionnaire des Données

### Les 5 Axes Stratégiques & KPIs Retenus

1. **Marché & Potentiel :** Taille globale du marché beauté/makeup aux Pays-Bas (€), taux de croissance annuel, part de marché de Sephora en France vs parts de marché de Douglas et ICI PARIS XL aux Pays-Bas.

2. **Prix & Marges :** Indice Prix Relatif (*Sephora FR* vs *Douglas NL / ICI PARIS XL*) et **Marge Brute estimée post-TVA** (intégration de la TVA néerlandaise à **21 %** contre 20 % en France).

3. **Réseau & Implantation :** Densité des boutiques concurrentes et coût moyen au $m^2$ commercial dans les 4 villes de la Randstad.

4. **Opérations & Logistique :** Distance et coût de transport depuis l'entrepôt central Sephora France (Saran, près d'Orléans) vers les Pays-Bas (0 % de droits de douane au sein du marché unique européen).

5. **Assortiment :** Taux de pénétration des sous-catégories Makeup (*Teint, Yeux, Lèvres*) et proportion du catalogue éligible en exclusivité vérifiée.

### KPI Propriétaire : Le « Score de Désirabilité »

Afin d'éviter l'erreur de 2013, nous mesurons l'appétence réelle des consommateurs néerlandais avant implantation via un score composite sur 100 :

$$\text{Score de Désirabilité} = (0.40 \times \text{Google Trends NL}) + (0.35 \times \text{Score Avis \& Notes FR}) + (0.25 \times \text{Bonus Exclusivité Vérifiée})$$

### Dictionnaire des Données (Couche Gold)

| Table | Champ | Type | Description & Règle de Gestion | Exemple |

| :--- | :--- | :--- | :--- | :--- |

| *`Dim_Product`** | `product_id` | `INT` (PK) | Identifiant unique de la référence Makeup | `101` |

| *`Dim_Product`** | `product_name` | `STRING` | Nom commercial du produit | `Soft Pinch Liquid Blush` |

| *`Dim_Product`** | `brand` | `STRING` | Marque du produit | `Rare Beauty` |

| *`Dim_Product`** | `sub_category` | `STRING` | Segment Makeup `Teint`, `Yeux`, `Lèvres`) | `Teint` |

| *`Dim_Product`** | `is_verified_exclusive` | `BOOLEAN` | `True` si absent chez [Douglas.nl](http://Douglas.nl) et ICI PARIS [XL.nl](http://XL.nl), `False` sinon | `True` |

| *`Dim_City_NL`** | `city_id` | `INT` (PK) | Identifiant de la ville cible aux Pays-Bas | `1` |

| *`Dim_City_NL`** | `city_name` | `STRING` | Nom du pôle urbain Randstad | `Amsterdam` |

| *`Dim_City_NL`** | `avg_rent_m2_eur` | `FLOAT` | Loyer commercial annuel moyen au $m^2$ (€) | `1850.0` |

| *`Dim_City_NL`** | `competitor_store_count` | `INT` | Nombre total de magasins Douglas + ICI PARIS XL dans la ville | `14` |

| *`Dim_City_NL`** | `distance_hub_km` | `FLOAT` | Distance routière depuis le hub logistique Sephora de Saran (FR) | `575.0` |

| *`Fact_Product_Pricing`** | `price_sephora_fr_ttc` | `FLOAT` | Prix de vente TTC relevé sur `sephora.fr` (€) | `28.00` |

| *`Fact_Product_Pricing`** | `price_competitor_nl_ttc` | `FLOAT` | Prix moyen TTC relevé sur `douglas.nl` / `iciparisxl.nl` `NULL` si exclusif) | `29.50` |

| *`Fact_Product_Pricing`** | `relative_price_index` | `FLOAT` | Ratio `(Prix NL / Prix FR) * 100` (base 100 = parité France) | `105.3` |

| *`Fact_Product_Pricing`** | `gross_margin_post_vat_21` | `FLOAT` | Marge brute estimée après déduction de la TVA néerlandaise de 21 % (€) | `14.20` |

| *`Fact_Product_Pricing`** | `desirability_score` | `FLOAT` | Score composite d'attractivité client aux Pays-Bas (0 à 100) | `88.5` |

| *`Fact_City_Expansion`** | `market_size_nl_eur` | `FLOAT` | Taille estimée du marché Makeup adressable (€) | `420000000` |

| *`Fact_City_Expansion`** | `logistics_cost_eur` | `FLOAT` | Coût d'acheminement annuel estimé depuis la France (€) | `85000` |

| *`Fact_City_Expansion`** | `net_profit_projection_eur` | `FLOAT` | Résultat opérationnel prévisionnel par ville (€) | `310000` |

---

## 3. Architecture & Choix des Sources

### Architecture Médaillon `Bronze` $\rightarrow$ `Silver` $\rightarrow$ `Gold`)

1. **Bronze `/data/raw`) :** Ingestion des fichiers bruts `products_prices.csv`, `market_cities_nl.csv`).

2. **Silver `/data/silver`) :** Nettoyage via Python (harmonisation des types, suppression des doublons, détection des valeurs aberrantes de prix via la méthode statistique **IQR**, normalisation des scores sur 100).

3. **Gold `/data/gold`) :** Modélisation dimensionnelle en **Schéma en Étoile à 2 Tables de Faits**.

### Justification du Modèle en Étoile à 2 Tables de Faits

Plutôt que de mélanger des données produits et des données géographiques dans une seule table hybride (ce qui créerait des produits cartésiens artificiels et fausserait les agrégations), nous avons conçu **2 Tables de Faits au grain strict** reliées aux dimensions partagées `Dim_Product`, `Dim_City_NL`, `Dim_Competitor`, `Dim_Date`) :

- *`Fact_Product_Pricing` (Grain : 1 ligne = 1 produit)** : Permet l'analyse fine des prix, marges post-TVA 21 % et scores de désirabilité par référence.

- *`Fact_City_Expansion` (Grain : 1 ligne = 1 ville)** : Permet d'évaluer la rentabilité immobilière, logistique et concurrentielle par zone d'implantation.

### Sources de Données Retenues

- **Relevé E-commerce Direct `sephora.fr`, `douglas.nl`, `iciparisxl.nl`) :** Collecte des prix TTC, notes clients, volumes d'avis et vérification de la disponibilité effective des 30 références Makeup aux Pays-Bas.

- **Google Trends (Pays-Bas, 12 derniers mois) :** Mesure objective de l'intérêt de recherche des consommateurs néerlandais pour les marques ciblées.

- **Open Data (CBS Statistics Netherlands / Eurostat) :** Démographie cible et taille du marché cosmétique aux Pays-Bas.

- **NOS & Cushman & Wakefield :** Sources de référence pour l'analyse du marché immobilier commercial et l'estimation des loyers au $m^2$ dans les artères commerçantes de la Randstad.

- **Google Maps :** Géolocalisation et comptage des points de vente concurrents (Douglas et ICI PARIS XL) par ville, ainsi que le calcul des distances routières depuis l'entrepôt logistique Sephora de Saran (France).

---

## 4. Plan d'Organisation & Roadmap

### Méthodologie de Travail

Nous appliquons le cycle **PACE** (*Plan, Analyze, Construct, Execute*) couplé à un workflow **Git Feature Branch** : chaque membre développe sur sa branche dédiée `feature/`*), puis fusionne sur `develop` pour validation avant mise en production sur `main`.

### Roadmap d'Exécution

- **Phase 1 — Plan & Cadrage :** Définition des 5W, sélection des 30 produits Makeup et des 4 villes Randstad, initialisation du dépôt Git.

- **Phase 2 — Collecte & Nettoyage (Bronze $\rightarrow$ Silver) :** Extraction des données prix/concurrence, Google Trends NL, Open Data villes/marché et rédaction du dictionnaire de données.

- **Phase 3 — Modélisation Gold, DataViz & Brique IA :** Génération des 2 Tables de Faits et 4 Dimensions, création du Dashboard décisionnel (2 pages) et exécution du script IA de synthèse Comex.

- **Phase 4 — Arbitrage & Restitution Comex :** Synthèse stratégique Go/No-Go et soutenance orale de 10 minutes.

### Next Steps (Recommandations Post-Étude)

1. **Phase Pilote (T1-T2 2027) :** Lancement du site e-commerce `sephora.nl` expédié depuis la France pour valider les taux de conversion réels par code postal néerlandais avant tout bail commercial.

2. **Ouverture Flagships Ciblés (T3 2027 – 2028) :** Ouverture prioritaire de **2 à 3 magasins étendards** dans les artères à plus fort trafic de la Randstad (*Kalverstraat* à Amsterdam, *Koopgoot* à Rotterdam, *Hoog Catharijne* à Utrecht) avec un assortiment concentré à **75 % sur les marques exclusives à fort Score de Désirabilité**.

3. **Industrialisation Data :** Automatisation hebdomadaire du scraping des prix concurrents et suivi du taux de rachat client via le programme de fidélité Sephora.

---

## 5. Stack Technique Utilisée

- **Collecte & Exploration :** Google Trends, Open Data CBS/Eurostat, Cushman & Wakefield, NOS, Google Maps, relevés web structurés (CSV).

- **ETL, Nettoyage & Modélisation :** Python `pandas`, `numpy`) — architecture Médaillon `Bronze` / `Silver` / `Gold`).

- **Intelligence Artificielle Générative :** Python + API LLM (génération automatisée d'un mémo exécutif comparant les scénarios d'implantation pour le Comex).

- **Data Visualisation :** Power BI / Looker Studio (Dashboard décisionnel interactif en 2 pages).

- **Versioning & Collaboration :** Git & GitHub (stratégie de branches `main`, `develop`, `feature/`*).