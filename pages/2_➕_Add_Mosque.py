# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode

# Add tab title to page
st.set_page_config(page_title="Add mosque")
#----------------------------------------------------------------------------------------------
# Formatting of CSV File (lines 11-65)
#----------------------------------------------------------------------------------------------
df2  = pd.read_csv("uk_mosques_modified.csv")
df2["Longitude"] = df2["Longitude"].astype(float)
df2["Latitude"] = pd.to_numeric(df2["Latitude"], errors="coerce")

st.title("Hey Ed! Add mosques here")

with st.form("Add mosque", clear_on_submit=True):
    nomi = pgeocode.Nominatim('gb')
    mosque_name =  st.text_input("Mosque name **(Required)**")
    mosque_address = st.text_input("Mosque Address **(Required)**")
    mosque_city = st.text_input("City **(Required)**")
    mosque_postcode = st.text_input("Postcode **(Required)**")
    mosque_number = st.text_input("Contact number of Mosque **(Required)**")
    mosque_long = st.text_input("Longitude (Optional)")
    mosque_lat = st.text_input("Latitude (Optional)")
    mosque_capacity = st.text_input("Mosque capacity **(Required)**")
    mosque_denomination = st.text_input("Mosque Denomination **(Required)**")
    mosque_women = st.text_input("Are there prayer facilities for women?*")
    submit_button = st.form_submit_button("Submit")
    # location = nomi.query_postal_code(mosque_postcode)
    # mosque_lat = location.latitude if not pd.isna(location.latitude) else ""
    # mosque_long = location.longitude if not pd.isna(location.longitude) else ""

    # if not mosque_lat:
    #     nomi = pgeocode.Nominatim('gb')
    #     location = nomi.query_postal_code(mosque_postcode)
    #     mosque_lat = location.latitude if not pd.isna(location.latitude) else ""

    # if not mosque_long:
    #     nomi = pgeocode.Nominatim("gb")
    #     location = nomi.query_postal_code(mosque_postcode)
    #     mosque_long = location.longitude if not pd.isna(location.longitude) else ""
#new_data  = [mosque_long, mosque_lat, mosque_name, mosque_denomination, mosque_capacity, mosque_women, mosque_address, mosque_city, mosque_postcode, mosque_number, int(mosque_capacity)] 
 
    if submit_button:
        location = nomi.query_postal_code(mosque_postcode)
        mosque_lat = float(location.latitude) 
        mosque_long = float(location.longitude)
        new_data  = [mosque_long, mosque_lat, mosque_name, mosque_denomination, mosque_capacity, mosque_women, mosque_address, mosque_city, mosque_postcode, mosque_number, mosque_capacity]
        if not mosque_name or not mosque_city or not mosque_postcode or not mosque_number or not mosque_capacity or not mosque_women or not mosque_denomination or not mosque_address:
            st.warning("One or more required fields are missing. Please try again")
        else:
            new_row_df = pd.DataFrame([new_data], columns=df2.columns)
            df2 = pd.concat([df2, new_row_df], ignore_index=True)
            df2["Latitude"] = df2["Latitude"].astype(float)
            df2["Longitude"] = df2["Longitude"].astype(float)
            df2["Capacity_For_Calc"] = df2["Capacity_For_Calc"].astype(float)
            df2.to_csv("uk_mosques_modified.csv", index=False)
            st.success("Mosque has now been added!")
