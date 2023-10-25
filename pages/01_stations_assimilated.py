# !/usr/bin/python3

import streamlit as st 
import pandas as pd
import numpy as np
import os
from configparser import ConfigParser
import branca.colormap as cm

import folium
from folium.plugins import Draw
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

#============================ READ CONFIGURATION
#
config = ConfigParser()
config.read("Configuration.ini")

# name of the variables
namevars                 = config["VARIABLES"]["namevar"].split(',')  #TT,TD,SD

# time information
years                    = config["PERIOD"]["timeperiod"].split(',') 
yearfirst                = int(years[0])
yearend                  = int(years[1])

# directory where the data are saved
dirdata                  = "../data"

# name of experiments
nameexps = []
for section in config.sections():
    if 'DRS' in section :
        nameexps.append(section)


#============================= FUNCTIONS
#%% LOAD DATA
# function to load the data and cache it
@st.cache_data
def load_data(namevar, nameexp, year, namersas):
    namefile      = f"data/count_nbstation_assim_{namevar}_{nameexp}_{namersas}_{year}.parquet"
    data          = pd.read_parquet(namefile)
    
    month_columns = data[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    month_sum     = month_columns.sum(axis=0)
    return(data, month_sum)        

#============================ END READ CONFIGURATION
st.set_page_config(layout = 'wide')

st.write("""
## Number of assimilated stations in CaLDAS derived from statoma files over the reanalysis period
""")


option_exp = st.selectbox("Select an experiment:", ("DRS1992A", "DRS2014A", "DRS1992IC401", "DRS1992IC401wCWA" ))

namersas   = config[option_exp]['RSAS']
exppath    = config[option_exp]['EXPPATH']
years_s    = config[option_exp]['YEAR'].split(',')
years      = [int(x) for x in years_s]    
    
year_to_look = st.slider('Select a year', min_value=yearfirst, max_value=yearend)

if year_to_look in years:        
    # extract the name of the directory
    option        = st.selectbox("Variables",("TT", "TD", "SD"))

    # extract the datasets 
    data_var, monthval    = load_data(option, option_exp, year_to_look, namersas)

    data_var['LON'] = data_var['LON'] -360

    # do the map
    colormap = cm.LinearColormap(colors=['magenta', 'green', 'red'], vmin=0, vmax=365)

    m        = folium.Map(location=[45.5, -93.56], zoom_start=2.4)    
    data_var.apply(lambda row:folium.Circle(location=[row["LAT"], row["LON"]], 
                                            color=colormap(row['Total']), fill=True,  fill_opacity=0.2,
                                            radius=30).add_to(m), axis=1)

    m.add_child(colormap)
    folium.map.LayerControl('topleft', collapsed= False).add_to(m)
    

    folium_static(m, width=600, height=320)


    st.subheader('Annual cycles of the number of assimilated stations')
    
    # Create the x-axis values (months) and the corresponding y-axis values (sums)
    x_values = range(1, 13)  # Month numbers from 1 to 12
    y_values = monthval.tolist()  # Convert the Series to a list

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(x_values, y_values, marker='o', linestyle='-', color='m')
    
    ax.set_title(f"Annual Time Series - {year_to_look} - {option}")
    ax.set_xlabel('Month')
    ax.set_xticks(x_values, month_names)  # Label the x-axis with month names
    ax.set_ylabel('# assimilated cases')
    
    ax.grid(True)

    # Use ScalarFormatter to format the x-axis tick labels
    ax.xaxis.set_major_formatter(ScalarFormatter())
    
    st.pyplot(fig, use_container_width=True)
    

else:
    
    st.warning(f"Currently this experiments RDRS year is not run - only {years_s} is/are available", icon="⚠️")

