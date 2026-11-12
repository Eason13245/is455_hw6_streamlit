import streamlit as st
import pandas as pd
import altair as alt

# 1. Configure application

st.set_page_config(
    page_title="UFO Sightings Explorer",
    layout="wide"
)


# 2. Display title and introduction

st.title("UFO Sightings Explorer")


# 3. Load UFO dataset

DATA_URL = (

    "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/"

    "is445_data/main/ufo-scrubbed-geocoded-time-standardized-00.csv"

)

@st.cache_data

def load_data():

    column_names = [
        "datetime",
        "city",
        "state",
        "country",
        "shape",
        "duration_seconds",
        "duration_hours_min",
        "comments",
        "date_posted",
        "latitude",
        "longitude"

    ]

    return pd.read_csv(
        DATA_URL,
        header=None,
        names=column_names,
        low_memory=False

    )

df = load_data()


# 4. Clean and transform data

df["datetime"] = pd.to_datetime(df["datetime"], errors = "coerce")

df["year"] = df["datetime"].dt.year

df["shape"] = df["shape"].fillna("unknown")
df["shape"] = df["shape"].str.lower().str.strip()

df["state"] = df["state"].fillna("unknown")
df["state"] = df["state"].str.upper().str.strip()

df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors = "coerce")


# 5. Create interactive filters
st.header("Visualization 1: Distribution of UFO Sightings by Shape")

states = sorted(df["state"].dropna().unique().tolist())

selected_state = st.selectbox(
    "Selecxt a state:",
    ["All states"] + states
)

if selected_state == "All states":
    filtered_df = df.copy()
else:
    filtered_df = df[df["state"] == selected_state]

shape_counts = (filtered_df.groupby("shape").size().reset_index(name = "count").sort_values("count", ascending = False))

top_shapes = shape_counts.head(6).copy()

other_count = shape_counts.iloc[6:]["count"].sum()

if other_count > 0 :
    top_shapes = pd.concat(
        [
            top_shapes,
            pd.DataFrame({
                "shape": ["other categories"],
                "count": [other_count]
            })
        ],
        ignore_index=True
    )
    

# 6. Visualization 1: Donut chart
donut_chart = (
    alt.Chart(top_shapes)
    .mark_arc(innerRadius = 90)
    .encode(
        theta = alt.Theta("count:Q", title = "Number of Reports"),
        color = alt.Color("shape:N", title = "UFO Shape"),
        tooltip = [
            alt.Tooltip("shape:N", title = "UFO Shape"),
            alt.Tooltip("count:Q", title = "Reports", format = ",")
        ]
    )
    .properties(
        width = 500,
        height = 400,
        title = "Distribution of Reported UFO Shapes"
    )
)

st.altair_chart(donut_chart, use_container_width= True)


# 7. Explanation for Visualization 1
st.markdown("The donut chart (first visualization) displays the distribution of reported UFO shapes across different states. For this graph, I show only the six most frequently reported shapes, while the remaining categories are grouped together to improve readability. The size of each segment changes based on the number of sightings of its corresponding shape, and each segment uses a different color for distinction. The interactivity property is a state-selection dropdown that lets users compare distributions across locations. I would also add percentage labels to each segment and potentially an option to compare multiple segments simultaneously. ")

# 8. Visualization 2: Heatmap
st.header("Visualization 2: UFO Sighting Duration Over Time")

scatter_df = df.dropna(subset = ["year", "duration_seconds"]).copy()
scatter_df = scatter_df[scatter_df["duration_seconds"]>0].copy()


min_year = int(scatter_df["year"].min())
max_year = int(scatter_df["year"].max())

selected_years = st.slider(
    "Select a year range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)


scatter_filtered = scatter_df[
    scatter_df["year"].between(
        selected_years[0],
        selected_years[1]
    )
].copy()

scatter_chart = (
    alt.Chart(scatter_filtered)
    .mark_circle(size=35, opacity=0.35)
    .encode(
        x=alt.X(
            "year:Q",
            title="Year of Sighting",
            scale=alt.Scale(domain=[selected_years[0], selected_years[1]],nice=False),
            axis=alt.Axis(format="d")
        ),
        y=alt.Y(
            "duration_seconds:Q",
            title="Reported Duration (Seconds)",
            scale=alt.Scale(type="log")
        ),
        color=alt.Color(
            "shape:N",
            title="UFO Shape"
        ),
        tooltip=[
            alt.Tooltip("year:Q", title="Year", format=".0f"),
            alt.Tooltip("shape:N", title="UFO Shape"),
            alt.Tooltip(
                "duration_seconds:Q",
                title="Duration (Seconds)",
                format=",.1f"
            )
        ]
    )
    .properties(
        height=450,
        title="Reported UFO Sighting Duration by Year"
    )
)

st.altair_chart(scatter_chart, use_container_width=True)
# 9. Explanation for Visualization 2
st.markdown("This scatter plot (second visualization) investigates the relationship between the year of a UFO sighting and its reported duration. The X-axis represents the sighting year, while the Y-axis displays duration in seconds, using a logarithmic scale to accommodate large differences in reported duration. Each point displayed on the scatter plot represents an individual report, and colors represent different UFO shapes. A year-range slider allows users to interact and select the specific periods. If I had more time, I would allow users to select reported durations by state to improve investigability. ")

# 10. Explain differences from HW5
st.markdown("In this project, I used a different dataset and different visualization types than in Homework 5. In Homework 5, I applied BFRO reports using a horizontal bar chart and an interactive line chart; in contrast, this project utilized UFO sightings with a donut chart and a scatter plot. Both visualizations and their interactivity were developed specifically for this project rather than reusing plots from previous assignments. ")