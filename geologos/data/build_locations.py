#!/usr/bin/env python3
"""Merge the hand-written clue batch with map geometry.

The batch file carries no coordinates, and the game needs something to click.
Each entry here adds: `at` (one or more [lon, lat] anchors -- a list, so that
rivers and seas can be traced rather than pinned), `radiusKm` (how close a
click has to land), and `group` (the round filter).
"""
import json, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent

HOLY, EGYPT, EAST, ASIA = (
    "The Holy Land", "Egypt & Sinai", "Mesopotamia & the East", "Greece & Asia Minor")

GEO = {
    # City-sized targets: one anchor, tight radius.
    "Jerusalem":   dict(at=[[35.2137, 31.7683]], radiusKm=22, group=HOLY),
    "Bethlehem":   dict(at=[[35.2020, 31.7054]], radiusKm=14, group=HOLY),
    "Nazareth":    dict(at=[[35.3035, 32.6996]], radiusKm=22, group=HOLY),
    "Jericho":     dict(at=[[35.4444, 31.8667]], radiusKm=20, group=HOLY),
    "Bethany":     dict(at=[[35.2620, 31.7714]], radiusKm=12, group=HOLY),
    "Capernaum":   dict(at=[[35.5750, 32.8808]], radiusKm=20, group=HOLY),
    "Damascus":    dict(at=[[36.2919, 33.5138]], radiusKm=45, group=EAST),
    "Babylon":     dict(at=[[44.4211, 32.5355]], radiusKm=55, group=EAST),
    "Ur":          dict(at=[[46.1031, 30.9626]], radiusKm=55, group=EAST),
    "Nineveh":     dict(at=[[43.1526, 36.3593]], radiusKm=55, group=EAST),
    "Antioch":     dict(at=[[36.1611, 36.2021]], radiusKm=45, group=ASIA),
    "Corinth":     dict(at=[[22.9319, 37.9061]], radiusKm=40, group=ASIA),
    "Ephesus":     dict(at=[[27.3417, 37.9397]], radiusKm=40, group=ASIA),
    "Patmos":      dict(at=[[26.5470, 37.3086]], radiusKm=35, group=ASIA),

    # Mountains: a peak, but forgiving.
    "Mount Sinai":  dict(at=[[33.9750, 28.5392]], radiusKm=70, group=EGYPT),
    "Mount Ararat": dict(at=[[44.2989, 39.7025]], radiusKm=70, group=EAST),

    # Regions and waterways: traced with several anchors so a click anywhere
    # along the feature reads as correct, not just at an arbitrary midpoint.
    "Red Sea": dict(at=[[32.55, 29.90], [32.95, 29.25], [33.45, 28.50],
                        [34.05, 27.60], [34.75, 26.60], [35.30, 25.60]],
                    radiusKm=90, group=EGYPT),
    "Jordan River": dict(at=[[35.62, 32.72], [35.58, 32.42], [35.55, 32.14],
                             [35.53, 31.90], [35.52, 31.78]],
                         radiusKm=26, group=HOLY),
    "Sodom (Dead Sea region)": dict(at=[[35.40, 31.25], [35.46, 31.05],
                                        [35.48, 31.40]],
                                    radiusKm=40, group=HOLY),
    "Egypt (Goshen)": dict(at=[[31.85, 30.75], [31.35, 30.55], [31.24, 30.05],
                               [31.10, 29.40], [32.30, 30.60]],
                           radiusKm=95, group=EGYPT),
}

src = json.loads((ROOT / "bible_facts_batch1.json").read_text())

out = []
for loc in src["locations"]:
    geo = GEO[loc["place"]]
    # Clue text, modernCountry, ancientRegion and didYouKnow are carried over
    # verbatim -- this script only ever adds map geometry.
    out.append(collections.OrderedDict(
        place=loc["place"],
        modernCountry=loc["modernCountry"],
        ancientRegion=loc["ancientRegion"],
        group=geo["group"],
        at=geo["at"],
        radiusKm=geo["radiusKm"],
        clues=loc["clues"],
        didYouKnow=loc["didYouKnow"],
    ))

doc = collections.OrderedDict(
    source="bible_facts_batch1.json",
    notes=("Playable form of batch 1. Clues, modernCountry, ancientRegion and "
           "didYouKnow are verbatim from the source batch; `at` (lon/lat "
           "anchors), `radiusKm` (click tolerance) and `group` (round filter) "
           "were added so the location can be found on the map."),
    locations=out,
)
(ROOT / "bible_locations.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {len(out)} locations")
for g in (HOLY, EGYPT, EAST, ASIA):
    print(" ", g, sum(1 for o in out if o["group"] == g))
