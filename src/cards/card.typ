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
    [Population : #format-number(dept.population) habitants],
    [Superficie : #format-number(dept.superficie_km2) km#super[2]],
  )
  #scale-marker(scale-labels.departement)
]

#let com-card(com, statut-name) = block(
  width: card-width,
  height: card-height,
  stroke: cut-line,
  inset: 5mm,
)[
  #set align(center)
  #text(size: 15pt, weight: "bold")[#com.code #com.nom]
  #v(1mm)
  #text(size: 9pt, fill: muted)[#statut-name]
  #v(4mm)
  #set align(left)
  #set text(size: 8pt)
  #list(
    ..if "chef_lieu" in com {
      let label = if com.at("chef_lieu_type", default: none) == "siege" {
        "Siège"
      } else {
        "Chef-lieu"
      }
      ([#label : #com.chef_lieu],)
    } else { () },
    ..if "population" in com {
      if com.population == 0 {
        ([Population : inhabitée],)
      } else {
        ([Population : #format-number(com.population) habitants],)
      }
    } else { () },
    ..if "superficie_km2" in com {
      ([Superficie : #format-number(com.superficie_km2) km#super[2]],)
    } else { () },
  )
  #scale-marker(scale-labels.com)
]

#let challenge-card(challenge) = block(
  width: card-width,
  height: card-height,
  stroke: cut-line,
  inset: 5mm,
)[
  #set align(center + horizon)
  #if challenge.titre != none [
    #text(size: 16pt, weight: "bold")[#challenge.titre]
    #v(3mm)
  ]
  #text(size: 11pt)[#challenge.consigne]
  #scale-marker(scale-labels.at(challenge.echelle, default: challenge.echelle))
]
