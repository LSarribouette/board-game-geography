// Region deck — front side. 18 cards.

#import "sheet.typ": deck
#import "card.typ": region-card

#deck(yaml("/data/regions.yaml").map(region-card))
