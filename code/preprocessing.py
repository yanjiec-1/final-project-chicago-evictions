from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
import altair as alt

import warnings
warnings.filterwarnings('ignore')
alt.data_transformers.disable_max_rows()
import vl_convert as vlc
from IPython.display import SVG, display, Image
import tempfile
alt.renderers.enable("png")

# base directory for the project: code/
BASE_DIR = Path(__file__).resolve().parent
# parent directory of the base directory: repo root
REPO_DIR = BASE_DIR.parent
# raw data directory: data/raw-data/
RAW_DIR = REPO_DIR / "data" / "raw-data"
# derived data directory: data/derived-data/
DERIVED_DIR = REPO_DIR / "data" / "derived-data"

# helper function to save an Altair chart as a high-resolution PNG
def save_altair_png(chart, out_path, scale=3):
    # convert the chart to a PNG bytes object
    png_bytes = vlc.vegalite_to_png(chart.to_dict(), scale=scale)
    # save the PNG bytes to a file
    with open(out_path, "wb") as f:
        f.write(png_bytes)

# helper function to read a shapefile
def _read_shapefile(shp_path: Path):
    # try to read the shapefile using the default engine
    try:
        return gpd.read_file(shp_path)
    except Exception:
        # if the default engine fails, try using the pyogrio engine
        return gpd.read_file(shp_path, engine="pyogrio")

# load the eviction data for the year 2019
def load_eviction_tract_2019():
    # path to the eviction data: data/raw-data/eviction_data_tract.csv
    path = RAW_DIR / "eviction_data_tract.csv"
    # read the eviction data into a pandas dataframe
    df = pd.read_csv(path, dtype={"tract": str})

    # filter the dataframe to only include the year 2019
    df = df.loc[df["filing_year"] == 2019].copy()
    
    # keep only the columns we need
    keep_cols = [
        "tract",
        "filing_year",
        "eviction_filings_total",
        "eviction_filings_rate",
    ]
    return df[keep_cols].copy()

# load the census covariates
def load_census_covariates():
    # path to the census data: data/raw-data/census_data_tract.csv
    path = RAW_DIR / "census_data_tract.csv"
    # read the census data into a pandas dataframe
    df = pd.read_csv(path, dtype={"tract": str})

    # filter the dataframe to only include the year 2014-2018 5-year estimates
    df = df.loc[df["census_year"] == "2014-2018 5-year estimates"].copy()
    
    # keep only the numeric columns
    numeric_cols = [
        "housing_units_total",
        "housing_units_rental",
        "housing_units_other",
        "median_rent",
        "population_total",
        "population_poverty_below",
        "population_poverty_above",
        "population_race_white",
        "population_race_black",
        "population_race_latinx",
        "population_race_asian",
        "population_race_other",
    ]
    # convert the numeric columns to numeric data types
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # calculate the poverty rate
    df["poverty_rate"] = df["population_poverty_below"] / df["population_total"]
    # calculate the percentage of the population that is black
    df["pct_black"] = df["population_race_black"] / df["population_total"]
    # calculate the percentage of the population that is latinx
    df["pct_latinx"] = df["population_race_latinx"] / df["population_total"]
    # calculate the minority share
    df["minority_share"] = (
        df["population_race_black"]
        + df["population_race_latinx"]
        + df["population_race_asian"]
        + df["population_race_other"]
    ) / df["population_total"]

    # keep only the columns we need
    keep_cols = [
        "tract",
        "census_year",
        "housing_units_rental",
        "median_rent",
        "population_total",
        "population_poverty_below",
        "poverty_rate",
        "pct_black",
        "pct_latinx",
        "minority_share",
    ]
    return df[keep_cols].copy()

# load the income data
def load_income_b19013():
    # path to the income data: data/raw-data/ACSDT5Y2019.B19013-Data.csv
    path = RAW_DIR / "ACSDT5Y2019.B19013-Data.csv"
    # read the income data into a pandas dataframe
    df = pd.read_csv(path, dtype=str)

    # Drop the first metadata row: Geography column
    df = df.loc[df["GEO_ID"] != "Geography"].copy()

    # extract the tract from the GEO_ID column by removing the first characters (1400000US)
    df["tract"] = df["GEO_ID"].str.replace("1400000US", "", regex=False)
    # convert the median household income to a numeric data type
    df["median_household_income"] = pd.to_numeric(df["B19013_001E"], errors="coerce")

    return df[["tract", "median_household_income"]].copy()

# load the chicago crosswalk
def load_chicago_crosswalk():
    # path to the chicago crosswalk: data/raw-data/census_tract_crosswalk_chicago.csv
    path = RAW_DIR / "census_tract_crosswalk_chicago.csv"
    # read the chicago crosswalk into a pandas dataframe
    df = pd.read_csv(path, dtype={"census_tract": str})
    # rename the census tract column to tract
    df = df.rename(columns={"census_tract": "tract"})
    # keep only the columns we need
    keep_cols = [c for c in ["tract", "place", "partial", "housing_percent", "pop_percent"] if c in df.columns]
    
    return df[keep_cols].copy()

# load the tract geometry
def load_tract_geometry():
    # path to the tract geometry: data/raw-data/tl_2019_17_tract.shp
    shp_path = RAW_DIR / "tl_2019_17_tract.shp"
    # read the tract geometry into a geopandas dataframe
    gdf = _read_shapefile(shp_path)

    # extract the tract from the GEOID column
    gdf["tract"] = gdf["GEOID"].astype(str)
    
    # keep only the columns we need
    keep_cols = ["tract", "STATEFP", "COUNTYFP", "TRACTCE", "GEOID", "geometry"]
    keep_cols = [c for c in keep_cols if c in gdf.columns]
    
    return gdf[keep_cols].copy()

# build the analytic dataframe by merging the eviction, census, income, and chicago crosswalk dataframes
def build_analytic_dataframe():
    # load the eviction data
    eviction = load_eviction_tract_2019()
    # load the census data
    census = load_census_covariates()
    # load the income data
    income = load_income_b19013()
    # load the chicago crosswalk
    chicago_xwalk = load_chicago_crosswalk()

    # merge the eviction, census, income
    df = eviction.merge(census, on="tract", how="inner")
    df = df.merge(income, on="tract", how="inner")

    # filter to Chicago tracts via crosswalk if available
    # merge the chicago crosswalk with the dataframe on the tract column
    if "tract" in chicago_xwalk.columns:
        df = df.merge(chicago_xwalk[["tract"]].drop_duplicates(), on="tract", how="inner")

    # keep only the columns we need
    core_cols = [
        "eviction_filings_total",
        "eviction_filings_rate",
        "median_household_income",
        "poverty_rate",
        "pct_black",
        "pct_latinx",
        "minority_share",
    ]
    # drop rows with missing values in the core columns
    df = df.dropna(subset=core_cols).copy()

    return df

# build the analytic geodataframe by merging the analytic dataframe with the tract geometry
def build_analytic_geodataframe():
    # build the analytic dataframe
    df = build_analytic_dataframe()
    # load the tract geometry
    tracts = load_tract_geometry()
    
    # merge the analytic dataframe with the tract geometry on the tract column
    gdf = tracts.merge(df, on="tract", how="inner")
    # convert the dataframe to a geopandas dataframe
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=tracts.crs)

    return gdf

# save the processed outputs to the derived data directory
def save_processed_outputs():
    # build the analytic dataframe
    df = build_analytic_dataframe()
    # build the analytic geodataframe
    gdf = build_analytic_geodataframe()

    # path to the csv file: data/derived-data/chicago_eviction_analytic_2019.csv
    csv_path = DERIVED_DIR / "chicago_eviction_analytic_2019.csv"
    # path to the geojson file: data/derived-data/chicago_eviction_analytic_2019.geojson
    geojson_path = DERIVED_DIR / "chicago_eviction_analytic_2019.geojson"
    # path to the json file: data/derived-data/chicago_eviction_analytic_2019.json
    json_path = DERIVED_DIR / "chicago_eviction_analytic_2019.json"

    # We asked AI how to save csv, geojson, and json files. It suggested using the to_csv, to_file, and json.dump methods.
    # save the dataframe to a csv file
    df.to_csv(csv_path, index=False)
    # save the geodataframe to a geojson file
    gdf.to_file(geojson_path, driver="GeoJSON")
    # save the geodataframe to a json file
    with open(json_path, "w") as f:
        json.dump(json.loads(gdf.to_json()), f)

    # print the saved files
    print(f"Saved: {csv_path}")
    print(f"Saved: {geojson_path}")
    print(f"Saved: {json_path}")

# main function to save the processed outputs
if __name__ == "__main__":
    save_processed_outputs()