// COM deck — front side. 9 cards.

#import "sheet.typ": deck
#import "card.typ": com-card

#let com = yaml("/data/cards/com.yaml")
#let statuts = yaml("/data/cards/statuts.yaml")

#deck(com.map(c => com-card(
  c,
  statuts.at(c.statut).nom,
)))
