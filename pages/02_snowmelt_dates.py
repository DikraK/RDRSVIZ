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

@st.cache_data
def load_prcp_data(domain, nameexp):
    latinf, latsup, loninf, lonsup = domain
    
    if nameexp == "v21":    
        nameexpfile = "V2P1"
    else:
        nameexpfile = nameexp
        
    namefile           = f"data/yearly_prcp_domain_lat{latinf}to{latsup}_lon{loninf}to{lonsup}_{nameexpfile}.parquet"
    data               = pd.read_parquet(namefile)
    
    return(data)        

def doplottimeseries(axin, data_prcp_agg, unit, marker_t, colorm, colore, labeltxt):
    
    if labeltxt == "V2.1":
        alphaval = 0.4
    else:
        alphaval = 0.7
        
    axin.plot(data_prcp_agg['year'], unit*data_prcp_agg['yearlysum'], 
        marker=marker_t, linestyle='--', markersize=7, 
        color=colorm, markeredgecolor=colore, label=labeltxt)

    axin.fill_between(data_prcp_agg['year'], 
                    unit*data_prcp_agg['yearlysum_25pct'], 
                    unit*data_prcp_agg['yearlysum_75pct'], 
                    color=colorm, alpha=alphaval)   
    
    return(axin)
        
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
## Melting snow date per domain 
""")

st.write(""" The melting snow melt date displayed in the figure is the median snow melt date (one per year) over the domain (shaded blue) on the left""")

st.info("""The snow is considered melted once at least 30 days of snow depth stays below a threshold (close to zero)""")


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

data_melt_v21       = load_data(domain, "v21")
data_melt_v3wCWA    = load_data(domain, "DRS1992IC401wCHDSD")
data_melt_v3        = load_data(domain, "DRS1992IC401")
data_melt_v3_bis    = load_data(domain, "DRS1992IC401v3")

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

dfout_v3wCWA = estimateangle(data_melt_v3wCWA)
dfout_v3wCWA.loc[dfout_v3wCWA['YEAR'] == 1991, 'ANGLE'] = np.nan

dfout_v3_bis = estimateangle(data_melt_v3_bis)
dfout_v3_bis.loc[dfout_v3_bis['YEAR'] == 1993, 'ANGLE'] = np.nan

#%%    
# do the plot
fig = plt.figure(figsize=(12, 6))

ax1 = fig.add_subplot(121, projection='polar')

ax1.plot(dfout_v2['ANGLE'], dfout_v2['RADII'], marker='o', linestyle='--', markersize=5, 
        color='sandybrown', label="V2.1")
ax1.plot(dfout_v3['ANGLE'], dfout_v3['RADII'], marker='*', linestyle='--', markersize=8, 
        color='blue', label="DRS1992IC401")
ax1.plot(dfout_v3wCWA['ANGLE'], dfout_v3wCWA['RADII'], marker='D', linestyle='--', markersize=7, 
        color='purple', label="DRS1992IC401wCHDSD")
ax1.plot(dfout_v3_bis['ANGLE'], dfout_v3_bis['RADII'], marker='>', linestyle='--', markersize=8, 
        color='hotpink', markeredgecolor='darkred', label="DRS1992IC401v3")

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

#%%    
# do the plot

data_prcp_agg_v21   = load_prcp_data(domain, "v21")

data_prcp_agg_v01_ = load_prcp_data(domain, "DRS1992IC401")
data_prcp_agg_v01  = data_prcp_agg_v01_[data_prcp_agg_v01_['year'] == 1992].reset_index(drop=True)

data_prcp_agg_v01v3_ = load_prcp_data(domain, "DRS1992IC401v3")
data_prcp_agg_v01v3  = data_prcp_agg_v01v3_[data_prcp_agg_v01v3_['year'] == 1992].reset_index(drop=True)


unit = 1000

fig = plt.figure(figsize=(4, 2))

ax = fig.add_subplot(111)

ax = doplottimeseries(ax, data_prcp_agg_v21, unit, 
                    'o', 'sandybrown', 'sandybrown', "V2.1")

ax = doplottimeseries(ax, data_prcp_agg_v01v3, unit, 
                    '>', 'hotpink', 'darkred', "DRS1992IC401v3")
                    
ax = doplottimeseries(ax, data_prcp_agg_v01, unit, 
                    '*', 'blue', 'blue', "DRS1992IC401")

ax.legend(loc="lower right")
ax.set_title('Precipitation accumulation over the domain')
ax.set_ylabel('[mm]')
ax.set_xlabel('year')
ax.grid()

st.pyplot(fig)

st.info("The shaded area corresponds to the 25th and 75th percentiles of the accumulation precipitation over the area")

