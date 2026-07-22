#!/usr/bin/env python3
"""Fetch AWMC's Barrington-derived layers and trim them to the game's frame.

Run this to regenerate basemap/*.geojson. Geometry is never altered -- features
outside the frame are dropped and unused attributes stripped, nothing more.
See basemap/ATTRIBUTION.md: this data is ODbL, attribution and share-alike.
"""
import json, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
DST  = ROOT / "basemap"
BB   = (11.0, 49.5, 24.0, 44.0)          # lon0, lon1, lat0, lat1
RAW  = "https://raw.githubusercontent.com/AWMC/geodata/master/"

NE = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
      "geojson/ne_10m_rivers_lake_centerlines.geojson")

SOURCES = [
    ("herods_kingdom.geojson",
     RAW + "Cultural-Data/political_shading/herod/herods_kingdom.geojson", None, 0),
    ("roman_provinces_ce200.geojson",
     RAW + "Cultural-Data/political_shading/roman_empire_ce_200_provinces/"
           "roman_empire_ce_200_provinces.geojson", ["PROVINCE10", "PROVINCE_1"], 0),
    ("regional_names.geojson",
     RAW + "Cultural-Data/regional_name_linework/regional_names_linework.geojson",
     ["TITLE", "TYPE", "MINDATE", "MAXDATE"], 3),
    # Public domain, and proper line geometry. AWMC carries inland water as
    # thousands of small polygons instead -- the Nile alone comes in 128
    # fragments -- which is the wrong shape for drawing a river course.
    ("rivers.geojson", NE, ["name", "name_en"], 0),
]

# The lakes that the clues actually name, pulled out of AWMC's inland water by
# their ancient titles rather than by dragging in 2.3 MB of marshland.
LAKES = ("https://raw.githubusercontent.com/AWMC/geodata/master/"
         "Physical%20Data/inland_water/inland-water-OSM.geojson")
LAKE_TITLES = ("Mortuum Mare/Asphaltitis L.",      # the Dead Sea
               "Tiberiadis Mare/Gennesar L.",      # the Sea of Galilee
               "Semachonitis L.")                  # Lake Huleh, up the Jordan
# Label linework only: the file also carries thousands of two-point ticks for
# individual islets, which are noise at this scale.
NAME_TYPES = ("region", "mountain", "plain", "people, tribe")


def in_frame(geom):
    xs, ys = [], []
    def walk(c):
        if not c:
            return
        if isinstance(c[0], (int, float)):
            xs.append(c[0]); ys.append(c[1])
        else:
            for k in c:
                walk(k)
    walk(geom.get("coordinates") or [])
    if not xs:
        return False
    return max(xs) >= BB[0] and min(xs) <= BB[1] and max(ys) >= BB[2] and min(ys) <= BB[3]


def points(fc):
    return sum(json.dumps(f["geometry"]["coordinates"]).count("[") - 1
               for f in fc["features"])


def main():
    DST.mkdir(exist_ok=True)
    for name, url, keep, min_pts in SOURCES:
        with urllib.request.urlopen(url) as r:
            src = json.load(r)
        out = []
        for f in src["features"]:
            g = f.get("geometry")
            if not g or not in_frame(g):
                continue
            props = f.get("properties") or {}
            if keep:
                props = {k: props.get(k) for k in keep
                         if props.get(k) not in (None, "", 0, 0.0)}
            if min_pts:
                if (f["properties"].get("TYPE") or "") not in NAME_TYPES:
                    continue
                if json.dumps(g["coordinates"]).count("[") - 1 < min_pts:
                    continue
            out.append({"type": "Feature", "properties": props, "geometry": g})
        fc = {"type": "FeatureCollection", "features": out}
        path = DST / name
        json.dump(fc, open(path, "w"), separators=(",", ":"))
        print(f"  {name:32} {len(out):>5} features  {points(fc):>7,} pts  "
              f"{path.stat().st_size / 1024:>7,.0f} KB")

    with urllib.request.urlopen(LAKES) as r:
        src = json.load(r)
    out = []
    for f in src["features"]:
        p = f.get("properties") or {}
        title = (p.get("EN_NAME") or p.get("TITLE") or "").strip()
        if title in LAKE_TITLES and in_frame(f["geometry"]):
            out.append({"type": "Feature",
                        "properties": {"TITLE": title},
                        "geometry": f["geometry"]})
    fc = {"type": "FeatureCollection", "features": out}
    path = DST / "lakes.geojson"
    json.dump(fc, open(path, "w"), separators=(",", ":"))
    print(f"  {'lakes.geojson':32} {len(out):>5} features  {points(fc):>7,} pts  "
          f"{path.stat().st_size / 1024:>7,.0f} KB")


if __name__ == "__main__":
    main()
