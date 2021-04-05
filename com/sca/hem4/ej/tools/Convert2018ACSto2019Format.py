# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 19:52:45 2021

@author: Steve Fudge
"""

import pandas as pd
import numpy as np


def get_column_types(numericColumns, strColumns):
    floatTypes = {col: np.float64 for col in numericColumns}

    dtypes = {col: str for col in strColumns}

    # merge both converter dictionaries and return
    dtypes.update(floatTypes)
    return dtypes


#----------------------- ACS block group data ----------------------------------------------------------

acs2018_file = r"C:\Git_HEM4\ACS data backup\acs_2018.xlsx"
reformatted_acs2018_file = r"C:\Git_HEM4\ACS data backup\acs_2018_reformat.xlsx"


columns2018 = ['STCNTRBG', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
               'PCT_AMIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18', 'PCT_AGE_GT64',
               'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99', 'EDU_UNIVERSE',
               'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK',
               'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND',
               'PCT_HISP_OTHER', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG', 'FRACT_25UP', 'HOUSEHOLDS']

columns2019 = ['STCNTRBG', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_AMIND', 'PCT_OTHER_RACE', 'PCT_HISP',
               'PCT_AGE_LT18', 'PCT_AGE_GT64', 'PCT_LOWINC', 'PCT_POV', 'AGE_25UP', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'AGE_UNIVERSE',
               'POV_UNIVERSE', 'EDU_UNIVERSE', 'ISO_UNIVERSE', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']

numericColumns2018 = ['TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
               'PCT_AMIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18', 'PCT_AGE_GT64',
               'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99', 'EDU_UNIVERSE',
               'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK',
               'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND',
               'PCT_HISP_OTHER', 'FRACT_25UP', 'HOUSEHOLDS']

strColumns2018 = ['STCNTRBG', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']


# Load 2018 data into dataframe
acs_df = pd.read_excel(acs2018_file, skiprows=0, names=columns2018, dtype=str, na_values=[''], keep_default_na=False)
types = get_column_types(numericColumns2018, strColumns2018)
acs_df = acs_df.astype(dtype=types)

# Create a couple of columns needed in 2019
acs_df['PCT_POV'] = acs_df['PCT_INC_POV_LT50'] + acs_df['PCT_INC_POV_50TO99']
acs_df['AGE_UNIVERSE'] = acs_df['TOTALPOP']

# Change percent white column
acs_df['PCT_WHITE'] = acs_df['PCT_NON_HISP_WHITE']

# Write using 2019 format
acs_df.to_excel(reformatted_acs2018_file, columns=columns2019, index=False, header=True)


#----------------------- ACS tract/county default data --------------------------------------------------

acs2018_default_file = r"C:\Git_HEM4\ACS data backup\acs-levels_2018.xlsx"
reformatted_acs2018_default_file = r"C:\Git_HEM4\ACS data backup\acs-levels_2018_reformat.xlsx"

columns2018 = ['ID', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
                'PCT_AMIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18',
                'PCT_AGE_GT64', 'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99',
                'EDU_UNIVERSE', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK',
                'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND',
                'PCT_HISP_OTHER', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG', 'FRACT_25UP']

columns2019 = ['ID', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_AMIND', 'PCT_OTHER_RACE', 'PCT_HISP',
               'PCT_AGE_LT18', 'PCT_AGE_GT64', 'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_POV', 'EDU_UNIVERSE', 'PCT_EDU_LTHS', 
               'PCT_LINGISO', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']

numericColumns2018 = ['TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
                'PCT_AMIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18',
                'PCT_AGE_GT64', 'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99',
                'EDU_UNIVERSE', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK',
                'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND',
                'PCT_HISP_OTHER', 'FRACT_25UP']

strColumns2018 = ['ID', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']


# Load 2018 data into dataframe
acsdef_df = pd.read_excel(acs2018_default_file, skiprows=0, names=columns2018, dtype=str, na_values=[''], keep_default_na=False)
types = get_column_types(numericColumns2018, strColumns2018)
acsdef_df = acsdef_df.astype(dtype=types)

# Change percent white column
acsdef_df['PCT_WHITE'] = acsdef_df['PCT_NON_HISP_WHITE']

# Create a few columns needed in 2019
acsdef_df['PCT_POV'] = acsdef_df['PCT_INC_POV_LT50'] + acsdef_df['PCT_INC_POV_50TO99']
acsdef_df['ISO_UNIVERSE'] = ''
acsdef_df['POP_FLAG'] = ''

# Write using 2019 format
acsdef_df.to_excel(reformatted_acs2018_default_file, columns=columns2019, index=False, header=True)





def get_column_types():
    floatTypes = {col: np.float64 for col in self.numericColumns}

    dtypes = {col: str for col in self.strColumns}

    # merge both converter dictionaries and return
    dtypes.update(floatTypes)
    return dtypes

