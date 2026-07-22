# Base map sources

## AWMC (Ancient World Mapping Center), University of North Carolina

`herods_kingdom.geojson`, `roman_provinces_ce200.geojson`, `regional_names.geojson`

Trimmed to this game's frame (lon 11–49.5, lat 24–44) from
<https://github.com/AWMC/geodata>, by `build_basemap.py`. Geometry is
unmodified; only out-of-frame features and unused attributes were dropped.

Derived from the *Barrington Atlas of the Greek and Roman World* and from
AWMC modifications to OpenStreetMap.

**Licence: ODbL 1.0** — <http://opendatacommons.org/licenses/odbl/1.0/>.
Attribution and share-alike apply to this data and to any database derived
from it.

Suggested citation: Ancient World Mapping Center, "<shapefile name>",
<http://awmc.unc.edu/wordpress/map-files/>.

## Natural Earth

Coastlines and modern country borders, loaded at runtime as
`world-atlas@2/countries-10m.json`. Public domain, no attribution required.

## Not used, and why

`aourednik/historical-basemaps` (GPL-3.0) was evaluated and rejected. In this
frame its Iron Age coverage is no better than a sketch — Assyria is 12 points,
Babylonia 9 — the bc1000 and bc700 files are identical over the Levant, and it
labels the region "Kingdom of David and Solomon" at 700 BC, some 230 years
after that kingdom split. At bc1 the entire Roman Empire is a single polygon
with no provinces.
