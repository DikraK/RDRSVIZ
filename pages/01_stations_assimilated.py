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

# caldas statoma
exppath                  = config["EXPPATH"]['statoma_caldas_dir']

# time information
years                    = config["PERIOD"]["timeperiod"].split(',') 
yearfirst                = int(years[0])
yearend                  = int(years[1])

nameexps                 = config["NAMEEXP"]["exp_name"].split(',')  #DRS1992A,DRS2014A

namevars                 = config["VARIABLES"]["namevar"].split(',')  #TT,TD,SD

namersas                 = config["NAMERSAS"]["namersas"]

dirdata                  = "../data"

#============================= FUNCTIONS
#%% LOAD DATA
# function to load the data and cache it
@st.cache_data
def load_data(namevar, nameexp, year):
    namefile      = f"data/count_nbstation_assim_{namevar}_{nameexp}_{namersas}_{year}.parquet"
    data          = pd.read_parquet(namefile)
    
    month_columns = data[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    month_sum     = month_columns.sum(axis=0)
    return(data, month_sum)        

#============================ END READ CONFIGURATION

st.write("""
## Number of assimilated stations in CaLDAS over the reanalysis period
""")


year_to_look = st.slider('Select a year', min_value=yearfirst, max_value=yearend)

if 2014 <= year_to_look <= 2016 or 1992 <= year_to_look <= 1994 :
    
    if 2014 <= year_to_look <= 2016:
        nameexp    = nameexps[1]
    elif 1992 <= year_to_look <= 1994:
        nameexp    = nameexps[0]
        
    # extract the name of the directory
    option        = st.selectbox("Variables",("TT", "TD", "SD"))

    # extract the datasets 
    data_var, monthval    = load_data(option, nameexp, year_to_look)

    data_var['LON'] = data_var['LON'] -360

    # do the map
    colormap = cm.LinearColormap(colors=['magenta', 'green', 'red'], vmin=0, vmax=365)

    m        = folium.Map(location=[45.5, -93.56], zoom_start=2.4)    
    data_var.apply(lambda row:folium.Circle(location=[row["LAT"], row["LON"]], 
                                            color=colormap(row['Total']), fill=True,  fill_opacity=0.2,
                                            radius=30).add_to(m), axis=1)

    m.add_child(colormap)
    folium.map.LayerControl('topleft', collapsed= False).add_to(m)
    
    folium_static(m)
    
    st.subheader('Annual cycles of the number of assimilated stations')
    
    # Create the x-axis values (months) and the corresponding y-axis values (sums)
    x_values = range(1, 13)  # Month numbers from 1 to 12
    y_values = monthval.tolist()  # Convert the Series to a list

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker='o', linestyle='-', color='m')
    
    ax.set_title(f"Annual Time Series - {year_to_look} - {option}")
    ax.set_xlabel('Month')
    ax.set_xticks(x_values, month_names)  # Label the x-axis with month names
    ax.set_ylabel('Sum')
    
    ax.grid(True)

    # Use ScalarFormatter to format the x-axis tick labels
    ax.xaxis.set_major_formatter(ScalarFormatter())
    
    st.pyplot(fig)
    


else:
    
    st.warning('Currently this RDRS year is not run - only 1992-1994 and 2014-2016 are available', icon="⚠️")

