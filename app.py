# apps.run()

import streamlit as st
#from pages import stations_assimilated, annual_amount,scores_plot

st.title("Home")

st.header("Introduction")
st.markdown(
    """
This site help visualize outputs from the CaPA reanalysis and explore different aspects of it.
"""
)

st.markdown(
    """
    - **Hourly precipitation in netCDF format and over North America domain available on the:**[Canadian Surface Prediction Archive (CaSPAr) platform](https://caspar-data.ca/)
    - **Scientific article about the reanalysis in HESS:** https://hess.copernicus.org/articles/25/4917/2021/
    """
)

