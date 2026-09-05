import io
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from shapely.affinity import scale, translate

BASE_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master"
SOURCES = {
    "departements": f"{BASE_URL}/departements.geojson",
    "regions": f"{BASE_URL}/regions.geojson",
}

PLATES = [
    ("departements_blank", "departements", None),
    ("departements_numbers", "departements", "code"),
    ("departements_names", "departements", "nom"),
    ("regions_blank", "regions", None),
    ("regions_names", "regions", "nom"),
]

METROPOLE_CRS = 2154  # RGF93 / Lambert-93
ZOOM_CODES = ["75", "92", "93", "94"]  # Paris and the inner ring
DROM_CRS = {  # one local projected CRS per overseas territory
    "Guadeloupe": 5490,  # RGAF09 / UTM 20N
    "Martinique": 5490,
    "Guyane": 2972,  # RGFG95 / UTM 22N
    "La Réunion": 2975,  # RGR92 / UTM 40S
    "Mayotte": 4471,  # RGM04 / UTM 38S
}

CREDIT = "© IGN – ADMIN EXPRESS (Licence Ouverte 2.0), via france-geojson"
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/transforms/maps/ -> project root
OUTPUT_DIR = PROJECT_ROOT / "data" / "maps"
STROKE_WIDTH = 1_200  # projected units (metres)
DEPARTEMENT_STROKE_WIDTH = 900
DEPARTEMENT_STROKE_COLOR = "#8c8c8c"
REGION_STROKE_WIDTH = 3_500
LABEL_SIZE = 12_000
PRINT_WIDTH = "600mm"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_regions = fetch(SOURCES["regions"])
    layers = {
        "departements": to_board_layout(
            with_region_codes(fetch(SOURCES["departements"]), raw_regions), ZOOM_CODES
        ),
        "regions": to_board_layout(raw_regions),
    }
    for plate, layer, label_field in PLATES:
        path = OUTPUT_DIR / f"{plate}.svg"
        path.write_text(render_svg(layers[layer], label_field), encoding="utf-8")
        print(f"written: {path}")

    path = OUTPUT_DIR / "departements_in_regions.svg"
    path.write_text(render_region_plate(layers["departements"]), encoding="utf-8")
    print(f"written: {path}")


def fetch(url):
    """Download a GeoJSON layer into a GeoDataFrame (EPSG:4326)."""
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return gpd.read_file(io.StringIO(response.text))


def to_board_layout(gdf, zoom_codes=()):
    """Project the metropole, then pack every inset into its own box.

    Insets are scaled to fill their box, so sizes are no longer comparable
    across territories: on a board, each one must stay playable.
    The zoom cluster is a duplicate -- those departments also stay in place
    on the main map, but unlabelled, so the label only shows on the blow-up.
    """
    is_drom = gdf["nom"].isin(DROM_CRS)
    metropole = flatten(gdf[~is_drom].to_crs(METROPOLE_CRS)).copy()
    metropole["labelled"] = ~metropole["code"].isin(zoom_codes)
    metropole["svg_id"] = metropole["code"]

    minx, miny, maxx, maxy = metropole.total_bounds
    box = (maxy - miny) / 6

    insets = [
        drom_inset(
            gdf, name, crs,
            (minx - 1.5 * box, maxy - (rank + 1) * box, minx - 0.5 * box, maxy - rank * box),
        )
        for rank, (name, crs) in enumerate(DROM_CRS.items())
    ]
    if zoom_codes:
        insets.append(
            zoom_inset(
                metropole, zoom_codes,
                (maxx - 1.5 * box, maxy + 0.1 * box, maxx, maxy + 1.1 * box),
            )
        )

    return gpd.GeoDataFrame(pd.concat([metropole, *insets], ignore_index=True))


def with_region_codes(departements, regions):
    """Tag each department with its region, by point-in-polygon on the region layer."""
    points = departements.copy()
    points.geometry = points.geometry.representative_point()
    joined = points.sjoin(regions[["code", "geometry"]].rename(columns={"code": "region"}), how="left")
    departements = departements.copy()
    departements["region"] = joined["region"].values
    return departements


def flatten(gdf):
    """Drop the CRS so projected metropole and DROM can share one canvas."""
    return gdf.set_crs(None, allow_override=True)


def drom_inset(gdf, name, crs, box):
    """Project one overseas territory in its local CRS, then fit it into its box."""
    inset = fit_into_box(flatten(gdf[gdf["nom"] == name].to_crs(crs)), box)
    inset["labelled"] = True
    inset["svg_id"] = inset["code"]
    return inset


def fit_into_box(gdf, box):
    """Scale and center a layer inside `box`, preserving its aspect ratio."""
    minx, miny, maxx, maxy = box
    left, bottom, right, top = gdf.total_bounds
    factor = min((maxx - minx) / (right - left), (maxy - miny) / (top - bottom))
    width, height = (right - left) * factor, (top - bottom) * factor

    gdf = gdf.copy()
    gdf.geometry = gdf.geometry.apply(
        lambda geometry: translate(
            scale(geometry, factor, factor, origin=(left, bottom)),
            minx - left + (maxx - minx - width) / 2,
            miny - bottom + (maxy - miny - height) / 2,
        )
    )
    return gdf


def zoom_inset(metropole, codes, box):
    """Duplicate a cluster of departments, blown up into its own box."""
    zoom = fit_into_box(metropole[metropole["code"].isin(codes)], box)
    zoom["labelled"] = True
    zoom["svg_id"] = zoom["code"] + "-zoom"  # keep SVG ids unique, keep labels clean
    return zoom


def render_svg(gdf, label_field):
    """Build one SVG plate: shapes in a group, labels in a separate group."""
    left, bottom, right, top = gdf.total_bounds
    pad = (right - left) * 0.02
    view_box = f"{left - pad:.0f} {bottom - pad:.0f} {right - left + 2 * pad:.0f} {top - bottom + 2 * pad:.0f}"
    flip = lambda y: bottom + top - y  # SVG y-axis points down

    shapes = "\n".join(
        f'<path id="{row.svg_id}" data-name="{escape(row.nom)}" d="{to_path(row.geometry, flip)}"/>'
        for row in gdf.itertuples()
    )
    labels = "" if label_field is None else "\n".join(
        label_at(row.geometry, getattr(row, label_field), flip)
        for row in gdf.itertuples() if row.labelled
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="{PRINT_WIDTH}">
<!-- {CREDIT} -->
<g id="shapes" fill="#ffffff" stroke="#000000" stroke-width="{STROKE_WIDTH}" stroke-linejoin="round">
{shapes}
</g>
<g id="labels" font-family="sans-serif" font-size="{LABEL_SIZE}" text-anchor="middle" fill="#000000">
{labels}
</g>
</svg>
"""


def render_region_plate(gdf):
    """Departments with name and number; regions read through weight and value."""
    regions = gdf.dissolve(by="region")
    regions.geometry = regions.buffer(50).buffer(-50)  # close the slivers left by simplification
    left, bottom, right, top = gdf.total_bounds
    pad = (right - left) * 0.02
    view_box = f"{left - pad:.0f} {bottom - pad:.0f} {right - left + 2 * pad:.0f} {top - bottom + 2 * pad:.0f}"
    flip = lambda y: bottom + top - y

    shapes = "\n".join(
        f'<path id="{row.svg_id}" data-name="{escape(row.nom)}" d="{to_path(row.geometry, flip)}"/>'
        for row in gdf.itertuples()
    )
    borders = "\n".join(
        f'<path id="region-{code}" d="{to_path(geometry, flip)}"/>'
        for code, geometry in regions.geometry.items()
    )
    labels = "\n".join(
        label_stack(row.geometry, row.nom, row.code, flip)
        for row in gdf.itertuples() if row.labelled
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="{PRINT_WIDTH}">
<!-- {CREDIT} -->
<g id="shapes" fill="#ffffff" stroke="{DEPARTEMENT_STROKE_COLOR}" stroke-width="{DEPARTEMENT_STROKE_WIDTH}" stroke-linejoin="round">
{shapes}
</g>
<g id="region-borders" fill="none" stroke="#000000" stroke-width="{REGION_STROKE_WIDTH}" stroke-linejoin="round">
{borders}
</g>
<g id="labels" font-family="sans-serif" font-size="{LABEL_SIZE}" text-anchor="middle" fill="#000000">
{labels}
</g>
</svg>
"""


def label_at(geometry, text, flip):
    point = geometry.representative_point()  # always inside the shape, unlike a centroid
    return f'<text x="{point.x:.0f}" y="{flip(point.y):.0f}">{escape(text)}</text>'


def label_stack(geometry, name, code, flip):
    """Name above, number below, as one movable text block."""
    point = geometry.representative_point()
    x = f"{point.x:.0f}"
    return (
        f'<text x="{x}" y="{flip(point.y):.0f}">'
        f'<tspan x="{x}">{escape(name)}</tspan>'
        f'<tspan x="{x}" dy="{LABEL_SIZE}" font-size="{LABEL_SIZE * 0.7:.0f}" fill="#666666">{code}</tspan>'
        f"</text>"
    )


def to_path(geometry, flip):
    polygons = geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry]
    rings = (ring for polygon in polygons for ring in [polygon.exterior, *polygon.interiors])
    return " ".join(to_subpath(ring, flip) for ring in rings)


def to_subpath(ring, flip):
    points = " ".join(f"{x:.0f},{flip(y):.0f}" for x, y in ring.coords)
    return f"M {points} Z"


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


if __name__ == "__main__":
    main()
