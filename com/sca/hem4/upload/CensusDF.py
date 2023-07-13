from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
import polars as pl
import pandas
import os


class CensusDF(InputFile):

    def __init__(self):
        InputFile.__init__(self, "census/Census2020.csv")
        self.censusPath = os.path.join("census", "Census2020.csv")

    def createDataframe(self):

        # Column names
        colnames = ['fips', 'blockid', 'population', 'lat', 'lon', 'elev',
                    'hill', 'urban_pop']
        
        # Specify dtypes for all fields
        self.datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'population':pl.Int64, 
                          'lat':pl.Float64, 'lon':pl.Float64, 'elev':pl.Float64, 
                          'hill':pl.Float64, 'urban_pop':pl.Int64}

        # Create pandas dataframe
        df = self.readFromPathCsvPolarsDF(colnames)
        
        self.dataframe = df
        
