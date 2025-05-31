import streamlit as st
import pandas as pd
import tempfile
import os
import diyepw

@st.cache_data
def load_station_data():
    url = "https://opendata.dwd.de/climate_environment/CDC/help/stations_list_CLIMAT_data.txt"
    df = pd.read_csv(url, sep=';', skiprows=1, names=['WMO_ID', 'StationName', 'Latitude', 'Longitude', 'Height', 'Country'])
    df = df.dropna(subset=['WMO_ID', 'StationName', 'Country'])
    df['StationName'] = df['StationName'].str.strip()
    df['Country'] = df['Country'].str.strip()
    df['WMO_ID'] = df['WMO_ID'].astype(int)
    return df

df_stations = load_station_data()

st.title("🌍 Generate EPW File with DIYEPW")
st.write("Select a **country**, then a **city**, and the year to generate a weather EPW file.")

country = st.selectbox("Select Country", sorted(df_stations['Country'].unique()))
cities = df_stations[df_stations['Country'] == country].sort_values('StationName')
city = st.selectbox("Select City", cities['StationName'].unique())
city_row = cities[cities['StationName'] == city].iloc[0]
wmo_id = city_row['WMO_ID']
year = st.number_input("Select Year", min_value=1979, max_value=2025, value=2020)

if st.button("Generate EPW File"):
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            result = diyepw.create_amy_epw_files_for_years_and_wmos(
                years=[year],
                wmo_indices=[wmo_id],
                allow_downloads=True,
                amy_epw_dir=tmpdir
            )
            epw_path = result[year][wmo_id][1]

            if os.path.exists(epw_path):
                with open(epw_path, "rb") as f:
                    st.success(f"✅ EPW file for {city}, {country} ({year}) is ready.")
                    st.download_button("Download EPW", f.read(), file_name=os.path.basename(epw_path))
            else:
                st.error("EPW file generation failed.")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
