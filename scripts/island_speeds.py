"""Compute how far north or south each territory moves in the final map.

Each territory warms at its own pace. The piece turns that pace into a vertical
position: the fastest warming territory ends up at the top of the frame, the
slowest at the bottom, everyone else in between.

The output is a table of Y offsets in metres, expressed in EPSG:3832. It is the
single source of truth shared by QGIS (Translate on the vector silhouettes) and
Blender (object translation on the relief meshes), so both layers stay aligned.

The move is a rigid-body translation. Shapes and sizes are untouched, only the
centroid position changes.
"""

import pandas as pd
import geopandas as gpd
from scipy.stats import linregress
from shapely.geometry import Point
import os

# One GeoPackage per territory, renamed with its GEO_PICT code so it matches the
# PDH data. Indonesia sits in the folder but is out of scope for the piece.
dossier = "data/raw/geopackages-lands-gadm"
codes = [f.removeprefix('gadm41_').removesuffix(".gpkg") for f in os.listdir(dossier) if f != "gadm41_IDN.gpkg"]

CSV_PATH = "data/processed/st_anom.csv"

# Linear mapping from warming rate (°C per decade) to a Y position in metres.
# Calibrated in output/58-cadrage-intermediaire.png: the 22 territories spread
# over 3 916 km of vertical amplitude, wide enough to read as a ranking, tight
# enough to keep everyone inside the frame.
# OFFSET recentres the whole set on Y = 0. It shifts every territory by the same
# amount, so it changes nothing in the spacing. It only keeps the coordinates
# near the equator, where the Pacific actually sits, which makes the result
# easier to check in QGIS.
FACTOR = 27_908_518.07
OFFSET = 3_961_468.40

overrides = {
    "KI" : (173.0176, 1.3382),
    "PF" : (-149.5667, -17.5334),
    "TV" : (179.1983, -8.5211)
}

df = pd.read_csv(CSV_PATH)

# 50-year window for the trend.
yoi = df[(df["TIME_PERIOD"] >= 1976) & (df['TIME_PERIOD'] <= 2025)]
# Pre-industrial reference and most recent decade, for the absolute warming figure.
ref = df[(df["TIME_PERIOD"] >= 1850) & (df['TIME_PERIOD'] <= 1900)]
decade = df[(df["TIME_PERIOD"] >= 2016) & (df['TIME_PERIOD'] <= 2025)]

resultats = []

for code in codes:
    country = yoi[yoi["GEO_PICT"] == code]
    nom = country["Pays et territoires insulaires du Pacifique"].iloc[0]

    # Least-squares trend on the annual anomalies. slope is °C per year,
    # multiplied by 10 to read as °C per decade.
    speed = linregress(x=country['TIME_PERIOD'], y=country['OBS_VALUE']).slope
    speed = speed * 10
    print(speed)

    # ADM_ADM_0 is the national outline. Reprojecting to 3832 before taking the
    # centroid matters: a centroid computed on degrees would not be in metres.
    gpkg = gpd.read_file("data/raw/geopackages-lands-gadm/gadm41_"+code+".gpkg", layer="ADM_ADM_0").to_crs(3832)

    if code in overrides: 
        gpkg_centroid = gpd.GeoSeries([Point(*overrides[code])], crs=4326)
        gpkg_centroid = gpkg_centroid.to_crs(3832)
    else: 
        gpkg_centroid = gpkg.geometry.centroid

    # target_y is where the territory belongs on the climate scale.
    # offset_y is the distance it has to travel from its real position.
    target_y = speed * FACTOR - OFFSET
    offset_y = target_y - gpkg_centroid.y.iloc[0]

    absolute_warming =  decade[decade["GEO_PICT"] == code]["OBS_VALUE"].mean() - ref[ref["GEO_PICT"] == code]["OBS_VALUE"].mean()

    resultats.append({"code": code, "label": nom, "offset": offset_y, "speed": speed,  "absolute_warming": absolute_warming})

resultats = pd.DataFrame(resultats)

resultats.to_csv("data/processed/offsets.csv", index=False)

print(resultats.head())
print(resultats.tail())