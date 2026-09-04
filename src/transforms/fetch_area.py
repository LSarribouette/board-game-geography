# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from yaml_io import write_yaml

SOURCE_KEY = "communes-france"
SOURCE_META = {
    "name": "Communes et villes de France",
    "publisher": "Ville de rêve",
    "url": "https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather",
    "license": "Licence Ouverte 2.0",
    "vintage": "2026",
    "note": "Agrégat INSEE + IGN ADMIN-EXPRESS. Superficie cartographique. Mayotte absente.",
}

INPUT = Path("data/downloads/area/communes-france.csv")
OUTPUT = Path("data/raw/area.yaml")

DEPARTMENT_CODE = "dep_code"
AREA = "superficie_km2"
COMMUNE_TYPE = "typecom"


def main() -> None:
    areas = sum_by_department(read_communes())

    write_yaml({"source": SOURCE_META, "superficie_km2": areas}, OUTPUT)
    print(f"{len(areas)} départements -> {OUTPUT}")


def sum_by_department(rows: list[dict]) -> dict[str, int]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        area = row[AREA].strip()
        if area:
            totals[row[DEPARTMENT_CODE]] += float(area)

    return {code: round(total) for code, total in sorted(totals.items())}


def read_communes() -> list[dict]:
    # Only actual communes: ARM, COMA and COMD would be counted twice.
    with INPUT.open(encoding="utf-8") as handle:
        return [
            row
            for row in csv.DictReader(handle)
            if row[COMMUNE_TYPE] == "COM"
        ]


if __name__ == "__main__":
    main()
