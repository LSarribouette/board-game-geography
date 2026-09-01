// Region deck — front side. 18 cards.

#import "sheet.typ": deck
#import "card.typ": region-card

#let cog = yaml("/data/raw/cog.yaml")

#deck(cog.regions.map(region-card))
