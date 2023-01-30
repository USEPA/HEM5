from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
import polars as pl
import pandas


class Census(InputFile):

    def __init__(self):
        InputFile.__init__(self, "census/Census2020_HEM_28Jun22.csv")

    def createDataframe(self):

        # Column names
        colnames = ['fips', 'blockid', 'population', 'lat', 'lon', 'elev',
                    'hill', 'urban_pop']
        
        # Specify dtypes for all fields
        self.datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'population':pl.Int64, 
                          'lat':pl.Float64, 'lon':pl.Float64, 'elev':pl.Float64, 
                          'hill':pl.Float64, 'urban_pop':pl.Int64}

        # Create polars lazyframe of the national census data
        self.dataframe = self.readFromPathCsvPolars()
        
        # # Create polars dataframe
        # pldf = self.readFromPathCsvPolars(colnames)        
        # pldf = pldf.fill_nan(0)

        # # Cast polars dataframe to pandas
        # self.dataframe = pldf.to_pandas()