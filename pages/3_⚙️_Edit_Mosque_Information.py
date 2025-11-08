# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode
import random

#----------------------------------------------------------------------------------------------
# Add tab title + Bring in CSV file (lines 14-39)
#----------------------------------------------------------------------------------------------
# Add tab title
st.set_page_config(page_title="Edit Mosques")

# Initialise session state DataFrame once
if 'df3' not in st.session_state:
    try:
        st.session_state.df3 = pd.read_csv("uk_mosques_modified.csv")
    except FileNotFoundError:
        st.session_state.df3 = pd.DataFrame()  

df3 = st.session_state.df3.copy()

# Initialise editing state
if 'editing_mosque' not in st.session_state:
    st.session_state.editing_mosque = None

#----------------------------------------------------------------------------------------------
# Add search bar and pagination feature (lines 33-106)
#----------------------------------------------------------------------------------------------
# Search bar
search_bar = st.text_input(label="**Search for a specific Masjid to edit**", placeholder="e.g. East London Mosque")

if search_bar:
    # Display Mosque if Mosque exits
    filtered_df = df3[df3["Mosque Name"].str.contains(search_bar, case=False, na=False)]
    if not filtered_df.empty:
        df3 = filtered_df
    else:
        st.write("No Mosque found matching your search...")
        df3 = pd.DataFrame()

# Pagination setup
rows_per_page, columns_per_page = 50, 2
mosques_per_page = rows_per_page * columns_per_page
total_number_of_mosques = len(df3)
number_of_pages = total_number_of_mosques // mosques_per_page + (1 if total_number_of_mosques % mosques_per_page > 0 else 0)

st.sidebar.title("Pagination")
current_page = st.sidebar.number_input("Page:", min_value=1, max_value=max(number_of_pages,1), value=1)
start_index = (current_page - 1) * mosques_per_page
end_index = start_index + mosques_per_page
current_data = df3.iloc[start_index:end_index]

columns = st.columns(columns_per_page)

# Pagination
for idx, (_, mosque) in enumerate(current_data.iterrows()):
    col = columns[idx % columns_per_page]  # Cycle through columns

    # Extract fields to display
    name = mosque.get('Mosque Name')
    address = mosque.get('Address')
    city = mosque.get('City')
    postcode = mosque.get('Postcode')
    telephone = mosque.get('Telephone Number')
    capacity = mosque.get('Capacity')
    denomination = mosque.get('Denomination')
    womens_facilities = mosque.get('Facilities for Women')

    with col:
        with st.container(border = True, height = 500):
            st.markdown(f"### {name}")
            st.write(f"**Address:** {address}")
            st.write(f"**City:** {city}")
            st.write(f"**Postcode:** {postcode}")
            st.write(f"**Telephone:** {telephone}")
            st.write(f"**Capacity:** {capacity}")
            st.write(f"**Denomination:** {denomination}")
            st.write(f"**Facilities for Women:** {womens_facilities}")

            if st.button("Edit Information", type='primary', key=f"edit_{idx}"):
                st.session_state.editing_mosque = idx

            if st.session_state.editing_mosque == idx:
                with st.form(f"form_{idx}"):
                    new_name = st.text_input("Mosque Name", name)
                    new_address = st.text_input("Address", address)
                    new_city = st.text_input("City", city)
                    new_postcode = st.text_input("Postcode", postcode)
                    new_telephone = st.text_input("Telephone Number", telephone)
                    new_capacity = st.text_input("Capacity", capacity)
                    new_denomination = st.text_input("Denomination", denomination)
                    new_womens = st.text_input("Facilities for Women", womens_facilities)

                    submitted = st.form_submit_button("Submit")
                    cancel = st.form_submit_button("Cancel")

                    if submitted:
                        # Update dataframe
                        st.session_state.df3.at[idx, 'Mosque Name'] = new_name
                        st.session_state.df3.at[idx, 'City'] = new_city
                        st.session_state.df3.at[idx, 'Postcode'] = new_postcode
                        st.session_state.df3.at[idx, 'Telephone Number'] = new_telephone
                        st.session_state.df3.at[idx, 'Capacity'] = new_capacity
                        st.session_state.df3.at[idx, 'Denomination'] = new_denomination
                        st.session_state.df3.at[idx, 'Facilities for Women'] = new_womens

                        st.success("Mosque information updated successfully!")
                        st.info("Please refresh this page if you want to be able to view the Mosque on the other pages!")
                        st.session_state.editing_mosque = None
                    elif cancel:
                        st.info("Edit cancelled")
                        st.session_state.editing_mosque = None

# Optionally add a save to CSV button
if st.button("Save changes to CSV"):
    st.session_state.df3.to_csv("uk_mosques_modified.csv", index=False)