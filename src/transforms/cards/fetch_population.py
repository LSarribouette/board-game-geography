# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

import csv
from pathlib import Path

import yaml
from yaml_io import write_yaml

SOURCE_KEY = "insee-pop"
SOURCE_META = {
    "name": "Populations de référence 2023",
    "publisher": "INSEE",
    "url": "https://www.insee.fr/fr/statistiques/8680726",
    "license": "Licence Ouverte 2.0",
    "vintage": "2023",
    "note": "En vigueur au 01/01/2026. Mayotte et les COM non couverts.",
}

INPUT_DIR = Path("data/downloads/population")
OUTPUT = Path("data/cards/raw/population.yaml")

DEPARTMENT_CODE = "DEP"
POPULATION = "PMUN"


def main() -> None:
    rows = read_department_rows()
    populations = {row[DEPARTMENT_CODE]: to_int(row[POPULATION]) for row in rows}

    write_yaml({"source": SOURCE_META, "population": populations}, OUTPUT)
    print(f"{len(populations)} départements -> {OUTPUT}")


def read_department_rows() -> list[dict]:
    with find_department_file().open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def find_department_file() -> Path:
    # INSEE renames files between vintages, so match rather than hardcode.
    for path in sorted(INPUT_DIR.glob("*.csv")):
        if "dep" in path.name.lower():
            return path
    listing = "\n  ".join(p.name for p in sorted(INPUT_DIR.iterdir()))
    raise FileNotFoundError(f"no department CSV in {INPUT_DIR}; contents:\n  {listing}")


def to_int(value: str) -> int:
    # Guard against thousands separators, including NBSP.
    return int(value.replace(" ", "").replace("\u00a0", ""))


if __name__ == "__main__":
    main()
