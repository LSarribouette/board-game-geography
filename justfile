# List available recipes
default:
    @just --list

# Download data sources
download:
    mkdir -p data/downloads/cog
    curl -L -o data/downloads/cog/cog_2026.zip "https://www.insee.fr/fr/statistiques/fichier/8740222/cog_ensemble_2026_csv.zip"
    unzip -o data/downloads/cog/cog_2026.zip -d data/downloads/cog

    mkdir -p data/downloads/population
    curl -L -o data/downloads/population/ensemble.zip "https://www.insee.fr/fr/statistiques/fichier/8680726/ensemble.zip"
    unzip -o data/downloads/population/ensemble.zip -d data/downloads/population

    mkdir -p data/downloads/area
    curl -L -o data/downloads/area/communes-france.csv "https://www.data.gouv.fr/api/1/datasets/r/c63fd0b1-7987-46f6-b779-8b3ed889090c"

# Build raw data and merge it in data/ 
build:
    uv run src/transforms/fetch_cog.py
    uv run src/transforms/fetch_population.py
    uv run src/transforms/fetch_area.py
    uv run src/transforms/merge.py

# Compile cards to print/
print:
    typst compile --root . src/cards/departments.typ print/cards-departments.pdf
    typst compile --root . src/cards/regions.typ     print/cards-regions.pdf

# Recompile a deck on change (deck: departments | regions)
watch deck:
    typst watch --root . src/cards/{{deck}}.typ print/cards-{{deck}}.pdf
