// Geometry and typography, shared by every deck.

#let card-width = 63mm
#let card-height = 88mm
#let gutter = 3mm
#let grid-columns = 3
#let grid-rows = 3

// Centre the grid on the sheet; the leftover is the page margin.
#let page-margin = (
  x: (210mm - grid-columns * card-width - (grid-columns - 1) * gutter) / 2,
  y: (297mm - grid-rows * card-height - (grid-rows - 1) * gutter) / 2,
)

#let muted = luma(110)
#let cut-line = 0.25pt + luma(180)

#let base-text = (font: "Libertinus Serif", size: 9pt)
