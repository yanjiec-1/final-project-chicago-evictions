# Chicago Eviction Filing Inequality Project

This project examines eviction filing patterns in Chicago and asks whether eviction filings are more common in low-income and minority neighborhoods. We focus on census tracts in 2019 and combine eviction outcomes with neighborhood socioeconomic and demographic characteristics to study where eviction filings are most concentrated.

## Streamlit Dashboard

Streamlit Community Cloud app:  
https://final-project-chicago-evictions-fbssvq6nw6ygtr9mwsappmf.streamlit.app/

**Note:** If the Streamlit app has not been used in the last 24 hours, it may need to be “woken up.” This is normal behavior on Streamlit Community Cloud and is not a bug.

## Setup

Create the conda environment:

```bash
conda env create -f environment_local.yml
conda activate final_project_chicago_evictions
python -m ipykernel install --user --name final_project_chicago_evictions --display-name "final_project_chicago_evictions"
```

## Project Structure

```
code/
  preprocessing.py     # Merges eviction, ACS, income, and shapefile data
  plot_1_choropleth.py         # Choropleth map of eviction filing rate
  plot_2_scatter.py            # Scatter plot of eviction rate vs median household income
  plot_3_boxplot.py            # Boxplot comparing eviction filing rates across minority-share quartiles
  plot_4_hotspot.py            # Hotspot ranking of top tracts with context
data/
  raw-data/                               # Original downloaded datasets
    eviction_data_tract.csv               # Chicago Evictions Release 2 tract-level eviction outcomes, including eviction filing counts and filing rates by year
    census_data_tract.csv                 # ACS-based tract-level neighborhood characteristics from the Chicago Evictions release, including poverty-related measures, race/ethnicity counts, housing variables, and median rent
    census_tract_crosswalk_chicago.csv    # Crosswalk file linking census tracts to Chicago, used to filter tract-level ACS income data to Chicago tracts
    ACSDT5Y2019.B19013-Data.csv           # ACS 5-year table B19013 with tract-level median household income
    tl_2019_17_tract.cpg                  # Encoding file for the 2019 Illinois Census tract shapefile
    tl_2019_17_tract.dbf                  # Attribute table for the 2019 Illinois Census tract shapefile
    tl_2019_17_tract.prj                  # Projection information for the 2019 Illinois Census tract shapefile
    tl_2019_17_tract.shp                  # Geometry file for the 2019 Illinois Census tract boundaries
    tl_2019_17_tract.shx                  # Shape index file for the 2019 Illinois Census tract shapefile
  derived-data/                              # Processed analytic datasets
    chicago_eviction_analytic_2019.csv    # Final tract-level analytic table for Chicago in 2019, containing eviction outcomes, income, poverty, and demographic variables
    chicago_eviction_analytic_2019.geojson # Spatial version of the final analytic dataset with tract geometries for mapping
    chicago_eviction_analytic_2019.json   # GeoJSON-style JSON file used by the Streamlit app for interactive mapping
figures/                                            # Externally generated graphics used in the final writeup
  plot_1_choropleth_eviction_rate_2019.png          # Choropleth map showing the spatial distribution of 2019 eviction filing rates across Chicago census tracts
  plot_2_scatter_eviction_vs_income.png             # Scatter plot of tract-level eviction filing rate versus median household income
  plot_3_boxplot_eviction_by_minority_quartile.png  # Boxplot comparing eviction filing rates across minority-share quartiles
  plot_4_top_tracts_hotspot_context.png             # Bar chart ranking the highest-eviction tracts and summarizing their neighborhood context
streamlit-app/
  app.py               # Streamlit dashboard
```

## Data Sources
This project uses the following datasets:
1. Chicago Evictions dataset (LCBH Release 2)
Downloaded from the Chicago Evictions data portal as CSV (https://eviction.lcbh.org/data/download).
Used for tract-level eviction filing counts and filing rates for Chicago.
Main file: eviction_data_tract.csv

2. ACS-based tract covariates from the Chicago Evictions release
Downloaded from the Chicago Evictions data portal as CSV (https://eviction.lcbh.org/data/download).
Used for poverty measures, demographic composition, and median rent.
Main file: census_data_tract.csv

3. ACS 5-year median household income (Table B19013)
Downloaded from data.census.gov as tract-level CSV (https://data.census.gov/table/ACSDT5Y2019.B19013?q=B19013:+Median+Household+Income+in+the+Past+12+Months+(in+2024+Inflation-Adjusted+Dollars)&g=050XX00US17031$1400000).
Used for tract-level median household income.
Main file: ACSDT5Y2019.B19013-Data.csv

4. 2019 Census TIGER/Line tract shapefile
Downloaded from the U.S. Census TIGER/Line site (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2019.html#list-tab-790442341).
Used for tract-level spatial boundaries and mapping.
Main files: tl_2019_17_tract.shp, tl_2019_17_tract.shx, tl_2019_17_tract.dbf, tl_2019_17_tract.prj, tl_2019_17_tract.cpg

## Data Processing

The data processing pipeline is implemented in `code/preprocessing.py`.

Main steps:
- Load tract-level eviction filings and outcomes from the Chicago Evictions release and keep 2019.
- Load tract-level ACS covariates from the Chicago Evictions release (poverty and demographic measures).
- Load ACS 5-year median household income (B19013) and filter to Chicago tracts using the crosswalk file.
- Merge datasets by tract identifier `GEOIDs` so each tract has eviction outcomes and neighborhood characteristics.
- Define eviction filing rate as filings divided by renter households (expressed as a percentage).
- Join the analytic table to 2019 TIGER/Line tract geometry and export:
  - `data/derived-data/chicago_eviction_analytic_2019.csv`
  - `data/derived-data/chicago_eviction_analytic_2019.geojson`
  - `data/derived-data/chicago_eviction_analytic_2019.json` (for the Streamlit app)
- Include a minimum renter-households filter (default: 200) in the Streamlit app to improve rate stability, since eviction filing rates can be inflated and less reliable in tracts with very small renter-household denominators.

## Usage

1. Run preprocessing:
   ```bash
   python code/preprocessing.py
   ```

2. Generate static visualizations:
   ```bash
   python code/plot_1_choropleth.py
   python code/plot_2_scatter.py
   python code/plot_3_boxplot.py
   python code/plot_4_hotspot.py
   ```

3. Launch the Streamlit dashboard
   ```bash
   streamlit run streamlit-app/app.py
   ```

## Outputs

The project produces:
- one tract-level analytic dataset for Chicago (2019), exported in three formats in data/derived-data/:
  - chicago_eviction_analytic_2019.csv (tabular analytic file)
  - chicago_eviction_analytic_2019.geojson (same data with tract geometries for mapping)
  - chicago_eviction_analytic_2019.json (GeoJSON-style JSON used by the Streamlit app)
- four static visualizations in figures/
- an interactive Streamlit dashboard in streamlit-app/

## Research Question

Our main research question is:
Are 2019 eviction filing rates higher in census tracts with lower income and higher minority share in Chicago?
As supporting analysis, we identify high-eviction hotspot tracts and summarize their neighborhood characteristics.