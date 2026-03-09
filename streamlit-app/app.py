from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# base directory for the project: streamlit-app/
APP_DIR = Path(__file__).resolve().parent
# parent directory of the app directory: repo root
REPO_DIR = APP_DIR.parent
# derived data directory: data/derived-data/
DERIVED_DIR = REPO_DIR / "data" / "derived-data"

# set the page config
st.set_page_config(page_title="Chicago Eviction Dashboard", layout="wide")

# cache the data
@st.cache_data
# function to load the data
def load_data():
    # load the csv file into a pandas dataframe
    df = pd.read_csv(DERIVED_DIR / "chicago_eviction_analytic_2019.csv")
    # load the json file into a python dictionary
    with open(DERIVED_DIR / "chicago_eviction_analytic_2019.json", "r") as f:
        geojson = json.load(f)

    # make the tract column a string column
    df["tract"] = df["tract"].astype(str)

    return df, geojson

# main function to run the app
def main():
    # write the title of the dashboard
    st.title("Chicago Eviction Filing Dashboard (2019)")
    # write the description of the dashboard
    st.write(
        "This dashboard explores whether eviction filing rates are higher in lower-income "
        "and higher-minority census tracts in Chicago. Use the controls to explore patterns "
        "and inspect extreme tracts."
    )

    # load the data
    df, geojson = load_data()

    # sidebar filters
    st.sidebar.header("Filters")

    # income filter
    income_min = int(df["median_household_income"].min())
    income_max = int(df["median_household_income"].max())
    income_range = st.sidebar.slider(
        "Median household income range",
        min_value=income_min,
        max_value=income_max,
        value=(income_min, int(df["median_household_income"].quantile(0.90))), # default value is the 90th percentile
        step=1000,
    )

    # minority share range
    minority_range = st.sidebar.slider(
        "Minority share range",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0), # default value is from 0.0 to 1.0
        step=0.01,
    )

    # denominator filter to check for stability
    # set the default value to the 95th percentile of the renter households
    renters_max = int(df["housing_units_rental"].quantile(0.95))
    min_renters = st.sidebar.slider(
        "Minimum renter households (stability filter)",
        min_value=0,
        max_value=max(100, renters_max),
        value=200, # default value is 200
        step=50,
    )

    # apply filters to the dataframe
    filtered = df[
        (df["median_household_income"].between(income_range[0], income_range[1]))
        & (df["minority_share"].between(minority_range[0], minority_range[1]))
    ].copy()

    # apply the denominator filter to the filtered dataframe
    filtered = filtered[filtered["housing_units_rental"] >= min_renters].copy()

    # summary metrics
    st.subheader("Filtered Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tracts shown", f"{len(filtered):,}")
    c2.metric("Mean eviction rate", f"{filtered['eviction_filings_rate'].mean():.3f}")
    c3.metric("Median income", f"${filtered['median_household_income'].median():,.0f}")
    c4.metric("Median minority share", f"{filtered['minority_share'].median():.1%}")

    # extreme tract check
    st.subheader("Extreme Tract Check")
    top1 = df.sort_values("eviction_filings_rate", ascending=False).head(1).copy()

    # columns to show in the table
    show_cols = [
        "tract",
        "eviction_filings_rate",
        "eviction_filings_total",
        "housing_units_rental",
        "median_household_income",
        "poverty_rate",
        "minority_share",
    ]
    # keep only the columns that are in the dataframe
    show_cols = [c for c in show_cols if c in df.columns]
    # write the highest eviction filing rate tract in the dataset
    st.write("Highest eviction filing rate tract in the dataset (2019):")
    # write the table of the highest eviction filing rate tract in the dataset
    st.dataframe(top1[show_cols], width="stretch")

    # note for interpretation of the extreme tract check
    st.caption(
        "Note: Very high eviction filing rates can occur when renter-household denominators are small. "
        "Use the stability filter in the sidebar to focus on tracts with larger denominators."
    )

    # interactive map
    st.subheader("Interactive Map")

    # use p95 to avoid one extreme tract dominating the color scale
    if len(filtered) > 0:
        p95 = filtered["eviction_filings_rate"].quantile(0.95)
    else:
        p95 = 1.0 # default value is 1.0

    # create a choropleth map
    fig_map = px.choropleth_map(
        filtered,
        geojson=geojson,
        locations="tract",
        featureidkey="properties.tract",
        color="eviction_filings_rate",
        range_color=(0, p95),
        hover_data={
            "tract": True,
            "eviction_filings_total": True,
            "eviction_filings_rate": ":.3f",
            "median_household_income": ":,.0f",
            "poverty_rate": ":.2%",
            "minority_share": ":.2%",
            "pct_black": ":.2%",
            "pct_latinx": ":.2%",
            "housing_units_rental": True,
        },
        zoom=9.2,
        center={"lat": 41.8781, "lon": -87.6298},
        opacity=0.7,
    )
    # update the layout of the choropleth map
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # plot the choropleth map
    st.plotly_chart(fig_map, width="stretch")

    # interactive scatter with selectable x-variable
    st.subheader("Interactive Scatter")

    # select the x-axis variable from three options
    x_choice = st.selectbox(
        "Choose x-axis variable",
        options=[
            "median_household_income",
            "poverty_rate",
            "minority_share",
        ],
        format_func=lambda x: {
            "median_household_income": "Median Household Income",
            "poverty_rate": "Poverty Rate",
            "minority_share": "Minority Share",
        }[x],
    )

    # set the label for the x-axis variable
    x_label = {
        "median_household_income": "Median Household Income (ACS 5-year, B19013)",
        "poverty_rate": "Poverty Rate",
        "minority_share": "Minority Share",
    }[x_choice]

    # create a scatter plot
    fig_scatter = px.scatter(
        filtered,
        x=x_choice,
        y="eviction_filings_rate",
        hover_data={
            "tract": True,
            "eviction_filings_total": True,
            "housing_units_rental": True,
            "median_household_income": ":,.0f",
            "poverty_rate": ":.2%",
            "minority_share": ":.2%",
        },
        labels={
            x_choice: x_label,
            "eviction_filings_rate": "Eviction Filing Rate",
        },
    )
    # update the layout of the scatter plot
    fig_scatter.update_layout(margin={"r": 20, "t": 20, "l": 20, "b": 20})
    # plot the scatter plot
    st.plotly_chart(fig_scatter, width="stretch")

    # top tracts table
    st.subheader("Top Tracts by Eviction Filing Rate (Filtered)")
    # create a dataframe of the top 15 tracts by eviction filing rate
    top = (
        filtered.sort_values("eviction_filings_rate", ascending=False)
        .head(15)[show_cols]
        .reset_index(drop=True)
    )
    # write the table of the top 15 tracts by eviction filing rate
    st.dataframe(top, width="stretch")

# main function to run the app
if __name__ == "__main__":
    main()