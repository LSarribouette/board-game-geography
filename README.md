# La France en jeu

Jeu de société éducatif à imprimer pour découvrir la géographie française :
départements, régions, reliefs, cours d'eau et cultures locales.

**2 à 6 personnes · dès 8 ans · 30 à 45 minutes**

> Le jeu est en cours de développement : le matériel disponible n'est pas
> encore suffisant pour jouer une partie complète.

## Découvrir le jeu

- [Règles du jeu](rules/game.md)
- [Objectifs pédagogiques](rules/learning-goals.md)
- [Cartes imprimer](print/)

## Générer les cartes

Avec [Typst](https://typst.app/) et [just](https://just.systems/) installés :

```sh
just build
just print
```

Les détails sur les données et la génération sont documentés dans
[`src/README.md`](src/README.md).

## Licences

Le code est distribué sous [licence MIT](LICENSE-CODE). Le contenu du jeu est
distribué sous [licence CC BY-NC-SA 4.0](LICENSE-CONTENT).
