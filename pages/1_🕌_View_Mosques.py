# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st

# Add tab title to page
st.set_page_config(page_title="View/Search/Filter Mosques")
df1 = pd.read_csv("uk_mosques_modified.csv")
#----------------------------------------------------------------------------------------------
# Add search bar and filters to page (lines 13-35)
#----------------------------------------------------------------------------------------------
# Search bar
search_bar = st.text_input(label="Search for a specific Masjid", placeholder="e.g. East London Mosque")

# Filter for denomination
denomination_options  = ["Sunni","Shia"]
st.selectbox(label="Filter for denomination", options=denomination_options, index=None)

# Allow user to select only mosques which have female facilities
#st.radio("Only show Mosques which have female facilities", options=["Yes", "Yes, as well as ones in which there is a chance", "Reset"], index=None)
st.toggle(label="Only show Mosques with womens facilities", value=False)
# Add slider for Geocoding filter
postcode_input = st.text_input(label="Enter starting postcode", placeholder="e.g. WC2N 6RH")
st.slider(label="Max distance between postcode from Mosque (km)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
#----------------------------------------------------------------------------------------------
# Display CSV information on streamlit in an elegant way (lines 18-65)
#----------------------------------------------------------------------------------------------
# Bring in CSV file and make slight modifications to it
#df1 = pd.read_csv("uk_mosques_modified.csv")
df1 = df1.replace(r'^\s*$', np.nan, regex=True)
df1 = df1.fillna(0)
df1 = df1.replace(0, "N/A")
df1["Capacity"] = pd.to_numeric(df1["Capacity"], downcast='integer', errors = "coerce")


# Create pagination feature for displaying mosques
rows_per_page, columns_per_page =33, 3
mosques_per_page = rows_per_page * columns_per_page
total_number_of_mosques = len(df1)

number_of_pages = total_number_of_mosques // mosques_per_page + (1 if total_number_of_mosques % mosques_per_page > 0 else 0)

# Sidebar pagination control
st.sidebar.title("Pagination")
current_page = st.sidebar.number_input("Page:", min_value=1, max_value=number_of_pages, value=1)

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
    new_one = mosque.get("Capacity_For_Calc")

    with col:
        with st.container(border=True, height= 500):
            st.markdown(f"### {name}")
            st.write(f"**City:** {city}")
            st.write(f"**Postcode:** {postcode}")
            st.write(f"**Telephone:** {telephone}")
            st.write(f"**Capacity:** {capacity}")
            st.write(f"**Denomination:** {denomination}")
            st.write(f"**Facilities for Women:** {womens_facilities}")
            st.write(f"{new_one}")

# Display footer with page info
st.write(f"Displaying page {current_page} of {number_of_pages}")

search_bar = st.text_input(label="Search for a specific Masjid", placeholder="e.g. East London Mosque")
