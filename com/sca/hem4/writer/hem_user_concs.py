# -*- coding: utf-8 -*-
"""
Created on 

@author: 
"""
import numpy as np
import pandas as pd
import polars as pl
from scipy.interpolate import griddata
# from scipy.interpolate import Rbf
# from scipy.interpolate import SmoothBivariateSpline
import time

start = time.time()

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

rec_file_type = 'cen' # this will change to some variable in hem that indicates alt vs census
alt_col_names = ['Receptor ID','rectype','coordsys','lon','lat','utmz','elev','hill','pop']
census_inp = r'C:\Work\Mark Git\HEM4\census\Census2020.csv'
# census_inp = r'C:\Work\HEM5\Inputs\HEM5 templates\HEM5.0_alternate_receptors.csv'

# for now, explicitly pull in census csv into polars frame and filter;
# when incorporated into hem, use hem's model.census.dataframe or alternate receptors
datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'Receptor ID':pl.Utf8}
if rec_file_type == 'alt':
    census_df = pl.scan_csv(census_inp,dtypes=datatypes,
                            with_column_names=lambda cols: [col for col in alt_col_names])
else:
    census_df = pl.scan_csv(census_inp,dtypes=datatypes)

# Will need to insert some kind of limit on number of input points (per pollutant) so as to
# not overwhelm the griddata operation - maybe 100k receptors and 10 million overall records
userconcs_inp = r'C:\Work\HEM5\Inputs\HEM5 templates\HEM5.0_User_Conc_template_Nested_AllSources.csv'
userconcs_df = pd.read_csv(userconcs_inp, usecols = [0,1,2,3,4,5])
userconcs_df.columns = ['Receptor ID', 'Lon', 'Lat', 'Pollutant', 'CConc', 'AConc']
# breakpoint()

''' Filter user data by pollutant, get block/alternate receptors within extents of user input data,
    interpolate the input data to the block/alternate receptors for each pollutant
    
    NOTE: would need to do this twice if we decide to do acute also
'''
polls = list(userconcs_df['Pollutant'].unique())
pollframes = []
for poll in polls:
    tempuser_df = userconcs_df.loc[userconcs_df['Pollutant'] == poll]
    minlat = tempuser_df['Lat'].min()
    maxlat = tempuser_df['Lat'].max()
    minlon = tempuser_df['Lon'].min()
    maxlon = tempuser_df['Lon'].max()
        
    census_filt = census_df.filter(
        (pl.col('lat') <= maxlat) & (pl.col('lat') >= minlat) 
        & (pl.col('lon') <= maxlon) & (pl.col('lon') >= minlon)).collect().to_pandas()
    
    x = tempuser_df['Lon'].values
    y = tempuser_df['Lat'].values
    z = tempuser_df['CConc'].values
            
    xi = census_filt['lon'].values
    yi = census_filt['lat'].values
    
    zi = griddata((x, y), z, (xi, yi), method='linear') # Using griddata
    
    # rbf = Rbf(x,y,z, function='linear') # Using Rbf instead
    # zi = rbf(census_filt['lon'], census_filt['lat']) # Using Rbf instead
    
    # interp = SmoothBivariateSpline(x, y, z, s=0, kx=1, ky=1) # Using BiV instead
    # zi = interp(census_filt['lon'], census_filt['lat'], grid=False) # Using BiV instead
    
    census_filt['Pollutant'] = poll
    census_filt['cconc'] = zi
    poll_df = census_filt.dropna(subset=['cconc']) # drop blocks with nan conc because outside hull
    pollframes.append(poll_df)
    print(f"pollutant {poll} is done")

all_inner_df = pd.concat(pollframes, ignore_index=True)

print("Total time is ", time.time()-start)

# The rest of the code is just for testing...
actuals = r'C:\Work\Mark Git\HEM4\output\Fac1_allsources_50km\Fac1-NC\Fac1-NC_all_inner_receptors.csv'
actuals_types = {'FIPs': str, 'Block': str}
actuals_df = pd.read_csv(actuals, dtype=actuals_types)
actuals_df['blockid'] = actuals_df['FIPs'] + actuals_df['Block']
actuals_agg = actuals_df.groupby(['blockid', 'Pollutant'], as_index=False).sum()
actuals_agg2 = actuals_agg[['blockid', 'Pollutant', 'Conc (µg/m3)']]
comp_df = pd.merge(actuals_agg2, all_inner_df, on=['blockid', 'Pollutant'],how='inner')
comp_df['pct_diff'] = np.abs((comp_df['cconc'] - comp_df['Conc (µg/m3)'])/comp_df['Conc (µg/m3)']*100)
comp_df[['pct_diff']].describe()


