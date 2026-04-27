import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import matplotlib.pyplot as plt

# --- 1. DASHBOARD CONFIGURATION ---
st.set_page_config(page_title="RCRA Landfill Siting", layout="wide")

st.title("Geospatial Suitability Analysis for RCRA Subtitle D Landfill Siting")
st.markdown("### Putnam County, TN - Candidate Sites")
st.write("""
This interactive model identifies viable locations for solid waste facilities based on strict environmental and zoning criteria. 
The highlighted parcels possess **>30% compact clay** at a depth of at least 5 feet, sit above a **safe groundwater table** (>10ft deep), and strictly adhere to a **1,000-foot residential exclusion buffer**.
""")

# --- 2. LOAD THE DATA ---
@st.cache_data 
def load_data():
    file_path = r"C:/PhD_Research/Landfill_Project/data/outputs/putnam_suitability.geojson"
    if os.path.exists(file_path):
        gdf = gpd.read_file(file_path)
        
        # THE FIX: Find any Timestamp columns (like well dates) and convert them to plain text
        for col in gdf.columns:
            if gdf[col].dtype.name.startswith('datetime'):
                gdf[col] = gdf[col].astype(str)
                
        return gdf
    else:
        return None

candidates = load_data()
# --- 3. BUILD THE INTERACTIVE MAP ---
if candidates is not None and not candidates.empty:
    st.sidebar.success(f"Successfully loaded {len(candidates)} candidate zones.")
    
    # Center map on Putnam County
    m = folium.Map(location=[36.1627, -85.5016], zoom_start=11, tiles="CartoDB positron")

    # Define the visual style for the candidate sites (Dark Green, easily visible)
    style_function = lambda x: {
        'fillColor': '#1a9850',
        'color': '#005a32',
        'weight': 2,
        'fillOpacity': 0.7
    }

# Add the GeoJSON to the map with interactive hover tooltips
    folium.GeoJson(
        candidates,
        name="Candidate Sites",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['MUKEY'], 
            aliases=['Soil Map Unit Key:'],
            localize=True
        )
    ).add_to(m)

    # 1. Read the image directly into Python memory to bypass browser security
    img_data = plt.imread(r"C:/PhD_Research/Landfill_Project/data/outputs/flow_network.png")

    # 2. Add the DEM Flow Network Overlay using the memory data
    folium.raster_layers.ImageOverlay(
        image=img_data, 
        bounds=[[34.99944444283109, -86.00055555599346], [37.00055555609492, -84.99944444380537]],
        opacity=0.7,
        name="Surface Flow Network"
    ).add_to(m)

    # 3. Add a layer control so you can toggle the flow network on and off
    folium.LayerControl(position='topleft').add_to(m)

    # 4. Render the map in the Streamlit app (THIS MUST ALWAYS BE LAST!)
    st_folium(m, width=900, height=600)

else:
    st.error("GeoJSON not found or empty. Please check the file path from your Jupyter output.")
# --- 4. METHODOLOGY & LEGEND ---
st.sidebar.header("Suitability Criteria")
st.sidebar.markdown("""
* **Soil Profile:** >30% Clay at 5ft (SSURGO)
* **Hydrology:** >10ft Depth to Water (TDEC)
* **Zoning:** 1,000-Foot Buffer (County Assessor)
""")
