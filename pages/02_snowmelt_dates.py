# !/usr/bin/python3

import streamlit as st 
import pandas as pd
import numpy as np
import os
from configparser import ConfigParser
import datetime
from math import pi, cos, sin
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from cartopy.feature import NaturalEarthFeature
import matplotlib.pyplot as plt


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
def load_data(domain):

    latinf, latsup, loninf, lonsup = domain
    
    namefile           = f"data/melting_date_stat_domain_lat{latinf}to{latsup}_lon{loninf}to{lonsup}.parquet"
    data               = pd.read_parquet(namefile)
    
    return(data)        

#============================ END READ CONFIGURATION

st.write("""
## Plot the date of melting snow per domain
""")

namedomain       = st.sidebar.radio('Select one:', ['Montreal-Quebec', 'West', 'East', 'Gaspesie'])

if namedomain == 'Montreal-Quebec':
    domain = [45, 48, 285, 290]
elif namedomain == 'East':   
    domain = [44,  47, 283, 288]
elif namedomain == 'West':
    domain = [50, 55, 235, 240]
elif namedomain == 'Gaspesie':
    domain = [48, 50, 291, 296]
    

latinf, latsup, loninf, lonsup = domain
data_melt = load_data(domain)


#%%
# DO THE PLOT
    
# COORDINATES MONTH
month_lbl        = ['Jan', 'Fev', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ordinal_days_lbl = [] 
for m in range(1,13):
    if m <10:
        date_str = f"2023-0{m}-01"
    else:
        date_str= f"2023-{m}-01"
    # Convert the date string to a datetime object
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        
    # Get the ordinal day
    ordinal_day = date.timetuple().tm_yday
    ordinal_days_lbl.append(ordinal_day)
    
angles_lbl  = [ (2* pi *x/365) for x in ordinal_days_lbl] 

ordinal_days     = []
for date_in in data_melt['MEDIAN']:
    if pd.isna(date_in):
        ordinal_day = float('nan')
    else: 
        # Get the ordinal day
        ordinal_day = date_in.timetuple().tm_yday
    
    ordinal_days.append(ordinal_day)
    
angles      = [ (2* pi *x/365) for x in ordinal_days]

# estimate the radiius
radii = np.linspace( 1,0.1,  len(range(1980, 2018+1)))
    
# do the plot
fig = plt.figure(figsize=(12, 6))


ax1 = fig.add_subplot(121, projection='polar')

# ax1 = axes[0]
# ax1 = plt.subplot(121, projection='polar')

ax1.plot(angles, radii, marker='o', linestyle='--', markersize=5, color='red')

yearsval    = np.arange(1980, 2018 + 1)
yticksval   = radii[::5]
yticklabels = [str(x) for x in yearsval[::5]]

ax1.set_yticks(yticksval)
ax1.set_yticklabels(yticklabels)
ax1.set_xticks(angles_lbl)      # Set the angular ticks to match the dates
ax1.set_xticklabels(month_lbl)  # Use date labels for the angular ticks

# Subplot 2: Map
if loninf > 180:
    loninf -= 360
if lonsup > 180:
    lonsup -= 360


ax2 = fig.add_subplot(122, projection=ccrs.PlateCarree())
# ax2 = axes[1]

# ax2 = plt.subplot(122, projection=ccrs.PlateCarree())
ax2.set_extent([loninf-5 , lonsup+5, latinf-5, latsup+5], crs=ccrs.PlateCarree())

# Add rivers using Cartopy's NaturalEarthFeature
rivers = NaturalEarthFeature(category='physical', name='rivers_lake_centerlines', 
                            scale='10m', facecolor='none', edgecolor='blue', linewidth=0.5)
ax2.add_feature(rivers)


ax2.add_patch(plt.Rectangle((loninf, latinf), lonsup - loninf, latsup - latinf, 
                            color='blue', alpha=0.2, transform=ccrs.PlateCarree()))
ax2.coastlines(resolution='10m')
ax2.set_title('Spatial Domain')


st.pyplot(fig)

