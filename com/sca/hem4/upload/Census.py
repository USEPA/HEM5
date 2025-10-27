from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
import polars as pl
from tkinter import messagebox
from com.sca.hem4.log.Logger import Logger
import os


class Census(InputFile):

    def __init__(self, rootname):
        self.fac_rootname = rootname
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
        try:
            self.dataframe = self.readFromPathCsvPolars(self.colnames)
        except BaseException as ex:
            message = ('\nFailed to read the census file because the file is not properly formatted.\n' 
                       + 'This model run will stop. Please correct the census file before rerunning.\n'
                       + 'The detailed error message is:\n\n'
                       + str(ex) + '\n')
            Logger.logMessage(message)
            return None


    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Missing values in any columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------

        # convert lazyframe to pandas dataframe
        p_df = df.collect().to_pandas()
        
        # Identify rows with elev/hill higher than 6,190m (Dinali) or less than -86m
        # (Death Valley). These are out of range values.
        out_of_range = p_df[(p_df['elev'] < -86) | (p_df['elev'] > 6190)
                            | (p_df['hill'] < -86) | (p_df['hill'] > 6190)]
        
        # Identify rows with missing values
        rows_with_missing = p_df[p_df.isnull().any(axis=1)]

        # # Get the column names with missing values for each row
        # missing_cols_per_row = (p_df[rows_with_missing].isnull()
        #                         .apply(lambda x: x.index[x].tolist(), axis=1))
                
        if len(rows_with_missing) > 0:
            message = ('\nThere are missing values in the Census file. This model run will stop. \n'
                       + 'The row number and column of the missing values are reported in the file\n'
                       + '"census_file_outOfRange_values.xlsx" located in the output root foler.\n'
                       + 'Please correct the Census file and retry. \n'
                       + 'Missing elevations or hill heights can be filled in by using the Census Updater utility. \n')
            Logger.logMessage(message)
            qafile = os.path.join(self.fac_rootname, 'census_file_missing_values.xlsx')
            styled_df = rows_with_missing.style.highlight_null(color='yellow')
            styled_df.to_excel(qafile, engine='openpyxl', index=False)
            return None

            if len(out_of_range.index) > 0:
                message = ('\nThere are missing values and out of range elevations/hill heights in the Census file. This model run will stop. \n'
                           + 'The row number and column of the missing values and out of range elevations/hill heights are reported in the file\n' 
                           + '"census_file_outOfRange_values.xlsx" located in the output root foler.\n'
                           + 'Please correct the Census file and retry. \n'
                           + 'Missing or out of range elevations or hill heights can be corrected by using the Census Updater utility. \n')
                Logger.logMessage(message)
                qafile = os.path.join(self.fac_rootname, 'census_file_missing_and_outOfRange_values.xlsx')
                styled_df = rows_with_missing.style.highlight_null(color='yellow')
                styled_df.to_excel(qafile, engine='openpyxl', index=False)
                return None
        else:
            if len(out_of_range.index) > 0:
                message = ('\nThere are out of range elevations/hill heights in the Census file. This model run will stop. \n'
                           + 'The row number and column of the out of range values are reported in the file\n'
                           + '"census_file_outOfRange_values.xlsx" located in the output root foler.\n'
                           + 'Please correct the Census file and retry. \n'
                           + 'Out of range elevations or hill heights can be corrected in by using the Census Updater utility. \n')
                Logger.logMessage(message)
                qafile = os.path.join(self.fac_rootname, 'census_file_outOfRange_values.xlsx')
                styled_df = rows_with_missing.style.highlight_null(color='yellow')
                styled_df.to_excel(qafile, engine='openpyxl', index=False)
                return None
                        
                
            # message = ('\nThere are missing values in the Census file. This model run will stop. \n'
            #                  + 'Please correct the Census file and retry. \n'
            #                  + 'The missing values are identified below: \n')
            # Logger.logMessage(message)
            # for index, value in missing_cols_per_row.items():
            #     # iinenum must account for header and 0-index
            #     linenum = f"{index+2:,}"
            #     value_str = ", ".join(value)
            #     message = 'Line ' + str(linenum) + ' has missing values.'
            #     Logger.logMessage(message)
            
            # return None
        
            else:
            
                return df