import os

import pandas as pd
from numpy import int16
from pandas import np

from com.sca.ej.data.ACSDataset import ACSDataset

acs_path = "/DeepGreen/SCA/ACS18BGEstimates_EJsubset-enhancified.xlsx"
output_dir = "/DeepGreen/SCA"

class ACSLevelGenerator:

    def __init__(self):
        self.acs = ACSDataset(path=acs_path)
        self.output_dir = output_dir

        self.all_columns = ['ID', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
                            'PCT_AMERIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18',
                            'PCT_AGE_GT64', 'POV_UNIVERSE_FRT', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99',
                            'EDU_UNIVERSE', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE',
                            'PCT_NON_HISP_BLACK', 'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE',
                            'PCT_HISP_BLACK', 'PCT_HISP_AMERIND', 'PCT_HISP_OTHER']

    def generate_tract_data(self):
        df = self.acs.dataframe

        # First filter out any records with missing data
        df = df.dropna()
        df = df.astype({"TOTALPOP": int16})

        # Next drop the last char from the block group ID to get the tract ID
        df['STCNTRBG'] = df['STCNTRBG'].astype(str).str[:-1]

        # Calculate a weighted mean of all fields based on population
        df = df.groupby(['STCNTRBG']).apply(self.my_agg)

        filename = os.path.join(self.output_dir, "ACS-levels.xlsx")
        df.to_excel(filename, index=False, columns=self.all_columns, header=self.all_columns)

    def generate_county_data(self):
        df = self.acs.dataframe

        # First filter out any records with missing data
        df = df.dropna()
        df = df.astype({"TOTALPOP": int16})

        # Keep only the first 5 chars to get the county ID
        df['STCNTRBG'] = df['STCNTRBG'].astype(str).str[:5]

        # Calculate a weighted mean of economic fields based on population
        df = df.groupby(['STCNTRBG']).apply(self.my_agg)

        filename = os.path.join(self.output_dir, "ACS-levels.xlsx")

        df.to_excel(filename, index=False, columns=self.all_columns, header=self.all_columns)

    def my_agg(self, x):
        names = {'ID': x['STCNTRBG'].iloc[0],
                 'TOTALPOP': (x['TOTALPOP']).sum(skipna=True),
                 'PCT_MINORITY': (x['TOTALPOP'] * x['PCT_MINORITY']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_WHITE': (x['TOTALPOP'] * x['PCT_WHITE']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_BLACK': (x['TOTALPOP'] * x['PCT_BLACK']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HISP': (x['TOTALPOP'] * x['PCT_HISP']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_ASIAN': (x['TOTALPOP'] * x['PCT_ASIAN']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_AMERIND': (x['TOTALPOP'] * x['PCT_AMERIND']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HAWPAC': (x['TOTALPOP'] * x['PCT_HAWPAC']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_OTHER_RACE': (x['TOTALPOP'] * x['PCT_OTHER_RACE']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_TWOMORE': (x['TOTALPOP'] * x['PCT_TWOMORE']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_AGE_LT18': (x['TOTALPOP'] * x['PCT_AGE_LT18']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_AGE_GT64': (x['TOTALPOP'] * x['PCT_AGE_GT64']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_LOWINC': (x['TOTALPOP'] * x['PCT_LOWINC']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_INC_POV_LT50': (x['TOTALPOP'] * x['PCT_INC_POV_LT50']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_INC_POV_50TO99': (x['TOTALPOP'] * x['PCT_INC_POV_50TO99']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_EDU_LTHS': (x['TOTALPOP'] * x['PCT_EDU_LTHS']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_LINGISO': (x['TOTALPOP'] * x['PCT_LINGISO']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_NON_HISP': (x['TOTALPOP'] * x['PCT_NON_HISP']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_NON_HISP_WHITE': (x['TOTALPOP'] * x['PCT_NON_HISP_WHITE']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_NON_HISP_BLACK': (x['TOTALPOP'] * x['PCT_NON_HISP_BLACK']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_NON_HISP_AMERIND': (x['TOTALPOP'] * x['PCT_NON_HISP_AMERIND']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_NON_HISP_OTHER': (x['TOTALPOP'] * x['PCT_NON_HISP_OTHER']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HISP_WHITE': (x['TOTALPOP'] * x['PCT_HISP_WHITE']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HISP_BLACK': (x['TOTALPOP'] * x['PCT_HISP_BLACK']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HISP_AMERIND': (x['TOTALPOP'] * x['PCT_HISP_AMERIND']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'PCT_HISP_OTHER': (x['TOTALPOP'] * x['PCT_HISP_OTHER']).sum(skipna=True)/x['TOTALPOP'].sum(skipna=True),
                 'POV_UNIVERSE_FRT': (x['POV_UNIVERSE_FRT']).sum(skipna=True),
                 'EDU_UNIVERSE': (x['EDU_UNIVERSE']).sum(skipna=True)}
        return pd.Series(names, index=self.all_columns)


generator = ACSLevelGenerator()
generator.generate_county_data()
