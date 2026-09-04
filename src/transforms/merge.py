# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

from pathlib import Path

from challenges import build_challenges
from yaml_io import read_yaml, write_yaml

RAW_DIR = Path("data/raw")
MANUAL_DIR = Path("data/manual")
DATA_DIR = Path("data")
CREDITS = Path("CREDITS.md")


def main() -> None:
    raw = load_dir(RAW_DIR)
    manual = load_dir(MANUAL_DIR)
    report_manual(manual)

    regions = build_regions(raw)
    departments = build_departments(raw, manual, region_slugs(regions))
    com = build_com(raw, manual)
    apply_status(departments + com, manual["statuts"])
    apply_elements(departments + com, manual["elements"])
    challenges = build_challenges(manual["challenges"], collections(regions, manual))

    write_yaml(departments, DATA_DIR / "departements.yaml")
    write_yaml(com, DATA_DIR / "com.yaml")
    write_yaml(regions, DATA_DIR / "regions.yaml")
    write_yaml(challenges, DATA_DIR / "challenges.yaml")
    write_yaml(manual["statuts"]["statuts"], DATA_DIR / "statuts.yaml")
    write_credits(collect_sources(raw, manual))

    print(f"{len(departments)} départements, "
          f"{len(com)} collectivités et territoires d'Outre Mer, "
          f"{len(regions)} régions, {len(challenges)} défis -> {DATA_DIR}")


def report_manual(manual: dict) -> None:
    drom = manual["drom"]
    com = manual["com"]
    statuts = manual["statuts"]["attribution"]
    families = {
        name: items
        for name, items in manual["elements"].items()
        if name != "sources"
    }

    elements = sum(len(items) for items in families.values())
    department_links = sum(
        len(item["departements"])
        for items in families.values()
        for item in items
    )
    com_links = sum(
        len(item["com"])
        for items in families.values()
        for item in items
    )

    print("Données manuelles chargées :")
    print(
        f"  DROM : {len(drom['population'])} populations, "
        f"{len(drom['superficie_km2'])} superficies"
    )
    print(
        f"  COM : {len(com['chef_lieu'])} chefs-lieux, "
        f"{len(com['chef_lieu_type'])} types de chef-lieu, "
        f"{len(com['population'])} populations, "
        f"{len(com['superficie_km2'])} superficies"
    )
    print(
        f"  statuts : {len(statuts) - 1} attributions explicites, "
        f"défaut {statuts['_defaut']!r}"
    )
    print(
        f"  éléments : {elements} définitions, "
        f"{department_links} rattachements département, "
        f"{com_links} rattachements COM"
    )
    print(f"  défis : {len(manual['challenges'])} modèles")


def build_departments(raw: dict, manual: dict, slugs: dict[str, str]) -> list[dict]:
    fields = [
        ("population", raw, "population", "population", "insee-pop"),
        ("superficie_km2", raw, "area", "superficie_km2", "communes-france"),
        ("superficie_km2", manual, "drom", "superficie_km2", "insee-superficie"),
        ("population", manual, "drom", "population", "insee-mayotte"),
    ]

    departments = []
    for entry in raw["cog"]["departements"]:
        department = apply_fields(entry, fields)
        department["region"] = slugs[entry["region"]]
        departments.append(department)
    return departments


def build_com(raw: dict, manual: dict) -> list[dict]:
    fields = [
        ("chef_lieu", manual, "com", "chef_lieu", "insee-com"),
        ("chef_lieu_type", manual, "com", "chef_lieu_type", "insee-com"),
        ("population", manual, "com", "population", "insee-com"),
        ("superficie_km2", manual, "com", "superficie_km2", "insee-com"),
    ]
    return [apply_fields(entry, fields) for entry in raw["cog"]["com"]]


def apply_status(territories: list[dict], statuts: dict) -> None:
    attribution = statuts["attribution"]
    default = attribution["_defaut"]
    known = set(statuts["statuts"])

    for territory in territories:
        status = attribution.get(territory["code"], default)
        if status not in known:
            raise ValueError(f"{territory['code']}: unknown status {status!r}")
        territory["statut"] = status
        territory["sources"]["statut"] = "statuts"


def apply_fields(entry: dict, fields: list[tuple]) -> dict:
    # Later fields override earlier ones targeting the same name.
    result = dict(entry)
    for name, store, block, key, source in fields:
        value = lookup(store, block, key, entry["code"])
        if value is not None:
            result[name] = value
            result["sources"][name] = source
    return result


def lookup(store: dict, block: str, key: str, code: str) -> object | None:
    entry = store[block][key].get(code)
    # Manual entries wrap the value alongside its own source URL.
    if isinstance(entry, dict):
        return entry.get("valeur")
    return entry


def apply_elements(departments: list[dict], elements: dict) -> None:
    by_code = {d["code"]: d for d in departments}
    families = {k: v for k, v in elements.items() if k != "sources"}
    validate_elements(families, set(by_code))

    for family, items in families.items():
        for item in items:
            for code in item["departements"]:
                department = by_code[code]
                department.setdefault(family, []).append(item["slug"])
                department["sources"][family] = "elements"


def validate_elements(families: dict[str, list[dict]], known: set[str]) -> None:
    unknown = sorted(
        f"{family}/{item['slug']}: {code}"
        for family, items in families.items()
        for item in items
        for code in item["departements"]
        if code not in known
    )
    if unknown:
        raise ValueError("unknown department codes:\n  " + "\n  ".join(unknown))


def build_regions(raw: dict) -> list[dict]:
    return [dict(entry) for entry in raw["cog"]["regions"]]


def region_slugs(regions: list[dict]) -> dict[str, str]:
    return {region["code"]: region["slug"] for region in regions}


def collections(regions: list[dict], manual: dict) -> dict[str, list[dict]]:
    # Challenge templates expand over regions and over every element family.
    families = {
        name: items
        for name, items in manual["elements"].items()
        if name != "sources"
    }
    return {"regions": regions, **families}


def load_dir(directory: Path) -> dict:
    if not directory.exists():
        return {}
    return {path.stem: read_yaml(path) for path in sorted(directory.glob("*.yaml"))}


def collect_sources(raw: dict, manual: dict) -> list[dict]:
    blocks = [b for b in list(raw.values()) + list(manual.values()) if isinstance(b, dict)]

    sources = []
    for block in blocks:
        if "source" in block:
            sources.append(dict(block["source"], details=entry_urls(block)))
        # Plural form: one source per field, so only that field carries details.
        for field, source in block.get("sources", {}).items():
            sources.append(
                dict(source, details=entry_urls({field: block.get(field, {})}))
            )

    return sorted(sources, key=lambda s: s["publisher"])


def entry_urls(block: dict) -> list[tuple[str, str]]:
    # Manual files carry one URL per entry alongside its value.
    return sorted(
        (code, entry["url"])
        for values in block.values()
        if isinstance(values, dict)
        for code, entry in values.items()
        if isinstance(entry, dict) and "url" in entry
    )


def write_credits(sources: list[dict]) -> None:
    lines = ["# Crédits", "", "Ce fichier est généré par `merge.py`.", ""]
    lines += ["## Sources", ""]
    lines += ["| Source | Producteur | Millésime | Licence |", "|---|---|---|---|"]
    lines += [
        f"| {link(s)} | {s['publisher']} | {s.get('vintage', '—')} | {s['license']} |"
        for s in sources
    ]

    for source in sources:
        if source["details"]:
            entries = " · ".join(f"[{code}]({url})" for code, url in source["details"])
            lines += ["", f"Détail — {source['name']} : {entries}"]

    documented = [s for s in sources if s.get("note") or s.get("convention")]
    if documented:
        lines += ["", "## Conventions", ""]
        lines += [
            "Les sources ci-dessus recensent les éléments géographiques mais ne",
            "définissent pas leur rattachement aux départements. Les règles",
            "suivantes relèvent d'un choix éditorial.",
        ]
        for source in documented:
            lines += ["", f"### {source['name']}", ""]
            if source.get("note"):
                lines += [f"**Sélection** — {source['note'].strip()}", ""]
            if source.get("convention"):
                lines += [f"**Rattachement** — {source['convention'].strip()}"]

    lines += [""]
    CREDITS.write_text("\n".join(lines), encoding="utf-8")


def link(source: dict) -> str:
    url = source.get("url")
    return f"[{source['name']}]({url})" if url else source["name"]


if __name__ == "__main__":
    main()
