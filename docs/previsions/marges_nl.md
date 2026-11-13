# Marge brute prévisionnelle aux Pays-Bas

> Projet Sephora (LVMH) – Étude d'implantation aux Pays-Bas.
> Données : `marges_nl.csv` (32 produits, une ligne par produit, 3 scénarios en colonnes). Calcul réalisé le 13 novembre 2026.

Selon le scénario, la marge brute moyenne de Sephora aux Pays-Bas serait comprise entre **36,6 % et 46,9 %** du prix de vente hors taxes, soit **9,40 € à 11,90 € par produit**. Les produits exclusifs conservent la marge française ; les produits également vendus par Douglas ou ICI Paris XL perdent environ 3 points de marge, du fait de l'alignement des prix.

## Sommaire

1. [Définition](#1-définition)
2. [Choix des taux de marge par scénario](#2-choix-des-taux-de-marge-par-scénario)
3. [Méthode de calcul](#3-méthode-de-calcul)
4. [Résultats](#4-résultats)
5. [Hypothèses et limites](#5-hypothèses-et-limites)
6. [Sources](#6-sources)

---

## 1. Définition

```text
Marge brute (€) = prix de vente hors taxes − coût d'achat hors taxes
Taux de marge brute (%) = marge brute / prix de vente hors taxes
```

- Le prix est pris **hors taxes** : la TVA (21 % aux Pays-Bas) est reversée à l'État.
- La marge brute **n'est pas le bénéfice** : elle doit encore couvrir le loyer, le personnel, la logistique et les autres charges. Le bénéfice est calculé dans l'étude de rentabilité par ville.

## 2. Choix des taux de marge par scénario

Sephora (LVMH) ne publie pas son taux de marge brute, et aucun distributeur ne publie de marge propre au marché néerlandais. Les taux retenus s'appuient sur les marges publiées de deux distributeurs beauté cotés.

| Scénario | Taux de marge brute (France) | Référence | Justification |
|---|---:|---|---|
| Pessimiste | 38 % | Ulta Beauty : 39,1 % (exercice 2025) | Distributeur beauté multimarque comparable ; arrondi à la baisse pour tenir compte des promotions de lancement d'un nouvel entrant |
| Central | 44 % | Douglas Group : 43,6 % (T1 2024/25) à 45,3 % (T3 2024/25) | Concurrent direct de Sephora, présent aux Pays-Bas (111 magasins) |
| Optimiste | 48 % | Douglas Group + 4 points | Poids des exclusivités et de la marque propre Sephora Collection, à marge plus élevée |

Les marges de Douglas portent sur l'ensemble du groupe (22 pays, dont les Pays-Bas). Celles d'Ulta Beauty portent sur les États-Unis.

## 3. Méthode de calcul

Le coût d'achat d'un produit est supposé **identique en France et aux Pays-Bas** (mêmes fournisseurs, même groupe acheteur). Il est déduit du prix France et du taux de marge du scénario.

```text
Prix France HT        = prix France TTC / 1,20
Coût d'achat HT       = prix France HT × (1 − taux de marge du scénario)
Prix Pays-Bas HT      = prix Pays-Bas TTC / 1,21          (prix issus de prix_vente_nl.csv, option C)
Marge brute Pays-Bas  = prix Pays-Bas HT − coût d'achat HT
```

Conséquence de la politique de prix retenue (option C) :

- **produit exclusif** : prix hors taxes identique à la France → taux de marge identique ;
- **produit partagé** : prix aligné sur le concurrent le moins cher (−4,4 % HT en moyenne) → taux de marge plus faible.

**Exemples (scénario central, 44 %)**

| | Fenty Beauty – Gloss Bomb Stix (partagé) | Rhode – Pocket Blush (exclusif) |
|---|---:|---:|
| Prix France HT | 22,50 € | 27,50 € |
| Coût d'achat HT | 12,60 € | 15,40 € |
| Prix Pays-Bas HT | 20,66 € | 27,50 € |
| **Marge brute Pays-Bas** | **8,06 € (39,0 %)** | **12,10 € (44,0 %)** |

## 4. Résultats

Marge brute moyenne par produit aux Pays-Bas (32 produits) :

| Scénario | Produits exclusifs (17) | Produits partagés (15) | Ensemble |
|---|---:|---:|---:|
| Pessimiste | 10,10 € (38,0 %) | 8,50 € (35,1 %) | 9,40 € (36,6 %) |
| Central | 11,70 € (44,0 %) | 10,00 € (41,4 %) | 10,90 € (42,8 %) |
| Optimiste | 12,80 € (48,0 %) | 11,00 € (45,6 %) | 11,90 € (46,9 %) |

Le détail par produit figure dans `marges_nl.csv`.

**Description des colonnes de `marges_nl.csv`** (une ligne par produit)

| Colonne | Description |
|---|---|
| `product_id` … `is_verified_exclusive` | Identification du produit (voir `products_prices.csv`) |
| `price_sephora_fr_ttc`, `price_sephora_fr_ht` | Prix France, TTC et HT (HT = TTC / 1,20) |
| `price_sephora_nl_ttc`, `price_sephora_nl_ht` | Prix de vente Pays-Bas, TTC et HT (HT = TTC / 1,21) |
| `cout_achat_<scénario>_eur` | Coût d'achat estimé = prix France HT × (1 − taux du scénario) |
| `marge_<scénario>_eur` | Marge brute par unité vendue aux Pays-Bas = prix Pays-Bas HT − coût d'achat |
| `marge_<scénario>_pct` | Taux de marge brute aux Pays-Bas = marge en € / prix Pays-Bas HT |

`<scénario>` = `pessimiste` (38 %), `central` (44 %) ou `optimiste` (48 %).

## 5. Hypothèses et limites

| Hypothèse | Limite |
|---|---|
| Taux de marge de Sephora assimilé à celui de distributeurs comparables | Marge réelle de Sephora non publiée |
| Taux identique pour toutes les marques d'un même scénario | En pratique, la marge varie selon la marque (plus élevée sur Sephora Collection) |
| Coût d'achat identique en France et aux Pays-Bas | Les conditions fournisseurs peuvent différer selon les volumes |
| Prix hors promotions | Les promotions réduiraient la marge réelle |
| P04 (Liquid Matte Mousse) inclus | Retiré lors du nettoyage du modèle (aucun avis client) |

## 6. Sources

- Douglas Group, rapport intermédiaire T1 2024/25 (marge brute 43,6 %) : https://douglas.group/en/newsroom/press-releases/douglas-group-starts-with-solid-growth-into-financial-year-202425
- Douglas Group, rapport intermédiaire 9M 2024/25 : https://douglas.group/fileadmin/user_upload/9M_FY_2024_2025_-_Interim_Statement.pdf
- Ulta Beauty, résultats du 4e trimestre et de l'exercice 2025 (marge brute 39,1 %) : https://www.ulta.com/investor/news-events/press-releases/detail/224
- Prix de vente Pays-Bas : `data/previsions/prix_vente_nl.csv`
- Prix France et exclusivités : `data/raw/products_prices.csv`
