# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

import csv
import unicodedata
from pathlib import Path

import yaml
from yaml_io import write_yaml

SOURCE_KEY = "cog"
SOURCE_META = {
    "name": "Code officiel géographique",
    "publisher": "INSEE",
    "url": "https://www.insee.fr/fr/information/2560452",
    "license": "Licence Ouverte 2.0",
    "vintage": "2026",
}

INPUT_DIR = Path("data/downloads/cog")
OUTPUT = Path("data/raw/cog.yaml")

DEPARTMENT_FILE = "v_departement_2026.csv"
REGION_FILE = "v_region_2026.csv"
COMMUNE_FILE = "v_commune_2026.csv"


def main() -> None:
    communes = index_communes(read_csv(COMMUNE_FILE))
    departments = build_departments(read_csv(DEPARTMENT_FILE), communes)
    regions = build_regions(read_csv(REGION_FILE), communes)

    write_yaml(
        {
            "source": SOURCE_META,
            "departements": departments,
            "regions": regions,
        },
        OUTPUT,
    )
    print(f"{len(departments)} départements, {len(regions)} régions -> {OUTPUT}")


def build_departments(rows: list[dict], communes: dict[str, str]) -> list[dict]:
    """Map COG department rows onto the game's YAML schema."""
    return [
        {
            "code": row["DEP"],
            "slug": slugify(row["LIBELLE"]),
            "nom": row["LIBELLE"],
            "statut": status_of(row["DEP"]),
            "region": row["REG"],
            "prefecture": resolve(communes, row["CHEFLIEU"], row["LIBELLE"]),
            "sources": {"_defaut": SOURCE_KEY},
        }
        for row in sorted(rows, key=lambda r: r["DEP"])
    ]


def build_regions(rows: list[dict], communes: dict[str, str]) -> list[dict]:
    return [
        {
            "code": row["REG"],
            "slug": slugify(row["LIBELLE"]),
            "nom": row["LIBELLE"],
            "chef_lieu": resolve(communes, row["CHEFLIEU"], row["LIBELLE"]),
            "sources": {"_defaut": SOURCE_KEY},
        }
        for row in sorted(rows, key=lambda r: r["REG"])
    ]


def status_of(code: str) -> str:
    """Overseas departments are the five three-digit codes starting with 97."""
    return "drom" if code.startswith("97") else "metropole"


def index_communes(rows: list[dict]) -> dict[str, str]:
    """Map commune code to label, to resolve CHEFLIEU references.

    Filter on TYPECOM: delegated and associated communes share codes with
    actual communes, so an unfiltered index silently overwrites entries.
    """
    return {
        row["COM"]: row["LIBELLE"]
        for row in rows
        if row["TYPECOM"] == "COM"
    }


def resolve(communes: dict[str, str], code: str, context: str) -> str:
    label = communes.get(code)
    if label is None:
        raise KeyError(f"unknown chef-lieu code {code!r} for {context!r}")
    return label


def read_csv(filename: str) -> list[dict]:
    path = INPUT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"{path} — run `just fetch-cog` first")
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def slugify(label: str) -> str:
    """Ain -> ain, Côte-d'Or -> cote-d-or, Île-de-France -> ile-de-france."""
    decomposed = unicodedata.normalize("NFKD", label)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    cleaned = "".join(c if c.isalnum() else "-" for c in ascii_only.lower())
    return "-".join(part for part in cleaned.split("-") if part)


if __name__ == "__main__":
    main()
