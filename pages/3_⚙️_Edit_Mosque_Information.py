# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode
import random

st.title("Hey Ed! Edit mosques here")
st.set_page_config(page_title="View/Search/Filter Mosques")

# Initialize session state DataFrame once
if 'df3' not in st.session_state:
    try:
        st.session_state.df3 = pd.read_csv("uk_mosques_modified.csv")
    except FileNotFoundError:
        st.session_state.df3 = pd.DataFrame()  # fallback to empty if file missing

df3 = st.session_state.df3.copy()

# Initialize editing state
if 'editing_mosque' not in st.session_state:
    st.session_state.editing_mosque = None

# Search bar
search_bar = st.text_input(label="**Search for a specific Masjid to edit**", placeholder="e.g. East London Mosque")

if search_bar:
    filtered_df = df3[df3["Mosque Name"].str.contains(search_bar, case=False, na=False)]
    if not filtered_df.empty:
        df3 = filtered_df
    else:
        st.write("No Mosque found matching your search...")
        df3 = pd.DataFrame()

# # Pagination setup
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

# # Initialize the removal target mosque name in session_state if not present
# if 'edit_mosque_name' not in st.session_state:
#     st.session_state.edit_mosque_name = None
# def is_user_active():
#     if 'user_active' in st.session_state.keys() and st.session_state['user_active']:
#         return True
#     else:
#         return False

# # Display mosques in grid with remove button and confirmation form inside container
# for i, (_, mosque) in enumerate(current_data.iterrows()):
#     col = columns[i % columns_per_page]  # Cycle through columns

#     # Extract fields to display
#     name = mosque.get('Mosque Name')
#     city = mosque.get('City')
#     postcode = mosque.get('Postcode')
#     telephone = mosque.get('Telephone Number')
#     capacity = mosque.get('Capacity')
#     denomination = mosque.get('Denomination')
#     womens_facilities = mosque.get('Facilities for Women')

#     with col:
#         with st.container(border=True, height= 500):
#             st.markdown(f"### {name}")
#             st.write(f"**City:** {city}")
#             st.write(f"**Postcode:** {postcode}")
#             st.write(f"**Telephone:** {telephone}")
#             st.write(f"**Capacity:** {capacity}")
#             st.write(f"**Denomination:** {denomination}")
#             st.write(f"**Facilities for Women:** {womens_facilities}")
#             edit_button = st.button(label = "Edit Information", type = "primary", key = f"{i}")
#         if edit_button and is_user_active():
#             with st.form(f'form_{i}'):
#                 new_name = st.text_input('edit the value', name)
#                 new_city = st.text_input('edit the value', city)
#                 new_postcode = st.text_input('edit the value', postcode)
#                 new_telephone = st.text_input('edit the value', telephone)
#                 new_capacity = st.text_input('edit the value', capacity)
#                 new_denomination = st.text_input('edit the value', denomination)
#                 new_womens = st.text_input('edit the value', womens_facilities)
#                 if st.form_submit_button('submit'):
#                     name = new_name
#                     city = new_city
#                     postcode = new_postcode
#                     telephone = new_telephone
#                     capacity = new_capacity
#                     denomination = new_denomination
#                     womens_facilities = new_womens
#                 #You can as well save your user input to a database and access later(sqliteDB will be nice)
#                     st.success('updated successfully')
#                 if st.form_submit_button('cancel'):
#                     st.warning('cancelled')
                
#                 st.info("Kindly reload your browser to start again!")
        # else:
        #     if st.button('press here to edit', key={i}):
        #         st.session_state['user_active']=True

    


# x = 5
# y = 3
# def is_user_active():
#     if 'user_active' in st.session_state.keys() and st.session_state['user_active']:
#         return True
#     else:
#         return False
# # if st.button('press here to edit'):
# if is_user_active():
#     with st.form('form'):
#         new_x = st.text_input('edit the value', x)
#         new_y = st.text_input('edit the value', y)
#         if st.form_submit_button('submit'):
#             x = new_x
#             y = new_y
#         #You can as well save your user input to a database and access later(sqliteDB will be nice)
#             st.success('updated successfully')
#         st.text(f'{x},{y}')
#         if st.form_submit_button('cancel'):
#             st.warning('cancelled')
        
#         st.info("Kindly reload your browser to start again!")
# else:
#     if st.button('press here to edit'):
#         st.session_state['user_active']=True


# Pagination (simplified for demo)
for idx, (_, mosque_row) in enumerate(current_data.iterrows()):
    col = columns[idx % columns_per_page]  # Cycle through columns


    with col:
        with st.container(border = True, height = 500):
            st.markdown(f"### {mosque_row['Mosque Name']}")
            st.write(f"**City:** {mosque_row['City']}")
            st.write(f"**Postcode:** {mosque_row['Postcode']}")
            st.write(f"**Telephone:** {mosque_row['Telephone Number']}")
            st.write(f"**Capacity:** {mosque_row['Capacity']}")
            st.write(f"**Denomination:** {mosque_row['Denomination']}")
            st.write(f"**Facilities for Women:** {mosque_row['Facilities for Women']}")

            edit_key = f"edit_{idx}"
            if st.button("Edit Information", type='primary', key=edit_key):
                st.session_state.editing_mosque = idx

            if st.session_state.editing_mosque == idx:
                with st.form(f"form_{idx}"):
                    new_name = st.text_input("Mosque Name", mosque_row['Mosque Name'])
                    new_city = st.text_input("City", mosque_row['City'])
                    new_postcode = st.text_input("Postcode", mosque_row['Postcode'])
                    new_telephone = st.text_input("Telephone Number", mosque_row['Telephone Number'])
                    new_capacity = st.text_input("Capacity", mosque_row['Capacity'])
                    new_denomination = st.text_input("Denomination", mosque_row['Denomination'])
                    new_womens = st.text_input("Facilities for Women", mosque_row['Facilities for Women'])

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
                        st.session_state.editing_mosque = None
                    elif cancel:
                        st.info("Edit cancelled")
                        st.session_state.editing_mosque = None

# Optionally add a save to CSV button
if st.button("Save changes to CSV"):
    st.session_state.df3.to_csv("uk_mosques_modified.csv", index=False)