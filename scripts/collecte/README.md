# Collecte des données produits et prix

Chaîne de collecte de `data/raw/bestsellers_maquillage.csv` et `data/raw/products_prices.csv` (relevé du 12/11/2026).

| Étape | Script | Entrée | Sortie | Nature |
|---|---|---|---|---|
| 1 | `parse_sephora.py` | Texte de la page sephora.fr > Maquillage > Meilleures ventes, copié intégralement (Ctrl+A / Ctrl+C) dans un fichier `.txt` | `bestsellers_maquillage.csv` (168 produits) | Script exécuté |
| 2 | `select_top30.py` | `bestsellers_maquillage.csv` | `products_prices.csv` (30 produits, sans notes ni prix NL) | Script exécuté |
| 3 | `enrich_products.py` | Sortie de l'étape 2 | `products_prices.csv` final (32 produits) | Relevé manuel, consolidé dans un script |

## Étape 1 : extraction des best-sellers

La page des meilleures ventes de sephora.fr a été copiée intégralement puis transformée en tableau par `parse_sephora.py` : marque, nom, type de produit, prix, prix barré, mention « À partir de », nombre d'avis, badge, rang.

```bash
python parse_sephora.py sephora_bestsellers_maquillage_168.txt bestsellers_maquillage.csv 2026-11-12
```

Les notes sur 5 ne figurent pas dans le texte copié (elles sont affichées sous forme d'étoiles) : elles ont été relevées à l'étape 3.

## Étape 2 : sélection de l'échantillon

`select_top30.py` classe les best-sellers en trois segments (Teint, Yeux, Lèvres) et retient les 10 premiers de chaque segment selon le rang sephora.fr. Sont exclus : pinceaux, accessoires, sourcils, ongles, soins des cils, produits multi-zones ambigus, et doublons de format (mini, format voyage, recharge, duo, set).

```bash
python select_top30.py bestsellers_maquillage.csv products_prices.csv
```

## Étape 3 : relevé manuel

Les valeurs suivantes ont été **relevées à la main** le 12/11/2026, puis regroupées dans `enrich_products.py`. Ce script n'a pas servi pendant la collecte : il ne va rien chercher sur internet et permet uniquement de reconstruire le fichier final à l'identique.

- notes sur 5 : pages produit de sephora.fr ;
- prix aux Pays-Bas : douglas.nl (prix conseillé ou affiché, hors promotion) et iciparisxl.nl (prix produit) ; produit absent du site = valeur vide ;
- ajout de 2 produits Rhode (P31, P32), hors échantillon, pour la forte notoriété de la marque auprès des jeunes consommatrices ;
- exclusivité : `is_verified_exclusive = 1` si le produit n'est vendu ni chez Douglas ni chez ICI Paris XL aux Pays-Bas.

```bash
python enrich_products.py products_prices.csv products_prices.csv
```

## Contrôle

Texte brut de la page conservé dans `data/raw/sephora_bestsellers_maquillage_168.txt`.

Les trois étapes, appliquées à ce texte brut, reproduisent exactement `data/raw/bestsellers_maquillage.csv` puis `data/raw/products_prices.csv`.

## Limites

- Échantillon de 32 produits, choisis parmi les meilleures ventes de sephora.fr : panier représentatif des best-sellers, pas du catalogue complet.
- Prix et notes relevés à une date unique (12/11/2026).
- P04 (Liquid Matte Mousse, aucun avis) est retiré lors du nettoyage (couche Silver), ce qui ramène l'échantillon à 31 produits.
