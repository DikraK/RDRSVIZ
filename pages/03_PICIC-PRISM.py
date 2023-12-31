# !/usr/bin/python3

import streamlit as st 
import pandas as pd
import numpy as np

from configparser import ConfigParser

from PIL import Image


    
#============================ END READ CONFIGURATION

st.write("""
## Map of the differences per month between PRISM data generated by PICIC and Analysis (RSAS) or RDRS
""")

year_select = st.radio('Select one year:', ["1992"])

nameexp = st.radio(
    "Select one experiment",
    ["IC401wCHDSD", "IC401"],
    index=None,
)

namevar = st.radio(
    "Select one experiment",
    ["PR", "Tmin", "Tmax"],
    index=None,
)

if namevar and nameexp and year_select:
    
    if namevar == "PR" and nameexp == "IC401":
        st.warning(f"Currently this map for precipitation is not available for IC401 - try an other experiment", icon="⚠️")
    else:
        if namevar == "PR" and nameexp == "IC401wCHDSD":
            typediff = st.radio("Select one type of difference", ["DIFFERENCE (mm)", "RELATIVE DIFFERENCE (%)"], index=None)
            
            if typediff == "DIFFERENCE (mm)":
                image_name = f"figures/fig_diff_picic_rdrs_{nameexp}_{year_select}_{namevar}.png"
            else:
                image_name = f"figures/fig_diff_rel_picic_rdrs_{nameexp}_{year_select}_{namevar}.png"                    
            st.info('06-18 leadtimes of Precipitation are taken from RDRS')
        else:
            st.info('Analysis fields are taken from RSAS')
            image_name = f"figures/fig_diff_picic_rsas_{nameexp}_{year_select}_{namevar}.png"
            
        image = Image.open(image_name)

        st.image(image)
