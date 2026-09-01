// Sheet layout, shared by every deck.

#import "theme.typ": *

#let deck(cards) = {
  set page(paper: "a4", margin: page-margin)
  set text(..base-text)

  grid(
    columns: (card-width,) * grid-columns,
    rows: card-height,
    column-gutter: gutter,
    row-gutter: gutter,
    ..cards,
  )
}
