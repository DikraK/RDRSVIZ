# !/usr/bin/python3


import pandas as pd
import numpy as np
import os
from datetime import datetime
from configparser import ConfigParser
from tqdm import tqdm 
#============================ READ CONFIGURATION
#
config = ConfigParser()
config.read("../Configuration.ini")

# time information
years                    = config["PERIOD"]["timeperiod"].split(',') 
yearfirst                = int(years[0])
yearend                  = int(years[1])
# name of variable
namevars                 = config["VARIABLES"]["namevar"].split(',')  #TT,TD,SD


# name of experiments
nameexps = []
for section in config.sections():
    if 'DRS' in section :
        nameexps.append(section)

# where to save the outputs 
dirdata                  = "../data"

#============================= FUNCTIONS
#%% function to load the data 
def load_data(namevar, year, directory):
    # Create an empty DataFrame to store the concatenated data
    data = pd.DataFrame()
    
    # Define the suffix based on the namevar
    suffixe = f"_statoma_{namevar}_001" if "SD" in namevar else f"_statoma_{namevar}_000"
    
    # Create a list of relevant files
    relevant_files = [filename for filename in os.listdir(directory) if suffixe in filename and str(year) in filename]

    # Loop through the files in the directory
    for filename in tqdm(relevant_files, desc="Processing files"):
        # extract the date
        date_str  = filename[0:10]
        
        # # Load the statoma file
        file_path = os.path.join(directory, filename)
        df        = pd.read_csv(file_path, delim_whitespace=True, header='infer')  
        
        # select only interesting columns and add dates
        df_sub                  = df[['LAT', 'LON', 'ALT']] 
        
        df_sub                  = df_sub.assign(DATE=date_str)
        data                    = pd.concat([data, df_sub], axis=0, ignore_index=True)
        
    return(data)   

for nameexp in nameexps:
    
    print(nameexp)
    
    exppath  = config[nameexp]['EXPPATH']
    namersas = config[nameexp]['RSAS']
    years_s  = config[nameexp]['YEAR'].split(',')
    years    = [int(x) for x in years_s]
    
    dirname         = dict()
    dirname['TT']   = f"{exppath}/{nameexp}/{namersas}/gridpt/mist/statoma/screen/yin"  
    dirname['TD']   = dirname['TT']
    dirname['SD']   = f"{exppath}/{nameexp}/{namersas}/gridpt/mist/statoma/snow/yin"  
    
    for namevar in namevars:
        print(namevar)
        for year in years:
            # load the data
            data_var    = load_data(namevar, year, dirname[namevar])

            # format the date
            data_var['DATE'] = pd.to_datetime(data_var['DATE'], format="%Y%m%d%H")

            # Extract year and month
            data_var['MONTH'] = data_var['DATE'].dt.month

            # Group by 'LAT', 'LON', 'ALT', and 'MONTH', and count the size
            grouped = data_var.groupby(['LAT', 'LON', 'ALT', 'MONTH']).size().reset_index(name='COUNT')

            # Pivot the table to create one column for each month
            pivoted = grouped.pivot_table(index=['LAT', 'LON', 'ALT'], 
                                        columns='MONTH', values='COUNT', fill_value=0).reset_index()

            # List of month names and their corresponding month numbers
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            all_months = list(range(1, 13))  # All month numbers from 1 to 12

            # Identify missing months
            missing_months = set(all_months) - set(pivoted.columns[3:])

            # Insert columns for missing months with zeros
            for month in missing_months:
                pivoted[month_names[month - 1]] = 0

            # Rename columns with month names
            pivoted.columns  = ['LAT', 'LON', 'ALT'] + month_names

            pivoted['Total'] = pivoted.iloc[:, 3:].sum(axis=1)

            # Save the DataFrame to a Parquet file
            namefileout      = f"{dirdata}/count_nbstation_assim_{namevar}_{nameexp}_{namersas}_{year}.parquet"
            pivoted.to_parquet(namefileout, index=False) 
            
            if os.path.isfile(namefileout):
                print(f"File {namefileout} has been created successfully.")
            else:
                print(f"File {namefileout} was not created.")

# # #%% 

# # # LOAD THE DATA AND STORE THEM
# # for year in range(yearfirst, yearend+1):
    
# #     if 2014 <= year <= 2016 or 1992 <= year <= 1994 :
# #         for nameexp in nameexps:
# #         if "DRS2014A" in nameexp :
# #             if 2014 <= year <= 2016 or 1992 <= year <= 1994 :
# #                 namersas = namersass[0]
# #                 exppath  = exppaths[0]                                           
# #             else:
# #                 pass
# #         elif "DRS1992A" in nameexp:    
# #             if 1992 <= year <= 1994:
# #                 namersas = namersass[0]
# #                 exppath  = exppaths[0]    
# #             else:
# #                 pass
# #         elif "IC401" in nameexp:
# #             if year == 1992:
# #                 namersas = namersass[1]
# #                 exppath  = exppaths[1]
    
# #             else:
# #                 pass           

# #         # extract the name of the directory
# #         dirname         = dict()
# #         dirname['TT']   = f"{exppath}/{nameexp}/{namersas}/gridpt/mist/statoma/screen/yin"  
# #         dirname['TD']   = dirname['TT']
# #         dirname['SD']   = f"{exppath}/{nameexp}/{namersas}/gridpt/mist/statoma/snow/yin"  
        
# #         for namevar in namevars:
# #             print(namevar)
# #             # load the data
# #             data_var    = load_data(namevar, year, dirname[namevar])
            
# #             # format the date
# #             data_var['DATE'] = pd.to_datetime(data_var['DATE'], format="%Y%m%d%H")

# #             # Extract year and month
# #             data_var['MONTH'] = data_var['DATE'].dt.month
            
# #             # Group by 'LAT', 'LON', 'ALT', and 'MONTH', and count the size
# #             grouped = data_var.groupby(['LAT', 'LON', 'ALT', 'MONTH']).size().reset_index(name='COUNT')
            
# #             # Pivot the table to create one column for each month
# #             pivoted = grouped.pivot_table(index=['LAT', 'LON', 'ALT'], 
# #                                         columns='MONTH', values='COUNT', fill_value=0).reset_index()
            
# #             # List of month names and their corresponding month numbers
# #             month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# #             all_months = list(range(1, 13))  # All month numbers from 1 to 12

# #             # Identify missing months
# #             missing_months = set(all_months) - set(pivoted.columns[3:])

# #             # Insert columns for missing months with zeros
# #             for month in missing_months:
# #                 pivoted[month_names[month - 1]] = 0
    
# #             # Rename columns with month names
# #             pivoted.columns  = ['LAT', 'LON', 'ALT'] + month_names
            
# #             pivoted['Total'] = pivoted.iloc[:, 3:].sum(axis=1)
            
# #             # Save the DataFrame to a Parquet file
# #             namefileout      = f"{dirdata}/count_nbstation_assim_{namevar}_{nameexp}_{namersas}_{year}.parquet"
# #             pivoted.to_parquet(namefileout, index=False) 
