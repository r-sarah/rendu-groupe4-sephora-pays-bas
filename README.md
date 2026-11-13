# # 💄 Stratégie d'Expansion Européenne 2027-2029 : Implantation de Sephora aux Pays-Bas

> **Problématique Comex :** L'implantation de Sephora (maquillage) aux Pays-Bas est-elle réalisable et rentable ?

>

> **Réponse : NO-GO** pour un magasin 100 % maquillage en rue prime. **Réalisable : oui. Rentable : non** (0 combinaison ville × scénario rentable en 2029).

---

## Sommaire

0. [Liens Utiles](#0-liens-utiles)

1. [Présentation de l'Entreprise & de l'Équipe](#1-présentation-de-lentreprise--de-léquipe)

2. [Résultats & Décision](#2-résultats--décision)

3. [Cadrage & KPIs](#3-cadrage--kpis)

4. [Architecture des Données](#4-architecture-des-données)

5. [Dictionnaire des Données (Couche Gold)](#5-dictionnaire-des-données-couche-gold)

6. [Sources de Données](#6-sources-de-données)

7. [Organisation du Dépôt](#7-organisation-du-dépôt)

8. [Plan d'Organisation & Roadmap](#8-plan-dorganisation--roadmap)

9. [Limites](#9-limites)

10. [Stack Technique Utilisée](#10-stack-technique-utilisée)

---

## 0. Liens Utiles

- **Présentation Comex (Slides) :** [Accéder aux Slides Google Drive]([https://drive.google.com/file/d/1TfmOHh7LE4O_NbHXBt0oaorWcPC0q3Fg/view?usp=drive_link](https://drive.google.com/file/d/1TfmOHh7LE4O_NbHXBt0oaorWcPC0q3Fg/view?usp=drive_link))

- **Dashboard Décisionnel (Looker Studio) :** [Accéder au rapport Looker Studio]([https://datastudio.google.com/reporting/2d9636c3-64c4-4e9f-badd-b18e6e0c38f8](https://datastudio.google.com/reporting/2d9636c3-64c4-4e9f-badd-b18e6e0c38f8))

- **Données sources du dashboard (Google Sheets) :** [Accéder au Google Sheet]([https://docs.google.com/spreadsheets/d/10e3I6Memn1yEiwTryq4xwlqv1FKjsGyOFiKASAMMSOA/edit?usp=drive_link](https://docs.google.com/spreadsheets/d/10e3I6Memn1yEiwTryq4xwlqv1FKjsGyOFiKASAMMSOA/edit?usp=drive_link))

---

## 1. Présentation de l'Entreprise & de l'Équipe

### Périmètre d'activité

- **Entreprise :** **Sephora** (Groupe LVMH), leader de la distribution sélective de produits de beauté en France (**23 %** de part de marché de la beauté sélective en 2024, contre 14 % pour Nocibé).

- **Réseau France :** **~300 magasins physiques** et **2,68 Md€** de chiffre d'affaires (Sephora SAS, 2025).

- **Périmètre Produit étudié :** Catégorie **Makeup (Maquillage)** uniquement (segments *Teint*, *Yeux*, *Lèvres*), analysée sur un panel de **31 références** issues des best-sellers maquillage de `sephora.fr` (13 marques : marques tendance Gen Z / TikTok comme *Rhode, Rare Beauty, Fenty Beauty, Makeup by Mario, Haus Labs*, marques classiques et *Sephora Collection*).

- **Pays Européen Ciblé :** **Pays-Bas**, avec un focus opérationnel sur les **4 pôles urbains majeurs de la Randstad** : *Amsterdam*, *Rotterdam*, *Utrecht* et *La Haye*.

### Contexte Historique & Thèse Stratégique (2013 vs 2027)

- **Le constat de l'échec (2008-2013) :** Sephora avait tenté une première implantation aux Pays-Bas en 2008 (via des corners au sein des grands magasins V&D) avant de se retirer en 2013. À l'époque, l'enseigne proposait un catalogue de parfumerie classique identique à celui du duopole local (**Douglas** et **ICI PARIS XL**, filiale du groupe A.S. Watson), entraînant une guerre des prix défavorable.

- **L'opportunité 2027-2029 :** Le marché de la beauté a basculé vers les marques virales Gen Z / TikTok. Notre étude vérifie par les données si **l'exclusivité de ces références aux Pays-Bas** et leur forte **désirabilité** permettent aujourd'hui un retour rentable.

### Équipe Projet (Data Analytics)

| Membre | Rôle | Branches |

| :--- | :--- | :--- |

| **Ludivine Etou Apendi** — Membre 1 | Data Produits/Prix (scraping), marché NL, prévisions de rentabilité | `feature/scraping-pricing`, `feature/parts-de-marche-nl`, `feature/previsions` |

| **Ema Fernandes** — Membre 2 | Data Marché NL (Google Trends, villes, concurrents), situation actuelle de Sephora & Slides Comex | `feature/market-slides` |

| **Lamyaa Marzouq** — Membre 3 | Data Engineer : ETL, nettoyage (Silver), modèle en constellation (Gold), contrôles qualité | `feature/etl-star-ai` |

| **Sarah Ranganadane** — Membre 4 | Lead Documentation `README.md`) & DataViz | `readme` |

---

## 2. Résultats & Décision

| Axe | KPI | Valeur |

| :--- | :--- | ---: |

| Réalisable | Taille du marché du maquillage aux Pays-Bas (2024) | **515 M€** |

| Réalisable | Croissance annuelle moyenne 2019-2024 | **+6,5 %/an** |

| Réalisable | Part de marché Douglas + ICI Paris XL (magasins physiques) | **21,4 %** |

| Réalisable | Indice de prix NL / France (produits partagés, base 100 = France) | **96,4** |

| Réalisable | Part de produits en exclusivité vérifiée | **54,8 %** |

| Réalisable | Évolution des recherches « sephora » aux Pays-Bas | **+46,3 %** |

| Réalisable | Score de désirabilité : exclusifs / partagés | **72,0 / 56,3** |

| Rentable | Marge brute moyenne par produit (scénario central) | **10,95 € (42,8 %)** |

| Rentable | Combinaisons ville × scénario rentables en 2029 | **0 sur 12** |

| Rentable | Meilleur résultat annuel 2029 (La Haye, optimiste) | **−231 005 €** |

| Rentable | Part de marché minimale nécessaire au point mort | **8,7 %** |

**Conclusion :** le marché, la demande et les exclusivités sont là (**réalisable**), mais le loyer en rue prime et le personnel rendent un magasin 100 % maquillage **non rentable** sur 2027-2029.

**Recommandations :**

1. **Changer de format :** pop-up ou magasin en centre commercial (loyer et équipe réduits).

2. **Élargir l'offre :** ajouter le soin, mais pas le parfum (terrain fort de Douglas et ICI PARIS XL).

3. **Combiner les deux** et recalculer le point mort avec ces nouveaux coûts.

---

## 3. Cadrage & KPIs

### Les 5 Axes Stratégiques & KPIs Retenus

1. **Marché & Potentiel :** Taille du marché du maquillage aux Pays-Bas (€), taux de croissance annuel, part de marché de Sephora en France vs parts de marché de Douglas et ICI PARIS XL aux Pays-Bas.

2. **Prix & Marges :** Indice Prix Relatif (*Sephora FR* vs *Douglas NL / ICI PARIS XL*) et **Marge Brute estimée** (TVA néerlandaise à **21 %** contre 20 % en France), selon 3 scénarios (Pessimiste / Central / Optimiste).

3. **Réseau & Implantation :** Densité des boutiques concurrentes et loyer prime au m² dans les 4 villes de la Randstad.

4. **Opérations & Logistique :** Distance et coût de transport depuis l'entrepôt central Sephora France (Saran, près d'Orléans) vers les Pays-Bas (0 % de droits de douane au sein du marché unique européen).

5. **Assortiment :** Répartition des sous-catégories Makeup (*Teint, Yeux, Lèvres*) et proportion du catalogue en exclusivité vérifiée.

### KPI Propriétaire : Le « Score de Désirabilité »

Afin d'éviter l'erreur de 2013, nous mesurons l'appétence réelle des consommateurs néerlandais via un score composite sur 100 :

$$\text{Score de Désirabilité} = (0.40 \times \text{Google Trends NL}) + (0.35 \times \text{Score Avis \& Notes FR}) + (0.25 \times \text{Bonus Exclusivité Vérifiée})$$

- **Google Trends NL :** score de la marque (0-100, 100 = marque la plus recherchée).

- **Score avis :** note sur 5 ramenée sur 100.

- **Bonus exclusivité :** 100 si le produit est introuvable chez Douglas et ICI PARIS XL, sinon 0.

---

## 4. Architecture des Données

### Architecture Médaillon `Bronze` → `Silver` → `Gold`)

```text

Bronze   data/raw/                 fichiers bruts collectés (scraping, Google Trends, CBS, localisateurs…)

Silver   data/silver/              9 tables nettoyées

Gold     data/gold/                7 dimensions + 8 tables de faits

         data/gold/vues/           8 vues à plat pour Looker Studio (dont les KPI)
