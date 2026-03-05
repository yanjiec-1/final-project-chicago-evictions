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

# main function to plot the bar chart of the top 10 tracts by eviction filing rate
def main():
    # load data
    df_path = DERIVED_DIR / "chicago_eviction_analytic_2019.csv"
    # read the csv file into a pandas dataframe
    df = pd.read_csv(df_path)

    # city medians for context
    chicago_income_median = df["median_household_income"].median()
    chicago_poverty_median = df["poverty_rate"].median()
    chicago_minority_median = df["minority_share"].median()

    # top 10 tracts by eviction filing rate
    top_n = 10
    top = (
        df.sort_values("eviction_filings_rate", ascending=False)
        .head(top_n)
        .copy()
    )

    # create annotation text for each tract
    top["context_label"] = top.apply(
        lambda row: (
            f"Income ${row['median_household_income']:,.0f} | "
            f"Poverty {row['poverty_rate']:.1%} | "
            f"Minority {row['minority_share']:.1%}"
        ),
        axis=1
    )
    # make the tract column a string column
    top["tract"] = top["tract"].astype(str)

    # create a bar chart
    bars = alt.Chart(top).mark_bar().encode(
            x=alt.X(
                "eviction_filings_rate:Q",
                title="Eviction Filing Rate"
            ),
            y=alt.Y(
                "tract:N",
                sort=list(top["tract"]),
                title="Census Tract"
            ),
            tooltip=[
                alt.Tooltip("tract:N", title="Tract"),
                alt.Tooltip("eviction_filings_rate:Q", title="Eviction rate", format=".3f"),
                alt.Tooltip("median_household_income:Q", title="Income", format=",.0f"),
                alt.Tooltip("poverty_rate:Q", title="Poverty", format=".1%"),
                alt.Tooltip("minority_share:Q", title="Minority share", format=".1%"),
            ],
        )

    # text labels to the right of bars
    text = alt.Chart(top).mark_text(align="left", baseline="middle", dx=5, fontSize=11).encode(
            x=alt.X("eviction_filings_rate:Q"),
            y=alt.Y("tract:N", sort=list(top["tract"])),
            text="context_label:N"
        )

    # create a chart
    chart = (bars + text).properties(
        title="Top 10 Chicago Census Tracts by Eviction Filing Rate (2019)",
        width=760,
        height=420
        ).configure_title(fontSize=18, anchor="middle").configure_axis(
            titleFontSize=13,
            labelFontSize=11,
            grid=True,
            gridColor="#e6e6e6",
            domainColor="#888888",
            tickColor="#888888"
        ).configure_view(stroke=None)

    # path to the figure: figures/plot_4_top_tracts_hotspot_context.png
    out_path = FIG_DIR / "plot_4_top_tracts_hotspot_context.png"

    # save the chart to the figures directory
    save_altair_png(chart, out_path, scale=3)
    print(f"Saved PNG: {out_path}")

    # save as HTML
    # html_path = FIG_DIR / "plot_4_top_tracts_hotspot_context.html"
    # chart.save(html_path)
    # print(f"Saved HTML: {html_path}")

    # also print city medians for reference
    print(
        f"Chicago medians — Income: ${chicago_income_median:,.0f}, "
        f"Poverty: {chicago_poverty_median:.1%}, "
        f"Minority share: {chicago_minority_median:.1%}"
    )

# main function to run the script
if __name__ == "__main__":
    main()