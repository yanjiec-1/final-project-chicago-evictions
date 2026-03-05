from pathlib import Path
import pandas as pd
import altair as alt
from preprocessing import save_altair_png

# base directory for the project: code/
BASE_DIR = Path(__file__).resolve().parent
# parent directory of the base directory: repo root
REPO_DIR = BASE_DIR.parent
# derived data directory: data/derived-data/
DERIVED_DIR = REPO_DIR / "data" / "derived-data"
# figures directory: figures/
FIG_DIR = REPO_DIR / "figures"

# main function to plot the boxplot of the eviction filing rate by poverty quartile
def main():
    # load data
    df_path = DERIVED_DIR / "chicago_eviction_analytic_2019.csv"
    # read the csv file into a pandas dataframe
    df = pd.read_csv(df_path)

    # create poverty quartiles
    full_labels = [
        "Q1 (Lowest Poverty)",
        "Q2",
        "Q3",
        "Q4 (Highest Poverty)"
    ]

    # create a new column of poverty quartiles
    df["poverty_quantile"] = pd.qcut(
        df["poverty_rate"],
        q=4,
        labels=full_labels,
        duplicates="drop",
    )

    # drop missing values in the plot
    df = df.dropna(subset=["poverty_quantile", "eviction_filings_rate"]).copy()

    # make the poverty quantile column a categorical column
    df["poverty_quantile"] = pd.Categorical(
        df["poverty_quantile"],
        categories=full_labels,
        ordered=True
    )

    # create a boxplot
    chart = alt.Chart(df).mark_boxplot(size=50, extent=1.5).encode(
            x=alt.X(
                "poverty_quantile:N",
                title="Poverty-Rate Quartile",
                sort=full_labels,
                axis=alt.Axis(labelAngle=0, labelFontSize=12, titleFontSize=13)
            ),
            y=alt.Y(
                "eviction_filings_rate:Q",
                title="Eviction Filing Rate",
                scale=alt.Scale(zero=True),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)
            ),
        ).properties(
            title="Eviction Filing Rate by Poverty-Rate Quartile (Chicago Tracts, 2019)",
            width=720,
            height=430
        ).configure_title(
            fontSize=18,
            anchor="middle"
        ).configure_axis(
            grid=True,
            gridColor="#e6e6e6",
            domainColor="#888888",
            tickColor="#888888"
        ).configure_view(
            stroke=None
        )

    # path to the figure: figures/plot_3_boxplot_eviction_by_poverty_quantile.png
    out_path = FIG_DIR / "plot_3_boxplot_eviction_by_poverty_quantile.png"

    # save the chart to the figures directory
    save_altair_png(chart, out_path, scale=3)
    print(f"Saved PNG: {out_path}")

    # save as HTML
    # html_path = FIG_DIR / "plot_3_boxplot_eviction_by_poverty_quantile.html"
    # chart.save(html_path)
    # print(f"Saved HTML: {html_path}")

# main function to run the script
if __name__ == "__main__":
    main()