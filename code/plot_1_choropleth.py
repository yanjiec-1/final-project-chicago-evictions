from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from preprocessing import save_altair_png

# base directory for the project: code/
BASE_DIR = Path(__file__).resolve().parent
# parent directory of the base directory: repo root
REPO_DIR = BASE_DIR.parent
# derived data directory: data/derived-data/
DERIVED_DIR = REPO_DIR / "data" / "derived-data"
# figures directory: figures/
FIG_DIR = REPO_DIR / "figures"
# create the figures directory if it doesn't exist
FIG_DIR.mkdir(parents=True, exist_ok=True)

# main function to plot the choropleth map of the eviction filing rate
def main():
    # load processed tract-level spatial dataset
    gdf_path = DERIVED_DIR / "chicago_eviction_analytic_2019.geojson"
    # read the geojson file into a geopandas dataframe
    gdf = gpd.read_file(gdf_path)

    # create quintile labels
    quintile_labels = [
        "Q1 (Lowest)",
        "Q2",
        "Q3",
        "Q4",
        "Q5 (Highest)"
    ]

    # create a new column of eviction filing rate quintiles with the quintile labels
    gdf["rate_quantile"] = pd.qcut(
        gdf["eviction_filings_rate"],
        q=5,
        labels=quintile_labels,
        duplicates="drop"
    )

    # make the rate_quantile column a categorical column
    gdf["rate_quantile"] = pd.Categorical(
        gdf["rate_quantile"],
        categories=quintile_labels,
        ordered=True
    )

    # create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    # plot the choropleth map of the eviction filing rate
    gdf.plot(
        column="rate_quantile",
        categorical=True,
        cmap="GnBu",
        legend=True,
        linewidth=0.25,
        edgecolor="#c7c7c7", # light gray borders
        ax=ax,
        legend_kwds={"title": "Eviction Rate Quintile"} # legend title
    )

    # set the title and font size
    ax.set_title(
        "Eviction Filing Rate Quintiles Across Chicago Census Tracts (2019)",
        fontsize=15,
        pad=14
    )
    ax.set_axis_off()

    plt.tight_layout()
    # path to the figure: figures/plot_1_choropleth_eviction_rate_2019.png
    out_path = FIG_DIR / "plot_1_choropleth_eviction_rate_2019.png"
    # save the figure to the figures directory
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    # print the saved figure
    print(f"Saved: {out_path}")

# main function to run the script
if __name__ == "__main__":
    main()