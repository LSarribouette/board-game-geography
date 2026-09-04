// Challenge decks, one per scale.

#import "sheet.typ": deck
#import "card.typ": challenge-card

#let challenge-deck(scale) = {
  let challenges = yaml("/data/challenges.yaml")
  deck(challenges.filter(c => c.echelle == scale).map(challenge-card))
}
