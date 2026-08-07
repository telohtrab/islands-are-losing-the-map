"""Split the Pacific Data Hub climate export into one CSV per indicator.

The raw download stacks every indicator in a single long table. Working from
one file per indicator keeps the downstream scripts simple.

Source: https://stats-sdmx-disseminate.pacificdata.org/rest/data/SPC,DF_CLIMATE_CHANGE,1.0/all?dimensionAtObservation=AllDimensions&format=csvfilewithlabels
"""

import pandas as pd
from scipy.stats import linregress

CSV_PATH = "data/raw/SPC_DF_CLIMATE_CHANGE_COMPLETE.csv"

# The PDH export is semicolon-delimited
df = pd.read_csv(CSV_PATH, sep=";")

# One subset per indicator code.
# ST_ANOM = surface air temperature anomaly, the variable that drives the piece.
# SST_ANOM = sea surface temperature, RAIN_ANOM = rainfall, SEA_LEVEL_ANOM = sea level.
st_anom = df[df["CLIMATE_CHANGE_INDICATORS"] == "ST_ANOM"]
sst_anom = df[df["CLIMATE_CHANGE_INDICATORS"] == "SST_ANOM"]
rain_anom = df[df["CLIMATE_CHANGE_INDICATORS"] == "RAIN_ANOM"]
sea_level_anom = df[df["CLIMATE_CHANGE_INDICATORS"] == "SEA_LVL"]

st_anom.to_csv("data/processed/st_anom.csv", index=False)
sst_anom.to_csv("data/processed/sst_anom.csv", index=False)
rain_anom.to_csv("data/processed/rain_anom.csv", index=False)
sea_level_anom.to_csv("data/processed/sealevel_anom.csv", index=False)