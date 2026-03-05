# Chicago Eviction Filing Inequality Project

This project examines eviction filing patterns in Chicago and asks whether eviction filings are more common in low-income and minority neighborhoods. We focus on census tracts in 2019 and combine eviction outcomes with neighborhood socioeconomic and demographic characteristics to study where eviction filings are most concentrated.

## Streamlit Dashboard

Streamlit Community Cloud app:  
https://final-project-chicago-evictions-fbssvq6nw6ygtr9mwsappmf.streamlit.app/

**Note:** If the Streamlit app has not been used in the last 24 hours, it may need to be “woken up.” This is normal behavior on Streamlit Community Cloud and is not a bug.

## Setup

Create the conda environment:

```bash
conda env create -f environment.yml
conda activate chicago_eviction_analysis
```

## Project Structure

```
code/
  preprocessing.py     # Merges eviction, ACS, income, and shapefile data
  plot_1_choropleth.py         # Choropleth map of eviction filing rate
  plot_2_scatter.py            # Scatter plot of eviction rate vs median household income
  plot_3_boxplot.py            # Group comparison plot by poverty quantiles
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
  plot_1_choropleth_eviction_rate_2019.png        # Choropleth map showing the spatial distribution of 2019 eviction filing rates across Chicago census tracts
  plot_2_scatter_eviction_vs_income.png           # Scatter plot of tract-level eviction filing rate versus median household income
  plot_3_boxplot_eviction_by_poverty_quantile.png # Boxplot comparing eviction filing rates across tract poverty-rate quartiles
  plot_4_top_tracts_hotspot_context.png           # Bar chart ranking the highest-eviction tracts and summarizing their neighborhood context
streamlit-app/
  app.py               # Streamlit dashboard
```

## Data Sources
This project uses the following datasets:
1. Chicago Evictions dataset (LCBH Release 2)
Used for tract-level eviction filing counts and filing rates for Chicago.
Main file: eviction_data_tract.csv

2. ACS-based tract covariates from the Chicago Evictions release
Used for poverty measures, demographic composition, and median rent.
Main file: census_data_tract.csv

3. ACS 5-year median household income (Table B19013)
Used for tract-level median household income.
Main file: ACSDT5Y2019.B19013-Data.csv

4. 2019 Census TIGER/Line tract shapefile
Used for tract-level spatial boundaries and mapping.
Main files: tl_2019_17_tract.shp, tl_2019_17_tract.shx, tl_2019_17_tract.dbf, tl_2019_17_tract.prj, tl_2019_17_tract.cpg

## Data Processing

The data processing pipeline is implemented in code/preprocessing.py.

The script:
loads tract-level eviction data from the Chicago Evictions release
filters eviction outcomes to 2019
loads tract-level ACS covariates from the Chicago Evictions release
filters census covariates to 2014-2018 5-year estimates
loads tract-level median household income from ACS table B19013
extracts tract GEOIDs and merges all datasets by tract identifier
computes neighborhood covariates including:
  poverty rate
  percent Black
  percent Latinx
  minority share
joins the merged tract-level table to the 2019 TIGER/Line tract shapefile
saves processed outputs to data/derived-data/

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
a tract-level analytic dataset for Chicago in data/derived-data/
four static visualizations in figures/
an interactive Streamlit dashboard in streamlit-app/

## Research Question

Our main research question is:
Are 2019 eviction filing rates higher in census tracts with lower income, higher poverty, and higher minority share in Chicago?
As a supporting analysis, we identify high-eviction hotspot tracts and compare their characteristics to the city baseline.