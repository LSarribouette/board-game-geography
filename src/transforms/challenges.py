from __future__ import annotations


def build_challenges(templates: list[dict], collections: dict[str, list[dict]]) -> list[dict]:
    cards = []
    for template in templates:
        expanded = expand(template, collections)
        cards += expanded
        print(f"  {template['id']} : {len(expanded)} cartes")
    return cards


def expand(template: dict, collections: dict[str, list[dict]]) -> list[dict]:
    collection = template.get("sur")
    if collection is None:
        return [card(template)]
    
    if collection not in collections:
        available = ", ".join(sorted(collections))
        raise KeyError(f"{template['id']}: unknown collection {collection!r}; available: {available}")
    
    excluded = set(template.get("exclure", ()))
    return [
        card(template, item)
        for item in collections[collection]
        if item["slug"] not in excluded
    ]


def card(template: dict, item: dict | None = None) -> dict:
    return {
        "id": f"{template['id']}-{item['slug']}" if item else template["id"],
        "echelle": template["echelle"],
        "type": template["type"],
        "titre": item["nom"] if item else template.get("titre"),
        "consigne": template["consigne"],
    }
