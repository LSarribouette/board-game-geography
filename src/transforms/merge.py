# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

from pathlib import Path

from yaml_io import read_yaml, write_yaml

RAW_DIR = Path("data/raw")
MANUAL_DIR = Path("data/manual")
DATA_DIR = Path("data")
CREDITS = Path("CREDITS.md")


def main() -> None:
    raw = load_dir(RAW_DIR)
    manual = load_dir(MANUAL_DIR)

    regions = build_regions(raw)
    departments = build_departments(raw, manual, region_slugs(regions))

    write_yaml(departments, DATA_DIR / "departements.yaml")
    write_yaml(regions, DATA_DIR / "regions.yaml")
    write_credits(collect_sources(raw, manual))

    print(f"{len(departments)} départements, {len(regions)} régions -> {DATA_DIR}")


def build_departments(raw: dict, manual: dict, slugs: dict[str, str]) -> list[dict]:
    # Later entries override earlier ones for the same field.
    fields = [
        ("population", raw, "population", "population", "insee-pop"),
        ("superficie_km2", raw, "area", "superficie_km2", "communes-france"),
        ("superficie_km2", manual, "superficie", "superficie_km2", "insee-superficie"),
    ]

    departments = []
    for entry in raw["cog"]["departements"]:
        department = dict(entry)
        department["region"] = slugs[entry["region"]]

        for name, store, block, key, source in fields:
            value = lookup(store, block, key, entry["code"])
            if value is not None:
                department[name] = value
                department["sources"][name] = source

        departments.append(department)
    return departments


def lookup(store: dict, block: str, key: str, code: str) -> object | None:
    entry = store.get(block, {}).get(key, {}).get(code)
    # Manual entries wrap the value alongside its own source URL.
    if isinstance(entry, dict):
        return entry.get("valeur")
    return entry


def build_regions(raw: dict) -> list[dict]:
    return [dict(entry) for entry in raw["cog"]["regions"]]


def region_slugs(regions: list[dict]) -> dict[str, str]:
    return {region["code"]: region["slug"] for region in regions}


def load_dir(directory: Path) -> dict:
    if not directory.exists():
        return {}
    return {path.stem: read_yaml(path) for path in sorted(directory.glob("*.yaml"))}


def collect_sources(raw: dict, manual: dict) -> list[dict]:
    blocks = list(raw.values()) + list(manual.values())
    sources = [
        dict(block["source"], details=entry_urls(block))
        for block in blocks
        if "source" in block
    ]
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
    lines = [
        "# Crédits",
        "",
        "Ce projet réutilise des données publiques. Chaque source est citée",
        "conformément à sa licence. Ce fichier est généré par `merge.py`.",
        "",
        "| Source | Producteur | Millésime | Licence |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {link(s)} | {s['publisher']} | {s.get('vintage', '—')} | {s['license']} |"
        for s in sources
    ]

    for source in sources:
        if source["details"]:
            lines += ["", f"### {source['name']}", ""]
            lines += [f"- {code} : <{url}>" for code, url in source["details"]]

    lines += [""]
    CREDITS.write_text("\n".join(lines), encoding="utf-8")


def link(source: dict) -> str:
    url = source.get("url")
    return f"[{source['name']}]({url})" if url else source["name"]


if __name__ == "__main__":
    main()
