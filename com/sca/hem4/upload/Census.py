from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
import polars as pl
from tkinter import messagebox
from com.sca.hem4.log.Logger import Logger
import os
import pandas as pd


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

        qafile = os.path.join(self.fac_rootname, 'census_file_problem_values.xlsx')
                
        if len(rows_with_missing) > 0:

            if len(out_of_range.index) > 0:
                message = ('\nThere are missing values and out of range elevations/hill heights in the Census file. This model run will stop. '
                           + 'The row number and column of the missing values and out of range elevations/hill heights are reported in the file\n' 
                           + '"census_file_problem_values.xlsx" located in the output root folder.\n'
                           + 'Valid elevations/hill heigts are between -86m and 6190m.\n\n'
                           + 'Please correct the Census file and retry the HEM run. '
                           + 'Missing or out of range elevations or hill heights can be corrected by using the Revise Census utility. \n')
                Logger.logMessage(message)
                # Highlight missing values
                problem_rows = pd.concat([out_of_range, rows_with_missing])
                problem_rows.drop_duplicates(inplace=True)
                styled_df = problem_rows.style.highlight_null(color='yellow') \
                            .apply(self.highlight_out_of_range, lower_bound=-86 \
                                , upper_bound=6190, subset=['elev','hill'])
                styled_df.to_excel(qafile, engine='openpyxl', index=False)
                return None

            else:
                message = ('\nThere are missing values in the Census file. This model run will stop. '
                           + 'The row number and column of the missing values are reported in the file\n'
                           + '"census_file_problem_values.xlsx" located in the output root folder.\n\n'
                           + 'Please correct the Census file and retry the HEM run. '
                           + 'Missing elevations or hill heights can be filled in by using the Revise Census utility. \n')
                Logger.logMessage(message)
                styled_df = rows_with_missing.style.highlight_null(color='yellow')
                styled_df.to_excel(qafile, engine='openpyxl', index=False)
                return None
                
        else:
            if len(out_of_range.index) > 0:
                message = ('\nThere are out of range elevations/hill heights in the Census file. This model run will stop. '
                           + 'The row number and column of the out of range values are reported in the file\n'
                           + '"census_file_problem_values.xlsx" located in the output root folder.\n'
                           + 'Valid elevations/hill heigts are between -86m and 6190m.\n\n'
                           + 'Please correct the Census file and retry the HEM run. '
                           + 'Out of range elevations or hill heights can be corrected by using the Revise Census utility. \n')
                Logger.logMessage(message)
                styled_df = out_of_range.style.apply(self.highlight_out_of_range, lower_bound=-86 \
                                                     , upper_bound=6190, subset=['elev','hill'])
                styled_df.to_excel(qafile, engine='openpyxl', index=False)
                return None
                        
            else:
            
                return df
            
            
    def highlight_cells(self, cell):
        """
        Highlights cells based on multiple conditions.
        """
        color = 'background-color: yellow'
         
        # Check for null values
        if pd.isna(cell):
            return color
    
        # Check if a specific column is out of range
        if cell.name == 'elev' and not (-86 <= cell.iloc[0] <= 6190):
            return color
    
        if cell.name == 'hill' and not (-86 <= cell.iloc[0] <= 6190):
            return color
    
        # Return an empty string for all other cells
        return ''
    
    
    def highlight_out_of_range(self, s, lower_bound, upper_bound, color='background-color: yellow'):
        is_out_of_range = (s < lower_bound) | (s > upper_bound)
        return [color if v else '' for v in is_out_of_range]
            