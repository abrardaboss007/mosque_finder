# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode
import openrouteservice as ors
import folium
import operator
from functools import reduce
from sklearn.metrics.pairwise import haversine_distances
from math import radians
import random
#----------------------------------------------------------------------------------------------
# Add tab title + Bring in CSV file and make slight modifications to it (lines 19-31)
#----------------------------------------------------------------------------------------------
# Add tab title to page
st.set_page_config(page_title="View/Search/Filter Mosques")

if 'selected_mosque_index' not in st.session_state:
    st.session_state.selected_mosque_index = None

# Bring in and modify CSV file
df1 = pd.read_csv("uk_mosques_modified.csv")

df1 = df1.replace(r'^\s*$', np.nan, regex=True)
df1 = df1.fillna(0)
df1 = df1.replace(0, "N/A")
df1["Capacity"] = pd.to_numeric(df1["Capacity"], downcast='integer', errors = "coerce")
df1["Longitude"] = pd.to_numeric(df1["Longitude"], downcast='float', errors = "coerce")
df1["Latitude"] = pd.to_numeric(df1["Latitude"], downcast='float', errors = "coerce")
df1 = df1.fillna(0)
#----------------------------------------------------------------------------------------------
# Add search bar and filters to page (lines 38-106)
#----------------------------------------------------------------------------------------------
# Search bar
search_bar = st.text_input(label = "**Search for a specific Masjid**", placeholder="e.g. East London Mosque")

if search_bar:
    filtered_df = df1[df1["Mosque Name"].str.contains(search_bar, case=False, na=False)]
    if not filtered_df.empty:
        df1 = filtered_df
    else:
        st.write("No Mosque found matching your search...")
        df1 = pd.DataFrame()

st.markdown("")
st.markdown("")
st.markdown("**Filters**")

filter_columns = st.columns(3)

# Filter for Mosque denomination
with filter_columns[0]:
    denomination_options  = ["Sunni","Shia"]
    denomination_filter = st.selectbox(label="Filter for denomination", options=denomination_options, index=None)
    if denomination_filter == "Sunni":
        df1 = df1[df1["Denomination"] == "Sunni"]
    elif denomination_filter == "Shia":
        df1 = df1[df1["Denomination"] == "Shia"]
    st.markdown("")

# Allow user to select only Mosques which have female facilities
with filter_columns[1]:
    womens_facilities_filter = st.toggle(label="Show all Mosques with Women's facilities", value=False)
    if womens_facilities_filter:
        df1 = df1[df1["Facilities for Women"] == "Yes"]
    st.markdown("")

# Geocoding filter
# Create function for calculating the distance between two coordinates
def geo_distance_vectorized(input_lat, input_long, mosque_lat, mosque_long):
    input_coord = np.array([[radians(input_lat), radians(input_long)]])
    mosque_coords = np.vstack((mosque_lat, mosque_long)).T
    mosque_coords_rad = np.radians(mosque_coords)  # convert whole array to radians
    # Calculate distance matrix
    distances = haversine_distances(input_coord, mosque_coords_rad)
    # Convert distance to km
    distances_km = distances[0] * 6371
    return distances_km

with filter_columns[2]:
    postcode_input = st.text_input(label="Enter postcode", placeholder="e.g. WC2N 6RH")
    max_distance = st.slider(label="Max distance from postcode to mosque (km)", min_value=0.0, max_value=10.0, value=None, step=0.1)

    if postcode_input:
        nomi = pgeocode.Nominatim('gb')
        postcode_lat = nomi.query_postal_code(postcode_input).latitude
        postcode_long = nomi.query_postal_code(postcode_input).longitude

        if postcode_lat is None or postcode_long is None:
            st.warning("Invalid postcode, please enter a valid UK postcode.")
        elif max_distance:
            # Compute distances for all mosques
            distances = geo_distance_vectorized(postcode_lat, postcode_long, df1["Latitude"].values, df1["Longitude"].values)
            # Filter DataFrame to only mosques within max_distance
            df1 = df1[distances <= max_distance]
            st.write(f"Found {len(df1)} mosques within {max_distance} km of {postcode_input}")
    elif max_distance and not postcode_input:
        st.info("Please enter your postcode first...")

    st.markdown("")

#----------------------------------------------------------------------------------------------
# Display CSV information on streamlit in an elegant way as well as bring in map (lines 109-205)
#----------------------------------------------------------------------------------------------
# Create pagination feature for displaying mosques
rows_per_page, columns_per_page =50, 2
mosques_per_page = rows_per_page * columns_per_page
total_number_of_mosques = len(df1)

number_of_pages = total_number_of_mosques // mosques_per_page + (1 if total_number_of_mosques % mosques_per_page > 0 else 0)

# Sidebar pagination control
st.sidebar.title("Pagination")
current_page = st.sidebar.number_input("Page:", min_value=1, max_value=number_of_pages, value=1)

st.write(f"Displaying page {current_page} of {number_of_pages}")

# Calculate start and end indices for the current page
start_index = (current_page - 1) * mosques_per_page
end_index = start_index + mosques_per_page
current_data = df1.iloc[start_index:end_index]

# Create a grid layout to display mosques
columns = st.columns(columns_per_page)

# Loop over mosques on current page and display info in columns
if st.session_state.selected_mosque_index is None:
    for i, (_, mosque) in enumerate(current_data.iterrows()):
        col = columns[i % columns_per_page]  # Cycle through columns

        # Extract fields to display
        name = mosque.get('Mosque Name')
        address = mosque.get('Address')
        city = mosque.get('City')
        postcode = mosque.get('Postcode')
        telephone = mosque.get('Telephone Number')
        capacity = mosque.get('Capacity')
        denomination = mosque.get('Denomination')
        womens_facilities = mosque.get('Facilities for Women')

        # Display Mosque information on both columns
        with col:
            with st.container(border=True, height= 500):
                st.markdown(f"### {name}")
                st.write(f"**City:** {city}")
                st.write(f"**Postcode:** {postcode}")
                st.write(f"**Telephone:** {telephone}")
                st.write(f"**Capacity:** {capacity}")
                st.write(f"**Denomination:** {denomination}")
                st.write(f"**Facilities for Women:** {womens_facilities}")
                
                directions_button = st.button(label= "Get directions", type="primary", key=f"get_directions_{mosque['Mosque Name']}_{i}")
                if directions_button:
                    if postcode_input:
                        st.session_state.selected_mosque_index = i
                    else:
                        st.warning("Please input postcode at the top")
    st.write(f"Displaying page {current_page} of {number_of_pages}")
                    
else:
    # Allow user to be able to click on specific Mosque to be able to get directions
    with columns[0]:
        with st.container(border = True, width = 300, height = 500):
            mosque = df1.iloc[st.session_state.selected_mosque_index]

            st.markdown(f"### {mosque['Mosque Name']}")
            st.write(f"**City:** {mosque['City']}")
            st.write(f"**Postcode:** {mosque['Postcode']}")
            st.write(f"**Telephone:** {mosque['Telephone Number']}")
            st.write(f"**Capacity:** {mosque['Capacity']}")
            st.write(f"**Denomination:** {mosque['Denomination']}")
            st.write(f"**Facilities for Women:** {mosque['Facilities for Women']}")
            st.markdown(
    """
    <p style="color:blue; margin:0;">blue line = travelling by foot</p>
    <p style="color:red; margin:0;">red line = travelling by car</p>
    """, 
    unsafe_allow_html=True
)
    
    # Use map API to be able to display directions to the Mosque that the user clicks on
    with columns[1]:
        api_key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM2YWVmYjliNzkwZjQ1NjViNTQ3OGRkYWYyOWMzNmNmIiwiaCI6Im11cm11cjY0In0="
        client = ors.Client(key= api_key)

        mosque_coordinates = [float(mosque["Longitude"]), float(mosque["Latitude"])]
        input_coordinates = [float(postcode_long), float(postcode_lat)]
        coords = [mosque_coordinates, input_coordinates]

        map = folium.Map(location=list(reversed(mosque_coordinates)), tiles="cartodbpositron", zoom_start=13)

        route1 = client.directions(coordinates=coords,profile='foot-walking',format='geojson')
        route2 = client.directions(coordinates=coords,profile='driving-car',format='geojson')

        waypoints1 = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route1['features'][0]['properties']['segments'][0]['steps'])))))
        waypoints2 = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route2['features'][0]['properties']['segments'][0]['steps'])))))
        
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route1['features'][0]['geometry']['coordinates']], color="blue").add_to(map)
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route2['features'][0]['geometry']['coordinates']], color="red").add_to(map)
        
        st.components.v1.html(folium.Figure().add_child(map).render(), height=500)