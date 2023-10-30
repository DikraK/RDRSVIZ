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

# time information
years                    = config["PERIOD"]["timeperiod"].split(',') 
yearfirst                = int(years[0])
yearend                  = int(years[1])

dirdata                  = "../data"

#============================= FUNCTIONS
#%% LOAD DATA
# function to load the data and cache it
@st.cache_data
def load_data(domain, nameexp):

    latinf, latsup, loninf, lonsup = domain
    
    if nameexp == "v21":    
        namefile           = f"data/melting_date_stat_domain_lat{latinf}to{latsup}_lon{loninf}to{lonsup}.parquet"
    else:
        namefile           = f"data/melting_date_stat_domain_lat{latinf}to{latsup}_lon{loninf}to{lonsup}_{nameexp}.parquet"
    data               = pd.read_parquet(namefile)
    
    return(data)        


def estimateangle(data_melt_ds):
    
    # ordinal day
    ordinal_days     = []
    for date_in in data_melt_ds['MEDIAN']:
        if pd.isna(date_in):
            ordinal_day = float('nan')
        else: 
            # Get the ordinal day
            ordinal_day = date_in.timetuple().tm_yday
        
        ordinal_days.append(ordinal_day)
        
    angles      = [ (2* pi *x/365) for x in ordinal_days]
    
    yy = data_melt_ds['YEAR'].tolist()
    # extract the year
    df          = pd.DataFrame({'YEAR': yy, 'ANGLE': angles})
    
    # Generate a list of years from 1980 to 2018
    all_years    = list(range(1980, 2019))

    # Merge the existing DataFrame with the full list of years and fill NaN
    result_df = pd.DataFrame({'YEAR': all_years})
    result_df = result_df.merge(df, on='YEAR', how='left')
    result_df['ANGLE'] = result_df['ANGLE'].fillna(np.nan)

    # If needed, you can sort the DataFrame by the 'YEAR' column
    result_df = result_df.sort_values(by='YEAR')
    
    # estimate the radiius
    radii       = np.linspace( 1,0.1,  len(range(1980, 2018+1)))
    result_df['RADII'] = radii
    
    return(result_df)

    
#============================ END READ CONFIGURATION

st.write("""
## Plot the melting snow date per domain 
""")

st.write(""" #### The melting snow melt date displayed in the figure is the median (on per year) over the domain (shaded blue) on the left""")

st.write(""" #### The snow is considered melted once at least 30 days of snow depth stays below a threshold (close to zero)""")


namedomain       = st.radio('Select one domain:', ['Montreal-Quebec', 'West', 'East', 'Gaspesie'])

if namedomain == 'Montreal-Quebec':
    domain = [45, 48, 285, 290]
elif namedomain == 'East':   
    domain = [44,  47, 283, 288]
elif namedomain == 'West':
    domain = [50, 55, 235, 240]
elif namedomain == 'Gaspesie':
    domain = [48, 50, 291, 296]
    

latinf, latsup, loninf, lonsup = domain

data_melt_v21 = load_data(domain, "v21")
data_melt_v3  = load_data(domain, "DRS1992IC401wCWA")


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

dfout_v2 = estimateangle(data_melt_v21)
dfout_v3 = estimateangle(data_melt_v3)
dfout_v3.loc[dfout_v3['YEAR'] == 1991, 'ANGLE'] = np.nan

#%%    
# do the plot
fig = plt.figure(figsize=(12, 6))

ax1 = fig.add_subplot(121, projection='polar')

ax1.plot(dfout_v2['ANGLE'], dfout_v2['RADII'], marker='o', linestyle='--', markersize=5, color='red', label="V2.1")
ax1.plot(dfout_v3['ANGLE'], dfout_v3['RADII'], marker='*', linestyle='--', markersize=6, color='blue', label="DRS1992IC401wCWA")

radii       = dfout_v2['RADII'].tolist()

yearsval    = np.arange(yearfirst, yearend + 1)
yticksval   = radii[::5]
yticklabels = [str(x) for x in yearsval[::5]]

ax1.set_yticks(yticksval)
ax1.set_yticklabels(yticklabels)
ax1.set_xticks(angles_lbl)      # Set the angular ticks to match the dates
ax1.set_xticklabels(month_lbl)  # Use date labels for the angular ticks
ax1.legend(loc="lower right")

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

st.warning('The red markers illustrate the snow melt date for RDRSv2.1', icon="⚠️")