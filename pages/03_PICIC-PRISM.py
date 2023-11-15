# !/usr/bin/python3

import streamlit as st 
import pandas as pd
import numpy as np

from configparser import ConfigParser

from PIL import Image


    
#============================ END READ CONFIGURATION

st.write("""
## Map of the differences per month between PRISM data generated by PICIC and Analysis (RSAS) 
""")

year_select = st.radio('Select one year:', ["1992"])

nameexp = st.radio(
    "Select one experiment",
    ["IC401wCHDSD", "IC401"],
    index=None,
)

namevar = st.radio(
    "Select one experiment",
    ["Tmin", "Tmax"],
    index=None,
)

image_name = f"figures/fig_diff_picic_rsas_{nameexp}_{year_select}_{namevar}.png"
image = Image.open(image_name)

st.image(image)
