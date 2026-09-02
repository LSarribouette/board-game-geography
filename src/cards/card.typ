// Card layouts. One function per card type.

#import "theme.typ": *

#let department-card(dept, region-name) = block(
  width: card-width,
  height: card-height,
  stroke: cut-line,
  inset: 5mm,
)[
  #set align(center)
  #text(size: 15pt, weight: "bold")[#dept.code #dept.nom]
  #v(1mm)
  #text(size: 10pt, fill: muted)[#region-name]
  #v(4mm)
  #set align(left)
  #set text(size: 8pt)
  #list(
    [Préfecture : #dept.prefecture],
    ..if "population" in dept {
      ([Population : #format-number(dept.population) habitants],)
    } else { () },
    ..if "superficie_km2" in dept {
      ([Superficie : #format-number(dept.superficie_km2) km#super[2]],)
    } else { () },
  )
]

#let region-card(region) = block(
  width: card-width,
  height: card-height,
  stroke: cut-line,
  inset: 5mm,
)[
  #set align(center + horizon)
  #text(size: 16pt, weight: "bold")[#region.nom]
]
