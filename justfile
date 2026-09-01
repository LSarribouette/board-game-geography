# List available recipes
default:
    @just --list

# Compile cards to print/
cards:
    typst compile --root . src/cards/departments.typ print/cards-departments.pdf
    typst compile --root . src/cards/regions.typ     print/cards-regions.pdf

# Recompile cards on change
watch:
    typst watch --root . src/cards/departments.typ print/cards-departments.pdf
    typst watch --root . src/cards/regions.typ     print/cards-regions.pdf
