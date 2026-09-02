# Génération des données

## Prérequis

- [uv](https://docs.astral.sh/uv/)
- [Typst](https://github.com/typst/typst)

Les dépendances Python sont déclarées dans chaque script (PEP 723) : uv les
installe à la volée, rien à préparer.

## 1. Télécharger les sources

Les scripts ne téléchargent rien eux-mêmes : les URL de l'INSEE contiennent un
identifiant qui change à chaque millésime.

```bash
just download
```

## 2. Construire les données

```bash
just build
```

Chaque `fetch_*` lit une source et écrit un intermédiaire dans `data/raw/`.
`merge.py` les combine, résout les codes en slugs, et régénère `CREDITS.md`
à partir des métadonnées déclarées par chaque script.

Produit les 101 départements et les 18 régions.

> Les fichiers de `data/downloads/` et `data/raw/` sont générés : ne pas les
> éditer. Les données saisies à la main vivent dans `data/manual/`.

## 3. Générer les cartes

```bash
just print

# when developping
just watch regions
just watch departments
```

`--root .` est nécessaire : sans lui, Typst refuse de lire `/data/`.

Sortie : 12 pages A4 pour les départements, 2 pages pour les régions,
9 cartes par page.

- `departments.typ`, `regions.typ` — un paquet, chargement des données
- `sheet.typ` — feuille A4 et grille
- `card.typ` — mise en page d'une carte
- `theme.typ` — géométrie et typographie

## Impression

Papier ordinaire, recto simple, **100 % sans ajustement à la page** — sinon les
63 mm n'en font plus 63. Découper au massicot en suivant les bordures grises.
Les deux faces se montent à la main dans un sleeve 63 × 88 mm.

Si la première colonne est rognée, l'imprimante a une zone non imprimable plus
large que la marge calculée : réduire `gutter` dans `theme.typ`.
