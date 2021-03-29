# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 19:52:45 2021

@author: Steve Fudge
"""

import pandas as pd

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


# Load 2018 data into dataframe
acs_df = pd.read_excel(acs2018_file, skiprows=0, names=columns2018, dtype=str, na_values=[''], keep_default_na=False)

# Create a couple of columns needed in 2019
acs_df['PCT_POV'] = acs_df['PCT_INC_POV_LT50'] + acs_df['PCT_INC_POV_50TO99']
acs_df['AGE_UNIVERSE'] = acs_df['TOTALPOP']

# Write using 2019 format
acs_df.to_excel(reformatted_acs2018_file, columns=columns2019, index=False, header=True)


#----------------------- ACS tract/county default data --------------------------------------------------

columns2019 = ['ID', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_AMIND', 'PCT_OTHER_RACE', 'PCT_HISP',
               'PCT_AGE_LT18', 'PCT_AGE_GT64', 'POV_UNIVERSE', 'PCT_LOWINC', 'PCT_POV', 'EDU_UNIVERSE', 'PCT_EDU_LTHS', 
               'ISO_UNIVERSE', 'PCT_LINGISO', 'POP_FLAG', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']


