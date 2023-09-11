# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:57:27 2023

@author: SteveFudge
"""

from com.sca.hem4.upload.InputFile import InputFile

class CensusChanges(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):
        
        # Specify dtypes for all fields
        self.numericColumns = ["lat", "lon", "population", "elev", "hill", "urban_pop"]
        self.strColumns = ["change", "facid", "category", "blockid"]

        changes_df = self.readFromPath(('change', 'facid', 'category', 'blockid',
                                        'lat', 'lon', 'population', 'elev', 'hill', 'urban_pop'))

        if changes_df.empty == False:
            changes_df[['population', 'urban_pop']] = changes_df[['population', 'urban_pop',
                                                                  'elev', 'hill']].fillna(0)
            changes_df['population'] = changes_df['population'].astype(int)
            changes_df['urban_pop'] = changes_df['urban_pop'].astype(int)
        
        self.dataframe = changes_df
        
    