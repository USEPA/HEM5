from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
import polars as pl
from tkinter import messagebox
from com.sca.hem4.log.Logger import Logger


class Census(InputFile):

    def __init__(self):
        InputFile.__init__(self, "census/Census2020.csv")

    def createDataframe(self):

        # Column names
        self.colnames = ['fips', 'blockid', 'population', 'lat', 'lon', 'elev',
                    'hill']
        
        # Specify dtypes for all fields
        self.datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'population':pl.Int64, 
                          'lat':pl.Float64, 'lon':pl.Float64, 'elev':pl.Float64, 
                          'hill':pl.Float64}

        # Create polars lazyframe of the national census data
        self.dataframe = self.readFromPathCsvPolars(self.colnames)
        


    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Missing values in any columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------

        # convert lazyframe to pandas dataframe
        p_df = df.collect().to_pandas()

        # Identify rows with missing values
        rows_with_missing = p_df.isnull().any(axis=1)

        # Get the column names with missing values for each row
        missing_cols_per_row = (p_df[rows_with_missing].isnull()
                                .apply(lambda x: x.index[x].tolist(), axis=1))

                
        if len(missing_cols_per_row) > 0:
                        
            message = ('\nThere are missing values in the Census file. This model run will stop. \n'
                             + 'Please correct the Census file and retry. \n'
                             + 'The missing values are identified below: \n')
            Logger.logMessage(message)
            for index, value in missing_cols_per_row.items():
                index_comma = f"{index:,}"
                value_str = ", ".join(value)
                message = 'Line ' + str(index_comma) + ' has missing values in columns [' + value_str + ']'
                Logger.logMessage(message)
            
            return None
        
        else:
            
            return df