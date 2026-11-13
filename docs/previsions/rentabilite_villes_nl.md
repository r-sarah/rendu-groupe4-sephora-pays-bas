# Rentabilité prévisionnelle d'un magasin Sephora Maquillage aux Pays-Bas (2027-2029)

> Projet Sephora (LVMH) – Étude d'implantation aux Pays-Bas.
> Données : `rentabilite_villes_nl.csv` (4 villes × 3 scénarios × 3 années = 36 lignes). Calcul réalisé le 13 novembre 2026.

Un magasin Sephora de 270 m² consacré uniquement au maquillage, implanté dans la rue commerçante la plus chère de chacune des quatre villes de la Randstad, **n'est rentable dans aucune ville ni aucun scénario** sur la période 2027-2029. En 2029, le résultat annuel varie de **−0,23 M€** (La Haye, scénario optimiste) à **−1,09 M€** (Amsterdam, scénario pessimiste). Le point mort supposerait une part de marché de **9 % à 26 %** du marché du maquillage de la ville, hors de portée d'un magasin unique.

## Sommaire

1. [Périmètre](#1-périmètre)
2. [Hypothèses](#2-hypothèses)
3. [Méthode de calcul](#3-méthode-de-calcul)
4. [Résultats](#4-résultats)
5. [Conclusion et recommandations](#5-conclusion-et-recommandations)
6. [Description des colonnes](#6-description-des-colonnes)
7. [Limites](#7-limites)
8. [Sources](#8-sources)

---

## 1. Périmètre

- **Un magasin par ville** : Amsterdam, Rotterdam, Utrecht, La Haye.
- **Catégorie** : maquillage uniquement.
- **Période** : 2027 (ouverture), 2028, 2029.
- **Résultat calculé** : marge brute − loyer − personnel − transport. Les autres charges (énergie, marketing, frais de siège) ne sont pas incluses : le résultat réel serait donc inférieur.

## 2. Hypothèses

| Hypothèse | Pessimiste | Central | Optimiste | Source |
|---|---:|---:|---:|---|
| Marché du maquillage aux Pays-Bas | 510,9 M€ | 510,9 M€ | 510,9 M€ | Étude « Taille du marché » (NCV, 2025) |
| Population des Pays-Bas | 18 130 206 | 18 130 206 | 18 130 206 | CBS, 1er janvier 2026 |
| Surface du magasin | 270 m² | 270 m² | 270 m² | Premier magasin Sephora en Belgique (Docks Bruxsel, 2026) |
| Part de marché visée dans la ville (2029) | 1,5 % | 3 % | 5 % | Référence : un magasin Douglas ou ICI Paris XL ≈ 1,4 % |
| Montée en charge 2027 / 2028 / 2029 | 60 / 85 / 100 % | 60 / 85 / 100 % | 60 / 85 / 100 % | Hypothèse |
| Taux de marge brute | 36,6 % | 42,8 % | 46,9 % | `marges_nl.csv` |
| Loyer | Loyer prime de la ville | Loyer prime de la ville | Loyer prime de la ville | `market_cities_nl.csv` |
| Personnel (équivalents temps plein) | 7 | 6 | 5 | Hypothèse |
| Salaire brut mensuel | 2 750 € | 2 750 € | 2 750 € | Convention collective Retail Non-Food 2026 (2 468 € à 3 061 €) |
| Pécule de vacances | 8 % | 8 % | 8 % | Convention collective Retail Non-Food |
| Charges patronales | 35 % | 30 % | 25 % | Fourchette publiée : 20 % à 35 % du brut |
| Coût du transport | 2,0 €/km | 1,8 €/km | 1,6 €/km | Upply : 1,63 €/km (France, nov. 2025) |
| Fréquence de livraison | 1 / semaine | 1 / semaine | 1 / semaine | Hypothèse |
| Entrepôt | Saran (Loiret) | Saran (Loiret) | Saran (Loiret) | Siège de la Supply Chain Europe de Sephora |
| Coût d'ouverture | 1 200 €/m² | 1 000 €/m² | 800 €/m² | EHI : 590 €/m² (textile) à 961 €/m² (alimentaire) en 2025 |

**Loyer prime par ville** (rue commerçante la plus chère) :

| Ville | Rue | €/m²/an | Loyer annuel (270 m²) |
|---|---|---:|---:|
| Amsterdam | Kalverstraat | 3 000 | 810 000 € |
| Rotterdam | Lijnbaan | 1 650 | 445 500 € |
| Utrecht | Lange Elisabethstraat | 1 600 | 432 000 € |
| La Haye | Spuistraat | 1 000 | 270 000 € |

## 3. Méthode de calcul

```text
Marché maquillage de la ville = 510,9 M€ × population de la ville / 18 130 206
Part de marché de l'année     = part visée du scénario × montée en charge de l'année
CA TTC                        = marché de la ville × part de marché de l'année
CA HT                         = CA TTC / 1,21
Marge brute                   = CA HT × taux de marge du scénario
Loyer                         = 270 m² × loyer prime de la ville
Personnel                     = ETP × 2 750 € × 12 × 1,08 × (1 + charges patronales)
Transport                     = distance Saran → ville (km) × coût au km × 52 livraisons
Résultat annuel               = marge brute − loyer − personnel − transport
Coût d'ouverture              = 270 m² × coût d'aménagement au m² (dépensé en 2027)
Résultat cumulé               = − coût d'ouverture + somme des résultats annuels
CA HT au point mort           = (loyer + personnel + transport) / taux de marge
Part de marché au point mort  = CA HT au point mort × 1,21 / marché de la ville
```

**Exemple : La Haye, scénario central**

| | 2027 | 2028 | 2029 |
|---|---:|---:|---:|
| Part de marché | 1,80 % | 2,55 % | 3,00 % |
| CA HT | 238 720 € | 338 187 € | 397 867 € |
| Marge brute (42,8 %) | 102 172 € | 144 744 € | 170 287 € |
| Loyer | −270 000 € | −270 000 € | −270 000 € |
| Personnel | −277 992 € | −277 992 € | −277 992 € |
| Transport | −55 411 € | −55 411 € | −55 411 € |
| **Résultat annuel** | **−501 231 €** | **−458 659 €** | **−433 116 €** |
| Résultat cumulé (après ouverture de 270 000 €) | −771 231 € | −1 229 890 € | −1 663 006 € |

## 4. Résultats

**Résultat annuel en 2029**

| Ville | Pessimiste | Central | Optimiste |
|---|---:|---:|---:|
| Amsterdam | −1,09 M€ | −0,86 M€ | −0,57 M€ |
| Rotterdam | −0,75 M€ | −0,57 M€ | −0,35 M€ |
| Utrecht | −0,78 M€ | −0,65 M€ | −0,50 M€ |
| La Haye | −0,60 M€ | −0,43 M€ | −0,23 M€ |

**Résultat cumulé 2027-2029 (coût d'ouverture inclus)**

| Ville | Pessimiste | Central | Optimiste |
|---|---:|---:|---:|
| Amsterdam | −3,66 M€ | −3,02 M€ | −2,21 M€ |
| Rotterdam | −2,64 M€ | −2,10 M€ | −1,46 M€ |
| Utrecht | −2,70 M€ | −2,29 M€ | −1,82 M€ |
| La Haye | −2,15 M€ | −1,66 M€ | −1,08 M€ |

**Part de marché nécessaire pour atteindre le point mort**

| Ville | Pessimiste | Central | Optimiste |
|---|---:|---:|---:|
| Amsterdam | 15,1 % | 12,2 % | 10,5 % |
| Rotterdam | 14,6 % | 11,6 % | 9,7 % |
| Utrecht | 25,8 % | 20,3 % | 17,1 % |
| La Haye | 13,8 % | 10,6 % | 8,7 % |

À titre de comparaison, l'ensemble des magasins Douglas et ICI Paris XL représente environ 21 % des ventes de cosmétiques en magasins physiques aux Pays-Bas (voir `parts_de_marche_douglas_ici_NL.md`).

## 5. Conclusion et recommandations

**Conclusion : No-Go pour un magasin 100 % maquillage en rue commerçante prime.** La marge brute dégagée par le seul maquillage (0,05 à 0,51 M€ par an selon la ville et le scénario) ne couvre pas les charges fixes d'un magasin : loyer (0,27 à 0,81 M€) et personnel (0,22 à 0,34 M€).

**Recommandations pour une entrée rentable :**

1. **Réduire les charges fixes** : démarrer par des **pop-up** ou un emplacement en **centre commercial**, comme Sephora l'a fait en Belgique (Docks Bruxsel, City2). Sans le loyer d'une rue prime, le magasin de La Haye (scénario optimiste) dégagerait environ +40 000 € par an.
2. **Élargir l'offre au soin, sans le parfum** :
   - le **parfum** est le point fort de Douglas et ICI Paris XL, et ce segment a reculé en 2025 (−2,2 %), principalement en parfumerie ;
   - le **soin** représente un marché de taille comparable au maquillage (environ 550 M€ en 2023) ;
   - estimation indicative, en supposant pour le soin la même part de marché et la même marge que pour le maquillage : en 2029, avec les loyers prime, le résultat deviendrait positif à La Haye (≈ +80 000 €) et à Rotterdam (≈ +21 000 €) dans le scénario optimiste, mais resterait négatif dans le scénario central (La Haye ≈ −263 000 €).
3. **Combiner les deux leviers** (maquillage + soin, emplacement à loyer réduit) : c'est la seule configuration étudiée qui ouvre une perspective de rentabilité.

## 6. Description des colonnes

| Colonne | Description | Unité |
|---|---|---|
| `city_id`, `ville` | Ville (clé commune avec `market_cities_nl.csv`) | – |
| `scenario` | Pessimiste / Central / Optimiste | – |
| `annee` | 2027, 2028 ou 2029 | – |
| `marche_maquillage_ville_eur` | Marché du maquillage de la ville (prorata de la population) | € TTC |
| `part_de_marche_visee_pct` | Part de marché de l'année (part visée × montée en charge) | % |
| `ca_ttc_eur`, `ca_ht_eur` | Chiffre d'affaires du magasin | € |
| `taux_marge_pct` | Taux de marge brute du scénario | % |
| `marge_brute_eur` | Marge brute annuelle | € |
| `loyer_eur` | Loyer annuel | € |
| `personnel_eur` | Coût annuel du personnel (charges et pécule de vacances inclus) | € |
| `transport_eur` | Coût annuel du transport depuis Saran | € |
| `resultat_annuel_eur` | Marge brute − loyer − personnel − transport | € |
| `cout_ouverture_eur` | Coût d'aménagement du magasin (dépensé en 2027) | € |
| `resultat_cumule_eur` | Résultat cumulé depuis l'ouverture, coût d'ouverture inclus | € |
| `ca_ht_point_mort_eur` | Chiffre d'affaires HT nécessaire pour couvrir loyer, personnel et transport | € |
| `part_de_marche_point_mort_pct` | Part de marché correspondant au point mort | % |
| `rentable` | 1 si le résultat annuel est positif, sinon 0 | – |

## 7. Limites

| Hypothèse | Limite |
|---|---|
| Loyer prime (rue la plus chère) | Cas le plus coûteux ; un centre commercial ou une rue secondaire réduirait fortement le loyer |
| Marché de la ville au prorata de la population | Ne tient pas compte du pouvoir d'achat ni du tourisme (favorable à Amsterdam) |
| Marché constant (510,9 M€) sur 2027-2029 | Croissance de +6,5 %/an sur 2019-2024, mais −0,8 % en 2025 |
| Charges limitées au loyer, au personnel et au transport | Énergie, marketing et frais de siège non inclus : résultat réel inférieur |
| Livraison hebdomadaire dédiée depuis Saran | Une tournée mutualisée entre plusieurs magasins réduirait le coût |
| Parts de marché visées | Hypothèses, calées sur la part moyenne d'un magasin Douglas ou ICI Paris XL |
| Tout le personnel rémunéré au salaire d'un vendeur | Le responsable de magasin étant mieux payé, le coût du personnel est légèrement sous-estimé (≈ +17 000 €/an pour +1 000 € brut/mois) |
| Transport compté sur le trajet aller uniquement | Le retour du camion n'est pas compté : le coût du transport est légèrement sous-estimé (≈ +47 000 à 65 000 €/an en aller-retour) |

Ces deux simplifications sous-estiment les coûts : le résultat réel serait légèrement inférieur aux valeurs présentées, ce qui renforce la conclusion.

## 8. Sources

- CBS, population des Pays-Bas au 1er janvier 2026 : https://www.cbs.nl/nl-nl/cijfers/detail/83474NED
- Taille du marché du maquillage : `taille_marche_maquillage_NL.md` (NCV)
- Parts de marché : `parts_de_marche_douglas_ici_NL.md`
- Marges : `marges_nl.md`
- Loyers, population des villes, distances : `data/raw/villes/market_cities_nl.csv`
- Surface du magasin : RetailDetail, « Sephora fera ses débuts en Belgique à Docks Bruxsel et City2 » : https://www.retaildetail.be/fr/news/beaute-soins/sephora-fait-ses-debuts-en-belgique-a-docks-bruxsel-et-city2/
- Salaires : convention collective Retail Non-Food 2026, via Salaristabel : https://salaristabel.nl/salaris/verkoopmedewerker
- Charges patronales : De Zaak, « Werkgeverslasten » : https://www.dezaak.nl/financien/payroll-en-salarisadministratie/werkgeverslasten-2027-aof-premie-en-wkr-omhoog-auto-van-de-zaak-duurder/
- Coût du transport : Upply, baromètre du transport routier, novembre 2025 : https://market-insights.upply.com/hubfs/barometres-upply/2025/Baro-route-novembre/barometre-route-novembre-2025.pdf
- Coût d'aménagement : EHI Store Monitor 2026, via Formwerk : https://www.formwerk.com/en/retail-hub/ladeneinrichtung-einzelhandel
- Entrepôt de Saran : offre d'emploi Sephora « Supply Chain Europe » : https://www.jobteaser.com/fr/job-offers/8d558cba-9196-4c23-b98a-bf313fa42979-sephora-alternance-assistant-methodes-logistiques-supply-chain-europe-f-h-x
- Parfum et parfumeries en 2025 : Tophair (données NCV) : https://tophair.nl/31075-2/
- Taille du marché du soin : Statista : https://statista.com/statistics/452284/cosmetics-sales-value-in-the-netherlands
