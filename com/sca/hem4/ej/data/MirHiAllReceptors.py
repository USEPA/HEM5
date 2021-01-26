import datetime
import os
import re
import pandas as pd
import numpy as np
class MirHiAllReceptors():

    def __init__(self, path, createDataframe=True):
        self.path = path
        self.dataframe = None
        self.log = []
        self.numericColumns = []
        self.strColumns = []
        self.skiprows = 1

        if createDataframe:
            self.createDataframe()

    # Read values in from a source .xls(x) file. Note that we initially read everything in as a string,
    # and then convert columns which have been specified as numeric to a float64. That way, all empty
    # values in the resultant dataframe become NaN values. All values will either be strings or float64s.
    def readFromPath(self, colnames):
        with open(self.path, "rb") as f:

            try:
                df = pd.read_excel(f, skiprows=self.skiprows, names=colnames, dtype=str, na_values=[''], keep_default_na=False)

            except BaseException as e:

                if isinstance(e, ValueError):

                    msg = e.args[0]
                    if msg.startswith("Length mismatch"):
                        # i.e. 'Length mismatch: Expected axis has 5 elements, new values have 31 elements'
                        p = re.compile("Expected axis has (.*) elements, new values have (.*) elements")
                        result = p.search(msg)
                        custom_msg = "Length Mismatch: Input file has " + result.group(1) + " columns, but should have " + \
                                     result.group(2) + " columns. Please make sure you have selected the correct file or file version."
                        print("Error uploading input file: " + custom_msg)
                    else:
                        print("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")
                else:
                    print("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")

            else:
                df = df.astype(str).applymap(self.convertEmptyToNaN)
                types = self.get_column_types()
                df = df.astype(dtype=types)

                return df

    # Read values in from a source .csv file. Note that we initially read everything in as a string,
    # and then convert columns which have been specified as numeric to a float64. That way, all empty
    # values in the resultant dataframe become NaN values. All values will either be strings or float64s.
    def readFromPathCsv(self, colnames):
        with open(self.path, "rb") as f:
            
            self.skiprows = 1
            
            try:
                
                df = pd.read_csv(f, skiprows=self.skiprows, names=colnames, dtype=str, na_values=[''], keep_default_na=False)
                  
            except BaseException as e:
                
                if isinstance(e, ValueError):

                    msg = e.args[0]
                    if msg.startswith("Length mismatch"):
                        # i.e. 'Length mismatch: Expected axis has 5 elements, new values have 31 elements'
                        p = re.compile("Expected axis has (.*) elements, new values have (.*) elements")
                        result = p.search(msg)
                        custom_msg = "Length Mismatch: Input file has " + result.group(1) + " columns, but should have " + \
                                     result.group(2) + " columns. Please make sure you have selected the correct file or file version."
                        print("Error uploading input file: " + custom_msg)
                    else:
                        print("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")
                else:
                    print("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")
                
            else:
                
                df = df.astype(str).applymap(self.convertEmptyToNaN)
                types = self.get_column_types()
                df = df.astype(dtype=types)
                
                return df


    def getColumns(self):
        return ['fips', 'block', 'lon', 'lat', 'population', 'mir', 'mir_rounded', 'hi_resp', 'hi_live',
                'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul', 'hi_endo', 'hi_hema', 'hi_immu',
                'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol', 'fac_count']

    def createDataframe(self):
        # Type setting for CSV reading
        self.numericColumns = ['lon', 'lat', 'population', 'mir', 'mir_rounded', 'hi_resp', 'hi_live',
                               'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul', 'hi_endo', 'hi_hema', 'hi_immu',
                               'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol', 'fac_count']

        self.strColumns = ['fips', 'block']
        df = self.readFromPathCsv(self.getColumns())

        self.dataframe = df.fillna("")
        return self.dataframe

    # This method is being applied to every cell to guard against values which
    # have only whitespace.
    def convertEmptyToNaN(self, x):
        y = x.strip()
        if len(y) == 0:
            return 'nan'
        else:
            return y

    def get_column_types(self):
        floatTypes = {col: np.float64 for col in self.numericColumns}

        dtypes = {col: str for col in self.strColumns}

        # merge both converter dictionaries and return
        dtypes.update(floatTypes)
        return dtypes

    def to_numeric(self, slice):

        try:
            df = pd.to_numeric(slice,errors="coerce")
        except BaseException as e:
            print(str(e))
        else:
            return df

    @staticmethod
    def is_numeric(x):
        try:
            float(x)
            return x
        except:
            return "nan"