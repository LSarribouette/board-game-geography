# Génération des données

## Prérequis

- [uv](https://docs.astral.sh/uv/)

Les dépendances sont déclarées dans chaque script (PEP 723) : uv les installe
à la volée, rien à préparer.

## 1. Télécharger le COG

Le script ne télécharge rien lui-même : les URL de l'INSEE contiennent un
identifiant qui change à chaque millésime.

```sh
mkdir -p data/downloads/cog
curl -L -o data/downloads/cog/cog_2026.zip "https://www.insee.fr/fr/statistiques/fichier/8740222/cog_ensemble_2026_csv.zip"
unzip -o data/downloads/cog/cog_2026.zip -d data/downloads/cog
```

Pour un autre millésime, prendre l'URL sur
<https://www.insee.fr/fr/information/2560452>.

## 2. Construire les données

```sh
uv run src/data/fetch_cog.py    # -> data/raw/cog.yaml
```

Produit les 101 départements (code, nom, statut, région, préfecture) et les
18 régions (code, nom, chef-lieu).

Les fichiers de `data/raw/` sont générés : ne pas les éditer.

## 3. Générer les cartes

```sh
typst compile --root . src/cards/departments.typ print/cards-departments.pdf
typst compile --root . src/cards/regions.typ     print/cards-regions.pdf
```

`--root .` est nécessaire : sans lui, Typst refuse de lire `/data/`.

Sortie : 12 pages A4, 9 cartes par page, 101 cartes département.

- `main.typ` — feuille, grille, chargement des données
- `card.typ` — mise en page d'une carte
- `theme.typ` — géométrie et typographie

## Impression

Papier ordinaire, recto simple, **100 % sans ajustement à la page** — sinon les
63 mm n'en font plus 63. Découper au massicot en suivant les bordures grises.
Les deux faces se montent à la main dans un sleeve 63 × 88 mm.

Si la première colonne est rognée, l'imprimante a une zone non imprimable plus
large que la marge calculée : réduire `gutter` dans `theme.typ`.