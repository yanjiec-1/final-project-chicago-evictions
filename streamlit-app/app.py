from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# base directory for the project: streamlit-app/
APP_DIR = Path(__file__).resolve().parent
# parent directory of the base directory: repo root
REPO_DIR = APP_DIR.parent
# derived data directory: data/derived-data/
DERIVED_DIR = REPO_DIR / "data" / "derived-data"

# set the page config
st.set_page_config(page_title="Chicago Eviction Dashboard", layout="wide")

# cache the data
@st.cache_data
def load_data():
    # load the csv file into a pandas dataframe
    df = pd.read_csv(DERIVED_DIR / "chicago_eviction_analytic_2019.csv")
    # load the json file into a json object
    with open(DERIVED_DIR / "chicago_eviction_analytic_2019.json", "r") as f:
        geojson = json.load(f)

    # make the tract column a string column
    df["tract"] = df["tract"].astype(str)

    return df, geojson

# main function to run the app
def main():
    # set the title of the app
    st.title("Chicago Eviction Filing Dashboard (2019)")
    # write the description of the app
    st.write(
        "This dashboard explores whether eviction filing rates are higher in lower-income "
        "and higher-minority census tracts in Chicago."
    )

    # load the data
    df, geojson = load_data()

    # add a sidebar header
    st.sidebar.header("Filters")

    # add a slider for the median household income
    income_min = int(df["median_household_income"].min())
    income_max = int(df["median_household_income"].max())
    income_threshold = st.sidebar.slider(
        "Maximum median household income",
        min_value=income_min,
        max_value=income_max,
        value=int(df["median_household_income"].quantile(0.75)), # default value is the 75th percentile of the median household income
        step=1000,
    )

    # add a slider for the minority share
    minority_threshold = st.sidebar.slider(
        "Minimum minority share",
        min_value=0.0,
        max_value=1.0,
        value=0.30,
        step=0.01,
    )

    # filter the data based on the income (less than or equal to the income threshold) and minority share (greater than or equal to the minority share threshold)
    filtered = df[
        (df["median_household_income"] <= income_threshold)
        & (df["minority_share"] >= minority_threshold)
    ].copy()

    # add a subheader for the filtered summary
    st.subheader("Filtered Summary")
    # create three columns
    c1, c2, c3 = st.columns(3)
    c1.metric("Tracts shown", f"{len(filtered):,}")
    c2.metric("Mean eviction rate", f"{filtered['eviction_filings_rate'].mean():.3f}")
    c3.metric("Median household income", f"${filtered['median_household_income'].median():,.0f}")

    # add a subheader for the interactive map
    st.subheader("Interactive Map")
    
    # calculate the 95th percentile of the eviction filing rate
    p95 = filtered["eviction_filings_rate"].quantile(0.95)

    # create a choropleth map
    fig_map = px.choropleth_map(
        filtered,
        geojson=geojson,
        locations="tract",
        featureidkey="properties.tract",
        color="eviction_filings_rate",
        range_color=(0, p95), # set the range of the color scale to the 95th percentile of the eviction filing rate
        hover_data={
            "tract": True,
            "eviction_filings_total": True,
            "eviction_filings_rate": ":.3f",
            "median_household_income": ":,.0f",
            "poverty_rate": ":.2%",
            "minority_share": ":.2%",
            "pct_black": ":.2%",
            "pct_latinx": ":.2%",
        },
        zoom=9.2,
        center={"lat": 41.8781, "lon": -87.6298},
        opacity=0.7,
    )
    
    # update the layout of the map
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # plot the map
    st.plotly_chart(fig_map, width="stretch")

    # add a subheader for the interactive scatter plot
    st.subheader("Interactive Scatter Plot")
    
    # create a scatter plot
    fig_scatter = px.scatter(
        filtered,
        x="median_household_income",
        y="eviction_filings_rate",
        hover_data={
            "tract": True,
            "eviction_filings_total": True,
            "poverty_rate": ":.2%",
            "minority_share": ":.2%",
            "pct_black": ":.2%",
            "pct_latinx": ":.2%",
        },
        labels={
            "median_household_income": "Median Household Income",
            "eviction_filings_rate": "Eviction Filing Rate",
        },
    )
    
    # update the layout of the scatter plot
    fig_scatter.update_layout(margin={"r": 20, "t": 20, "l": 20, "b": 20})
    # plot the scatter plot
    st.plotly_chart(fig_scatter, width="stretch")

    # add a subheader for the top tracts by eviction filing rate
    st.subheader("Top Tracts by Eviction Filing Rate")
    # create a dataframe of the top 15 tracts by eviction filing rate
    top = (
        filtered.sort_values("eviction_filings_rate", ascending=False)
        .head(15)[
            [
                "tract",
                "eviction_filings_total",
                "eviction_filings_rate",
                "median_household_income",
                "poverty_rate",
                "minority_share",
            ]
        ]
        .reset_index(drop=True)
    )
    # display the top tracts by eviction filing rate
    st.dataframe(top, width="stretch")

# main function to run the app
if __name__ == "__main__":
    main()