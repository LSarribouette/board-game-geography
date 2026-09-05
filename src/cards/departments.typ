// Department deck — front side. 101 cards.

#import "sheet.typ": deck
#import "card.typ": department-card

#let departments = yaml("/data/cards/departements.yaml")
#let regions = yaml("/data/cards/regions.yaml")
#let region-names = regions.fold((:), (acc, r) => acc + ((r.slug): r.nom))

#deck(departments.map(d => department-card(
  d,
  if d.region == none { "—" } else { region-names.at(d.region, default: "—") },
)))
