// Department deck — front side. 101 cards.

#import "sheet.typ": deck
#import "card.typ": department-card

#let cog = yaml("/data/raw/cog.yaml")
#let region-names = cog.regions.fold((:), (acc, r) => acc + ((r.code): r.nom))

#deck(cog.departements.map(d => department-card(
  d,
  region-names.at(d.region, default: "—"),
)))
