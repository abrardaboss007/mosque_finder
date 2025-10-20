# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode
from sklearn.metrics.pairwise import haversine_distances
from math import radians
#----------------------------------------------------------------------------------------------
# Add tab title + Bring in CSV file and make slight modifications to it (lines 16-21)
#----------------------------------------------------------------------------------------------
# Add tab title to page
st.set_page_config(page_title="View/Search/Filter Mosques")


df1 = pd.read_csv("uk_mosques_modified.csv")

df1 = df1.replace(r'^\s*$', np.nan, regex=True)
df1 = df1.fillna(0)
df1 = df1.replace(0, "N/A")
df1["Capacity"] = pd.to_numeric(df1["Capacity"], downcast='integer', errors = "coerce")

#----------------------------------------------------------------------------------------------
# Add search bar and filters to page (lines 26-58)
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

# Filter for denomination
with filter_columns[0]:
    denomination_options  = ["Sunni","Shia"]
    denomination_filter = st.selectbox(label="Filter for denomination", options=denomination_options, index=None)
    if denomination_filter == "Sunni":
        df1 = df1[df1["Denomination"] == "Sunni"]
    elif denomination_filter == "Shia":
        df1 = df1[df1["Denomination"] == "Shia"]
    st.markdown("")

# Allow user to select only mosques which have female facilities
with filter_columns[1]:
    womens_facilities_filter = st.toggle(label="Show all Mosques with Women's facilities", value=False)
    if womens_facilities_filter:
        df1 = df1[df1["Facilities for Women"] == "Yes"]
    st.markdown("")

# Geocoding filter
# Create function for calculating the distance between two coordinates
# def geo_distance(input_lat, input_long, mosque_lat, mosque_long):
#     input_coordinates = [radians(input_lat), radians(input_long)]
#     mosque_coordinates = [radians(mosque_lat), radians(mosque_long)]
#     distance = haversine_distances([input_coordinates, mosque_coordinates])
#     distance = distance * 6371
#     return abs(distance[1,0])
from math import radians
from sklearn.metrics.pairwise import haversine_distances
import numpy as np

def geo_distance_vectorized(input_lat, input_long, mosque_lats, mosque_longs):
    # Convert all degrees to radians:
    input_coord = np.array([[radians(input_lat), radians(input_long)]])
    mosque_coords = np.vstack((mosque_lats, mosque_longs)).T
    mosque_coords_rad = np.radians(mosque_coords)  # convert whole array to radians
    # Calculate distance matrix
    distances = haversine_distances(input_coord, mosque_coords_rad)
    # distances are in radians, multiply by Earth radius in km to get km
    distances_km = distances[0] * 6371
    return distances_km

# with filter_columns[2]:
#     postcode_input = st.text_input(label="Enter max distance between postcode from Mosque", placeholder="e.g. WC2N 6RH")
#     geocode_slider = st.slider(label="Max distance between postcode from Mosque (km)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
#     geo_filter_check = st.checkbox(label="Activate geocode filter")
#     if geocode_slider:
#         if postcode_input:
#             nomi = pgeocode.Nominatim('gb')
#             postcode_lat = nomi.query_postal_code(postcode_input).latitude
#             postcode_long = nomi.query_postal_code(postcode_input).longitude
#             distance = geo_distance(postcode_lat, postcode_long, df1["Latitude"], df1["Longitude"])
#             if geo_filter_check:
#                 if distance <= geocode_slider:
#                     df1 = 

#         else:
#             st.write("Please enter your postcode first...")

with filter_columns[2]:
    postcode_input = st.text_input(label="Enter postcode", placeholder="e.g. WC2N 6RH")
    max_distance = st.slider(label="Max distance from postcode to mosque (km)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    geo_filter_check = st.checkbox(label="Activate geocode filter")

    if geo_filter_check:
        if postcode_input:
            nomi = pgeocode.Nominatim('gb')
            postcode_lat = nomi.query_postal_code(postcode_input).latitude
            postcode_long = nomi.query_postal_code(postcode_input).longitude

            if postcode_lat is None or postcode_long is None:
                st.warning("Invalid postcode, please enter a valid UK postcode.")
            else:
                # Compute distances for all mosques
                distances = geo_distance_vectorized(postcode_lat, postcode_long, df1["Latitude"].values, df1["Longitude"].values)
                # Filter DataFrame to only mosques within max_distance
                df1 = df1[distances <= max_distance]

                st.write(f"Found {len(df1)} mosques within {max_distance} km of {postcode_input}")
                
        else:
            st.info("Please enter your postcode first...")
    st.markdown("")
#----------------------------------------------------------------------------------------------
# Display CSV information on streamlit in an elegant way (lines 60-106)
#----------------------------------------------------------------------------------------------
# Create pagination feature for displaying mosques
rows_per_page, columns_per_page =33, 3
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
for i, (_, mosque) in enumerate(current_data.iterrows()):
    col = columns[i % columns_per_page]  # Cycle through columns

    # Extract fields to display
    name = mosque.get('Mosque Name')
    city = mosque.get('City')
    postcode = mosque.get('Postcode')
    telephone = mosque.get('Telephone Number')
    capacity = mosque.get('Capacity')
    denomination = mosque.get('Denomination')
    womens_facilities = mosque.get('Facilities for Women')

    with col:
        with st.container(border=True, height= 500):
            st.markdown(f"### {name}")
            st.write(f"**City:** {city}")
            st.write(f"**Postcode:** {postcode}")
            st.write(f"**Telephone:** {telephone}")
            st.write(f"**Capacity:** {capacity}")
            st.write(f"**Denomination:** {denomination}")
            st.write(f"**Facilities for Women:** {womens_facilities}")

# Display footer with page info
st.write(f"Displaying page {current_page} of {number_of_pages}")