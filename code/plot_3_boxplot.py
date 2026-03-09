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

# main function to plot the boxplot of the eviction filing rate by minority share quartile
def main():
    # load data
    df_path = DERIVED_DIR / "chicago_eviction_analytic_2019.csv"
    df = pd.read_csv(df_path)

    # required columns
    df = df.dropna(subset=["minority_share", "eviction_filings_rate"]).copy()

    # if minority_share is stored as 0.28, convert it to 28 for nicer display
    if df["minority_share"].max() <= 1:
        df["minority_share_display"] = df["minority_share"] * 100
    else:
        df["minority_share_display"] = df["minority_share"]

    # ordered minority-share quartiles
    q_labels = [
        "Q1 (Lowest minority share)",
        "Q2",
        "Q3",
        "Q4 (Highest minority share)",
    ]

    # create a new column of minority share quartiles
    df["minority_quartile"] = pd.qcut(
        df["minority_share"],
        q=4,
        labels=q_labels,
        duplicates="drop",
    )

    # drop rows with missing values in the minority quartile column
    df = df.dropna(subset=["minority_quartile"]).copy()

    # make the minority quartile column a categorical column
    df["minority_quartile"] = pd.Categorical(
        df["minority_quartile"],
        categories=q_labels,
        ordered=True,
    )

    # make a boxplot chart
    chart = alt.Chart(df).mark_boxplot(size=60, extent=1.5).encode(
        x=alt.X(
            "minority_quartile:N",
            title="Minority Share Quartile",
            sort=q_labels,
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "eviction_filings_rate:Q",
            title="Eviction Filing Rate (%)",
            scale=alt.Scale(zero=True),
            axis=alt.Axis(labelExpr="datum.value + '%'"),
        ),
        tooltip=[
            alt.Tooltip("minority_share_display:Q", title="Minority share", format=".0f"),
            alt.Tooltip("eviction_filings_rate:Q", title="Eviction rate", format=".0f"),
        ],
    ).properties(
        title="Eviction Filing Rate by Minority-Share Quartile (Chicago Tracts, 2019)",
        width=740,
        height=430,
    ).configure_title(
        fontSize=18,
        anchor="middle"
    ).configure_axis(
        titleFontSize=13,
        labelFontSize=11,
        grid=True,
        gridColor="#e6e6e6"
    ).configure_view(stroke=None)

    out_path = FIG_DIR / "plot_3_boxplot_eviction_by_minority_quartile.png"
    save_altair_png(chart, out_path, scale=3)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()