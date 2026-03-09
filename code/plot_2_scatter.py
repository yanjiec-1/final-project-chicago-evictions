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

# main function to plot the scatter plot of the eviction filing rate versus median household income
def main():
    # load data
    df_path = DERIVED_DIR / "chicago_eviction_analytic_2019.csv"
    df = pd.read_csv(df_path)

    # keep only the columns we need and drop missing values
    df = df[["median_household_income", "eviction_filings_rate"]].dropna().copy()

    # create tooltip label columns
    df["income_label"] = "$" + df["median_household_income"].round(0).astype(int).map("{:,}".format)
    df["eviction_rate_label"] = df["eviction_filings_rate"].round(0).astype(int).astype(str) + "%"

    # create a scatter plot
    points = alt.Chart(df).mark_circle(size=45, opacity=0.55).encode(
        x=alt.X(
            "median_household_income:Q",
            title="Median Household Income ($)",
            scale=alt.Scale(zero=False),
            axis=alt.Axis(labelExpr="'$' + format(datum.value, ',.0f')")
        ),
        y=alt.Y(
            "eviction_filings_rate:Q",
            title="Eviction Filing Rate (%)",
            scale=alt.Scale(zero=False),
            axis=alt.Axis(labelExpr="datum.value + '%'")
        ),
        tooltip=[
            alt.Tooltip("income_label:N", title="Income"),
            alt.Tooltip("eviction_rate_label:N", title="Eviction rate")
        ]
    )

    # create a linear trend line
    trend = alt.Chart(df).transform_regression(
        "median_household_income",
        "eviction_filings_rate"
    ).mark_line(size=3).encode(
        x="median_household_income:Q",
        y="eviction_filings_rate:Q"
    )

    # create a chart
    chart = (points + trend).properties(
        title="Eviction Filing Rate vs Median Household Income (Chicago Tracts, 2019)",
        width=720,
        height=480,
    ).configure_title(
        fontSize=18
    ).configure_axis(
        titleFontSize=13,
        labelFontSize=11
    )

    # path to the figure: figures/plot_2_scatter_eviction_vs_income.png
    out_path = FIG_DIR / "plot_2_scatter_eviction_vs_income.png"

    # save the chart to the figures directory
    save_altair_png(chart, out_path, scale=3)
    print(f"Saved PNG: {out_path}")

# main function to run the script
if __name__ == "__main__":
    main()