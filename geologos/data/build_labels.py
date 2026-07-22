#!/usr/bin/env python3
"""Resolve New Testament region labels to positions, and record where each came from.

AWMC's regional name linework is not a gazetteer of region centres -- it is the
label paths off many Barrington sheets, and it contains homonyms. Matching on
the name alone puts Assyria in Anatolia, Achaia on the Black Sea coast (a
different Achaei entirely) and Italia down in Calabria.

So each region is resolved against a reference point: of the atlas features
carrying that name, take the nearest one, and accept it only if it lands within
TOLERANCE degrees of where the region actually is. Anything further out is a
homonym and the reference point is used instead.

Every label ends up tagged with its source -- "awmc" for a real atlas position,
"placed" for one of mine -- so the map can be honest about which is which.
"""
import json, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
TOLERANCE = 3.5          # degrees; beyond this the atlas match is a homonym

# Reference centres. These decide nothing about shape -- they say only "this
# region is around here", which is the same claim the label itself makes.
REFERENCES = [
    # title in the AWMC data,   label to draw,      lon,    lat,   small?
    ("Galilaea",        "GALILAEA",     35.40, 32.85, True),
    ("Samaria",         "SAMARIA",      35.25, 32.35, True),
    ("Peraea",          "PERAEA",       35.75, 31.95, True),
    ("Phoenice",        "PHOENICE",     35.60, 33.80, True),
    ("Nabataea",        "NABATAEA",     36.30, 30.60, True),
    ("Coele Syria",     "COELE SYRIA",  36.60, 34.00, True),
    ("Ionia",           "IONIA",        27.30, 38.10, True),
    ("Caria",           "CARIA",        28.20, 37.30, True),
    ("Lydia/Maionia",   "LYDIA",        28.40, 38.60, True),
    ("Mysia",           "MYSIA",        27.90, 39.60, True),
    ("Phrygia",         "PHRYGIA",      30.50, 38.60, True),
    ("Pisidia",         "PISIDIA",      30.80, 37.60, True),
    ("Lycia",           "LYCIA",        29.60, 36.60, True),
    ("Pamphylia",       "PAMPHYLIA",    31.00, 37.00, True),
    ("Lycaonia",        "LYCAONIA",     32.80, 37.60, True),
    ("Cilicia",         "CILICIA",      34.50, 37.00, True),
    ("Galatia",         "GALATIA",      32.60, 39.60, True),
    ("Bithynia",        "BITHYNIA",     30.20, 40.60, True),
    ("Cappadocia",      "CAPPADOCIA",   35.50, 38.60, True),
    ("Commagene",       "COMMAGENE",    37.80, 37.50, True),
    ("Osrhoene",        "OSRHOENE",     39.20, 37.00, True),
    ("Adiabene",        "ADIABENE",     43.60, 36.60, True),
    ("Macedonia",       "MACEDONIA",    22.50, 40.80, False),
    ("Achaia",          "ACHAIA",       22.40, 38.10, False),
    ("Attica",          "ATTICA",       23.70, 38.10, True),
    ("Arcadia",         "ARCADIA",      22.20, 37.60, True),
    ("Italia",          "ITALIA",       13.20, 42.30, False),
    ("Latium Vetus",    "LATIUM",       12.90, 41.70, True),
    ("Creta Ins.",      "CRETA",        24.90, 35.20, True),
    ("Cyprus (island)", "CYPRUS",       33.20, 35.05, True),
    ("Mesopotamia",     "MESOPOTAMIA",  41.30, 34.60, False),
    ("Assyria",         "ASSYRIA",      42.80, 36.20, False),
    ("Babylonia",       "BABYLONIA",    44.60, 32.20, False),
    ("Susiane",         "SUSIANE",      48.40, 32.00, True),
    ("Armenia Maior",   "ARMENIA",      43.60, 39.60, True),
]

# Names AWMC's linework does not carry at all, and the game leans on them.
PLACED_ONLY = [
    ("IUDAEA",    35.15, 31.55, False),
    ("IDUMAEA",   34.95, 31.00, True),
    ("DECAPOLIS", 36.10, 32.40, True),
    ("AEGYPTUS",  31.20, 27.20, False),
    ("SYRIA",     37.60, 34.90, False),
]


def anchors(feature):
    """The midpoint of the longest line: where the atlas writes the name."""
    g = feature["geometry"]
    lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    longest = max(lines, key=len)
    return longest[len(longest) // 2]


def main():
    src = json.loads((ROOT / "basemap" / "regional_names.geojson").read_text())
    by_title = {}
    for f in src["features"]:
        t = (f["properties"].get("TITLE") or "").strip()
        by_title.setdefault(t, []).append(anchors(f))

    out, from_atlas, placed = [], 0, 0
    for title, label, lon, lat, sm in REFERENCES:
        best, best_d = None, 1e9
        for a in by_title.get(title, []):
            d = math.hypot((a[0] - lon) * math.cos(math.radians(lat)), a[1] - lat)
            if d < best_d:
                best, best_d = a, d
        if best and best_d <= TOLERANCE:
            out.append({"text": label, "at": [round(best[0], 4), round(best[1], 4)],
                        "sm": sm, "source": "awmc"})
            from_atlas += 1
        else:
            why = "no match" if best is None else f"nearest was {best_d:.1f} deg away"
            print(f"    {label:12} placed by hand ({why})")
            out.append({"text": label, "at": [lon, lat], "sm": sm, "source": "placed"})
            placed += 1

    for label, lon, lat, sm in PLACED_ONLY:
        out.append({"text": label, "at": [lon, lat], "sm": sm, "source": "placed"})
        placed += 1

    dst = ROOT / "basemap" / "region_labels.json"
    dst.write_text(json.dumps(
        {"note": ("New Testament region labels. source=awmc means the position is "
                  "the Barrington Atlas label path; source=placed means it is a "
                  "hand-placed centre, either because AWMC has no such label or "
                  "because every candidate was a homonym."),
         "labels": out}, indent=1))
    print(f"  region_labels.json          {len(out)} labels "
          f"({from_atlas} from the atlas, {placed} placed by hand)")


if __name__ == "__main__":
    main()
