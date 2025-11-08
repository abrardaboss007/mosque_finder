# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import pgeocode
import re
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

#----------------------------------------------------------------------------------------------
# Add tab title + Formatting of CSV File (lines 16-87)
#----------------------------------------------------------------------------------------------
# Add tab title to page
st.set_page_config(page_title="Add Mosque")

# Bring in CSV file and format it
df2  = pd.read_csv("uk_mosques_modified.csv")
df2["Longitude"] = df2["Longitude"].astype(float)
df2["Latitude"] = pd.to_numeric(df2["Latitude"], errors="coerce")

def is_valid_uk_postcode(postcode):
    # This regex covers most UK postcode formats 
    postcode = postcode.strip().upper()
    pattern = r"^(GIR 0AA|[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})$"
    return re.match(pattern, postcode) is not None

def is_valid_uk_phone_number(phone):
    try:
        parsed = phonenumbers.parse(phone, "GB")  # "GB" is the UK country code
        formatted_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return phonenumbers.is_valid_number(formatted_number)
    except NumberParseException:
        return False

# Create form asking user to add relevant information to be able to add Mosque
with st.form("Add mosque", clear_on_submit=True):
    nomi = pgeocode.Nominatim('gb')
    mosque_name =  st.text_input("Mosque name **(Required)**")
    mosque_address = st.text_input("Mosque Address **(Required)**")
    mosque_city = st.text_input("City **(Required)**")
    mosque_postcode = st.text_input("Postcode **(Required)**")
    mosque_number = st.text_input("Contact number of Mosque **(Required)**")
    mosque_long = st.number_input(label = "Longitude (Optional)", min_value = -10.6404, max_value = 1.7676, step = 0.0001, format="%0.4f", value=None)
    mosque_lat = st.number_input(label = "Latitude (Optional)", min_value= 49.9424, max_value= 60.8971, step=0.0001, format="%0.4f", value=None)
    mosque_capacity = st.number_input(label= "Mosque capacity **(Required)**", min_value=10, max_value=100000, step = 1, value=None)
    mosque_denomination = st.selectbox(label= "Mosque Denomination **(Required)**", options = ["Sunni","Shia", "Not Specified"], placeholder="Choose an option...", index = None)
    mosque_women = st.selectbox(label= "Are there prayer facilities for women? **(Required)**", options= ["Yes", "No", "Not Sure"], placeholder="Choose an option...", index = None)
    
    # Add submit button
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Add lat and long coordinates to Mosque information manually if user does not (since it is an optional field)
        try:
            location = nomi.query_postal_code(mosque_postcode)
            if not mosque_lat:
                mosque_lat = float(location.latitude) 
            if not mosque_long:
                mosque_long = float(location.longitude)
        except ValueError:
            pass
        
        # Create new row of data containing the user input
        new_data  = [mosque_long, mosque_lat, mosque_name, mosque_denomination, mosque_capacity, mosque_women, mosque_address, mosque_city, mosque_postcode, mosque_number, mosque_capacity]

        if mosque_postcode and not is_valid_uk_postcode(mosque_postcode):
            st.error("Please enter a valid UK postcode in the correct format, e.g. WC2N 6RH")
            st.stop()
        elif mosque_number and not is_valid_uk_phone_number(mosque_number):
            st.error("Please enter a valid UK phone number, e.g. +447911123456 or 07911123456")
            st.stop()
        elif not mosque_name or not mosque_city or not mosque_postcode or not mosque_number or not mosque_capacity or not mosque_women or not mosque_denomination or not mosque_address:
            st.error("One or more required fields are missing. Please try again!")
            st.stop()
        else:
            # Append Mosque data if user clicks submit having inputted all required information
            new_row_df = pd.DataFrame([new_data], columns=df2.columns)
            df2 = pd.concat([df2, new_row_df], ignore_index=True)
            df2["Latitude"] = df2["Latitude"].astype(float)
            df2["Longitude"] = df2["Longitude"].astype(float)
            df2["Capacity_For_Calc"] = df2["Capacity_For_Calc"].astype(float)
            df2.to_csv("uk_mosques_modified.csv", index=False)
            st.success("Mosque has now been added!")
            st.info("Please refresh this page if you want to be able to view the Mosque on the other pages!")