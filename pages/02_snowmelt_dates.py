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
def load_data(domain):

    latinf, latsup, loninf, lonsup = domain
    
    namefile           = f"data/melting_date_stat_domain_lat{latinf}to{latsup}_lon{loninf}to{lonsup}.parquet"
    data               = pd.read_parquet(namefile)
    
    return(data)        

#============================ END READ CONFIGURATION

st.write("""
## Plot the date of melting snow per domain
""")

namedomain       = st.sidebar.radio('Select one:', ['Mtl-Qc', 'West'])

if namedomain == 'Mtl-Qc':
    domain = [45, 48, 285, 290]
elif namedomain == 'West':
    domain = [50, 55, 235, 240]

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

ordinal_days     = []
for date_in in data_melt    ['MEDIAN']:
    if pd.isna(date_in):
        ordinal_day = float('nan')
    else: 
        # Get the ordinal day
        ordinal_day = date_in.timetuple().tm_yday
    
ordinal_days.append(ordinal_day)
    
angles      = [ (2* pi *x/365) for x in ordinal_days]

angles_lbl  = [ (2* pi *x/365) for x in ordinal_days_lbl] 

# estimate the radiius
radii = np.linspace( 1,0.1,  len(range(years[0], years[1] + 1)))
    
# do the plot
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
ax1 = axes[0]
ax1 = plt.subplot(121, projection='polar')


ax1.plot(angles, radii, marker='o', linestyle='--', markersize=5, color='red')

yearsval    = np.arange(years[0], years[1] + 1)
yticksval   = radii[::5]
yticklabels = [str(x) for x in yearsval[::5]]

ax1.set_yticks(yticksval)
ax1.set_yticklabels(yticklabels)
ax1.set_xticks(angles_lbl)  # Set the angular ticks to match the dates
ax1.set_xticklabels(month_lbl)  # Use date labels for the angular ticks


# Subplot 2: Map
    if loninf > 180:
        loninf -= 360
    if lonsup > 180:
        lonsup -= 360
        
    ax2 = axes[1]
    ax2 = plt.subplot(122, projection=ccrs.PlateCarree())
    ax2.set_extent([loninf, lonsup, latinf, latsup], crs=ccrs.PlateCarree())
    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world.boundary.plot(ax=ax2, linewidth=0.5, color='black')
    
    
    # Add rivers using Cartopy's NaturalEarthFeature
    rivers = NaturalEarthFeature(category='physical', name='rivers_lake_centerlines', 
                                scale='10m', facecolor='none', edgecolor='blue', linewidth=0.5)

    ax2.add_feature(rivers)
    
    sd_val = subset_data['SD'][0, 0,:,:].values
    sd_val[~np.isnan(sd_val)] = 1
    
    lats = subset_data['lat'][:].values
    lons = subset_data['lon'][:].values - 360

    sdp = ax2.contourf(lons, lats, sd_val, 1, colors='gray' ,
                transform=ccrs.PlateCarree())

    ax2.coastlines(resolution='10m')
    ax2.set_title('Spatial Domain')
    
    cities = gpd.read_file('data/ne_10m_populated_places.shp')

    # Filter the cities (you can customize this filter based on your requirements)
    cities_domain = cities.cx[loninf: lonsup, latinf: latsup]
    
    major_cities  = cities_domain[cities_domain['POP_MAX'] > 100000]
    
    compt = 10000  
    max_attempts = 10  # Maximum number of iterations to avoid infinite loop

    while len(major_cities) < 5 and max_attempts > 0: 
        taille_max   = 100000 - compt;
        major_cities = cities_domain[cities_domain['POP_MAX'] > taille_max]   
        compt += 10000
        max_attempts -= 1
        
    # Plot the city locations and labels
    for idx, city in major_cities.iterrows():
        ax2.text(city['geometry'].x, city['geometry'].y, city['NAME'], fontsize=8, 
                ha='center', va='center', transform=ccrs.PlateCarree())

st.pyplot(fig)


else:
    
    st.warning('Currently no other domain are computed', icon="⚠️")

