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
`merge.py` récupère les données ajoutées manuellement depuis `data/manual/`,
les combine avec les données raw, construis les cartes challenges et régénère
`CREDITS.md` à partir des métadonnées déclarées par chaque script.

Produit les 101 départements, les 9 collectivités et les 18 régions.

> Les fichiers de `data/downloads/` et `data/raw/` sont générés : ne pas les
> éditer. Les données saisies à la main vivent dans `data/manual/`.

## 3. Construire les cartes spatiales

## 4. Générer les cartes

```bash
just print

# when developping
just watch departments
just watch com
```

`--root .` est nécessaire : sans lui, Typst refuse de lire `/data/`.
