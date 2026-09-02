// Department deck — front side. 101 cards.

#import "sheet.typ": deck
#import "card.typ": department-card

#let departments = yaml("/data/departements.yaml")
#let regions = yaml("/data/regions.yaml")
#let region-names = regions.fold((:), (acc, r) => acc + ((r.slug): r.nom))

#deck(departments.map(d => department-card(
  d,
  region-names.at(d.region, default: "—"),
)))
