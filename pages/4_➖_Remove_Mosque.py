# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode

st.title("Hey Ed! Remove mosques here")
st.set_page_config(page_title="View/Search/Filter Mosques")

# Initialize session state DataFrame once
if 'df4' not in st.session_state:
    try:
        st.session_state.df4 = pd.read_csv("uk_mosques_modified.csv")
    except FileNotFoundError:
        st.session_state.df4 = pd.DataFrame()  # fallback to empty if file missing

df4 = st.session_state.df4.copy()

# Search bar
search_bar = st.text_input(label="**Search for a specific Masjid to remove**", placeholder="e.g. East London Mosque")

if search_bar:
    filtered_df = df4[df4["Mosque Name"].str.contains(search_bar, case=False, na=False)]
    if not filtered_df.empty:
        df4 = filtered_df
    else:
        st.write("No Mosque found matching your search...")
        df4 = pd.DataFrame()

# Pagination setup
rows_per_page, columns_per_page = 50, 2
mosques_per_page = rows_per_page * columns_per_page
total_number_of_mosques = len(df4)
number_of_pages = total_number_of_mosques // mosques_per_page + (1 if total_number_of_mosques % mosques_per_page > 0 else 0)
st.sidebar.title("Pagination")
current_page = st.sidebar.number_input("Page:", min_value=1, max_value=max(number_of_pages,1), value=1)
start_index = (current_page - 1) * mosques_per_page
end_index = start_index + mosques_per_page
current_data = df4.iloc[start_index:end_index]

columns = st.columns(columns_per_page)

# Initialize the removal target mosque name in session_state if not present
if 'remove_mosque_name' not in st.session_state:
    st.session_state.remove_mosque_name = None

# Display mosques in grid with remove button and confirmation form inside container
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
            remove_button = st.button(label = "Remove Mosque", type = "primary", key = f"{i}")
            if remove_button:
                st.session_state.remove_mosque_name = name

            # Show confirmation form inside this mosque’s container if it was clicked
            if st.session_state.remove_mosque_name == name:
                with st.form(key=f"confirm_removal_form_{i}", clear_on_submit=True):
                    user_validation = st.text_input(
                        f'Please type exactly: "I am absolutely sure that I would like to remove {name}"'
                    )
                    submit_button = st.form_submit_button("Remove mosque")

                    if submit_button:
                        if user_validation == f"I am absolutely sure that I would like to remove {name}":
                            # Remove mosque from session state dataframe
                            st.session_state.df4 = st.session_state.df4[st.session_state.df4['Mosque Name'] != name]
                            # Save updated dataframe to CSV
                            st.session_state.df4.to_csv("uk_mosques_modified.csv", index=False)

                            st.success(f"**{name}** has been successfully removed.")
                            # Reset removal target so form hides
                            st.session_state.remove_mosque_name = None
                        else:
                            st.warning("Please type exactly as prompted.")