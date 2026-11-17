
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# =====================================
# KONFIGURASI WEBSITE
# =====================================

st.set_page_config(
    page_title="Seoul Bike | Urban Mobility",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# MEMANGGIL CSS
# =====================================

with open("style.css", "r", encoding="utf-8") as file:
    css = file.read()

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True
)

# =====================================
# LOAD DATASET
# =====================================

@st.cache_data
def load_data():
    data = pd.read_csv(
        "SeoulBikeData.csv",
        encoding="latin1"
    )

    return data


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "Dataset tidak ditemukan! "
        "Pastikan SeoulBikeData.csv berada di folder yang sama."
    )
    st.stop()

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.stop()


# =====================================
# MEMERIKSA KOLOM DATASET
# =====================================

required = [
    "Rented Bike Count",
    "Hour",
    "Temperature(°C)",
    "Humidity(%)",
    "Rainfall(mm)",
    "Seasons"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Kolom berikut tidak ditemukan: {missing}")
    st.stop()

# Ubah kolom angka menjadi numerik
for col in required:
    if col != "Seasons":
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required)


# =====================================
# SIDEBAR NAVIGATION
# =====================================

st.sidebar.markdown("# 🚲 SEOUL BIKE")
st.sidebar.caption("URBAN MOBILITY ANALYTICS")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MAIN MENU",
    [
        "Overview",
        "Data Explorer",
        "Rental Analytics",
        "About Project"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### LOCATION")
st.sidebar.write("📍 Seoul, South Korea")
st.sidebar.write("서울특별시")

st.sidebar.markdown("---")
st.sidebar.caption("POWERED BY PYTHON & STREAMLIT")


# =====================================
# OVERVIEW
# =====================================

if menu == "Overview":

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    components.html(
        html,
        height=470,
        scrolling=False
    )

    st.markdown('<div id="dashboard"></div>',
                unsafe_allow_html=True)

    st.markdown("## Seoul Mobility Overview")

    st.markdown(
        '<p class="section-subtitle">'
        'A quick look at bicycle rental activity in Seoul.'
        '</p>',
        unsafe_allow_html=True
    )

    # STATISTIK
    total = df["Rented Bike Count"].sum()
    average = df["Rented Bike Count"].mean()
    maximum = df["Rented Bike Count"].max()
    temperature = df["Temperature(°C)"].mean()

    a, b, c, d = st.columns(4)

    a.metric("TOTAL RENTALS", f"{total:,.0f}")
    b.metric("AVERAGE RENTALS", f"{average:,.0f}")
    c.metric("MAX RENTALS", f"{maximum:,.0f}")
    d.metric("AVG TEMPERATURE", f"{temperature:.1f} °C")

    st.markdown("---")

    st.markdown("## Rental Overview")

    seasons = ["All Seasons"] + sorted(
        df["Seasons"].dropna().unique().tolist()
    )

    selected_season = st.selectbox(
        "Select season",
        seasons
    )

    filtered = df.copy()

    if selected_season != "All Seasons":
        filtered = filtered[
            filtered["Seasons"] == selected_season
        ]

    left, right = st.columns(2)

    with left:

        st.markdown("### Rental by Hour")

        hourly = (
            filtered.groupby("Hour")["Rented Bike Count"]
            .mean()
            .sort_index()
        )

        st.line_chart(hourly)

    with right:

        st.markdown("### Rental by Season")

        seasonal = (
            df.groupby("Seasons")["Rented Bike Count"]
            .mean()
        )

        st.bar_chart(seasonal)

    st.markdown("---")

    st.markdown("## Dataset Preview")

    st.dataframe(
        filtered.head(10),
        use_container_width=True
    )

    st.caption(
        f"Showing {len(filtered):,} records"
    )


# =====================================
# DATA EXPLORER
# =====================================

elif menu == "Data Explorer":

    st.title("Dataset Explorer")

    st.write(
        "Explore the historical Seoul Bike Sharing Demand dataset."
    )

    a, b = st.columns(2)

    a.metric("TOTAL ROWS", f"{len(df):,}")
    b.metric("TOTAL COLUMNS", len(df.columns))

    st.markdown("---")

    st.subheader("Dataset Information")

    st.dataframe(
        df.describe(include="all").transpose(),
        use_container_width=True
    )

    st.subheader("Complete Dataset")

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "SeoulBikeData.csv",
        "text/csv"
    )


# =====================================
# RENTAL ANALYTICS
# =====================================

elif menu == "Rental Analytics":

    st.title("Rental Analytics")

    st.write(
        "Analyze how weather and time relate to bicycle rentals."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Temperature Analysis")

        temp = (
            df.groupby("Temperature(°C)")["Rented Bike Count"]
            .mean()
        )

        st.line_chart(temp)

    with col2:

        st.subheader("Humidity Analysis")

        humidity = (
            df.groupby("Humidity(%)")["Rented Bike Count"]
            .mean()
        )

        st.line_chart(humidity)

    st.markdown("---")

    st.subheader("Weather and Rental Comparison")

    weather = df.groupby("Seasons")[
        ["Rented Bike Count", "Rainfall(mm)", "Snowfall (cm)"]
    ].mean()

    st.dataframe(
        weather,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Rental Simulation")

    st.write(
        "Choose conditions to find similar historical records."
    )

    with st.form("simulation_form"):

        hour = st.slider(
            "Hour",
            0, 23, 8
        )

        season = st.selectbox(
            "Season",
            sorted(df["Seasons"].dropna().unique())
        )

        temperature = st.slider(
            "Temperature (°C)",
            float(df["Temperature(°C)"].min()),
            float(df["Temperature(°C)"].max()),
            float(df["Temperature(°C)"].median())
        )

        submitted = st.form_submit_button(
            "RUN SIMULATION",
            use_container_width=True
        )

    if submitted:

        similar = df[
            (df["Hour"] == hour) &
            (df["Seasons"] == season)
        ].copy()

        if not similar.empty:

            similar["Difference"] = (
                similar["Temperature(°C)"] - temperature
            ).abs()

            similar = similar.sort_values("Difference")

            result = similar.head(20)[
                "Rented Bike Count"
            ].mean()

            st.success("Simulation completed!")

            st.metric(
                "Average Rentals in Similar Records",
                f"{result:,.0f} bikes"
            )

            st.info(
                "This result is calculated from similar historical "
                "records. It is not a trained ML prediction."
            )

            st.dataframe(
                similar.head(10),
                use_container_width=True
            )

        else:

            st.warning("No matching records were found.")


# =====================================
# ABOUT PROJECT
# =====================================

elif menu == "About Project":

    st.title("About Seoul Bike")

    st.write(
        "서울 자전거 공유 시스템"
    )

    st.markdown("""
    ### Seoul Bike Sharing Demand

    Seoul Bike is a data analysis project that explores
    public bicycle rental activity in Seoul, South Korea.

    This project focuses on understanding how time,
    temperature, humidity, rainfall, snowfall, and seasons
    relate to bicycle rental activity.

    ### Technologies

    - Python
    - Streamlit
    - HTML
    - CSS
    - Pandas
    - Scikit-learn

    ### Project Goals

    1. Explore the Seoul Bike dataset.
    2. Visualize bicycle rental statistics.
    3. Understand rental patterns.
    4. Build an interactive data dashboard.
    """)

    st.info(
        "This website is an educational data analytics project."
    )


# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:15px;">
        <h4 style="color:#65bdff;">SEOUL BIKE ANALYTICS</h4>
        <p>서울 · SOUTH KOREA</p>
        <p style="font-size:11px;">
        Urban Mobility Dashboard © 2026
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
