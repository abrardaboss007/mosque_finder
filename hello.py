# Import relevant modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
#----------------------------------------------------------------------------------------------
# Formatting of CSV File (lines 10-65)
#----------------------------------------------------------------------------------------------
# Store CSV file in a dataframe
df = pd.read_csv("uk_mosques.csv", encoding="latin1", on_bad_lines="skip")

df['Information'] = df['Information'].str.replace(r"[Unsure]", '', regex=False)

# Separate the amalgamated information inside the "Information" column using delimeters
information_split_df = df["Information"].str.split(r"[].]", expand=True)
information_split_df = information_split_df.iloc[:,0:4]
information_split_df_columns = ["Miscellaneous Info","Mosque Name","Address","Telephone Number"]
df[information_split_df_columns] = information_split_df

# Separate the amalgamated information inside the "City" column using delimeters
city_split_df = df["City"].str.rsplit("-", n=1, expand=True)
city_split_df_columns = ["City and Postcode","ID Number"]
df[city_split_df_columns] = city_split_df

second_city_split_df = df["City and Postcode"].str.rsplit(",", n=1, expand=True)
second_city_split_df_columns = ["City","Postcode"]
df[second_city_split_df_columns] = second_city_split_df

# Create a new column that mentions the denomination of the mosque
df["Denomination"] = np.where(
    df["Miscellaneous Info"].str.contains("Shia",regex=False, na=False), "Shia",
    np.where(df["Miscellaneous Info"].str.contains("Deob", regex=False, na=False),"Sunni",
    np.where(df["Miscellaneous Info"].str.contains("Arab", regex=False, na=False),"Sunni",
    np.where(df["Miscellaneous Info"].str.contains("Brel", regex=False, na=False),"Sunni",
    np.where(df["Miscellaneous Info"].str.contains("Maud", regex=False, na=False),"Sunni",
    np.where(df["Miscellaneous Info"].str.contains("Salf", regex=False, na=False),"Sunni",
    np.where(df["Miscellaneous Info"].str.contains("Sufi", regex=False, na=False),"Sunni",
    "Not Specified"))))))
)

# Create a new column that mentions whether there are facilities for women to pray or not
df["Facilities for Women"] = np.where(
    df["Miscellaneous Info"].str.contains("NoW", regex=False, na=False), "No",
    np.where(df["Miscellaneous Info"].str.contains("W", regex=False, na=False),"Yes",
    "Not Sure")
)

# Create a new column that mentions the capacity of the mosque as string data type for display purposes
df['Capacity'] = df['Miscellaneous Info'].str.extract(r'(\d+)')
df = df.replace(r'^\s*$', np.nan, regex=True)
df = df.fillna(0)
df = df.replace(0, "N/A")

# Recreate the capacity column which can be used for calculations behind the scenes with integer data type
df['Capacity_For_Calc'] = pd.to_numeric(df['Capacity'], downcast="integer", errors='coerce')
df["Longitude"] = pd.to_numeric(df["Longitude"], downcast='float', errors = "coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], downcast='float', errors = "coerce")
df = df.fillna(0)
# Remove unnecessary columns
columns_to_keep = ["Longitude","Latitude","Mosque Name", "Denomination", "Capacity", "Facilities for Women", "Address", "City", "Postcode", "Telephone Number", "Capacity_For_Calc"]
df = df[columns_to_keep]


#----------------------------------------------------------------------------------------------
# Save the CSV file to a new file
df.to_csv('uk_mosques_modified.csv', index=False)
df_modified = pd.read_csv("uk_mosques_modified.csv")
st.write(df)