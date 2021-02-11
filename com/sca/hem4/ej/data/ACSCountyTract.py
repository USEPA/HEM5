import datetime
import os
import re
import numpy as np
import pandas as pd

from com.sca.hem4.log import Logger


class ACSCountyTract:

    def __init__(self, path, createDataframe=True):
        self.path = path
        self.dataframe = None
        self.log = []
        self.numericColumns = []
        self.strColumns = []
        self.skiprows = 0

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
                        Logger.logMessage("Error uploading input file: " + custom_msg)
                    else:
                        Logger.logMessage("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")
                else:
                    Logger.logMessage("Error uploading input file: " + str(e) + " Please make sure you have selected the correct file or file version.")

            else:
                df = df.astype(str).applymap(self.convertEmptyToNaN)
                types = self.get_column_types()
                df = df.astype(dtype=types)

                return df

    def getColumns(self):
        return ['ID', 'TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
                'PCT_AMERIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18',
                'PCT_AGE_GT64', 'POV_UNIVERSE_FRT', 'PCT_LOWINC', 'PCT_INC_POV_LT50', 'PCT_INC_POV_50TO99',
                'EDU_UNIVERSE', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP', 'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK',
                'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER', 'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND',
                'PCT_HISP_OTHER', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG', 'FRACT_25UP']

    def createDataframe(self):
        # Type setting for reading
        self.numericColumns = ['TOTALPOP', 'PCT_MINORITY', 'PCT_WHITE', 'PCT_BLACK', 'PCT_HISP', 'PCT_ASIAN',
                               'PCT_AMERIND', 'PCT_HAWPAC', 'PCT_OTHER_RACE', 'PCT_TWOMORE', 'PCT_AGE_LT18',
                               'PCT_AGE_GT64', 'POV_UNIVERSE_FRT', 'PCT_LOWINC', 'PCT_INC_POV_LT50',
                               'PCT_INC_POV_50TO99', 'EDU_UNIVERSE', 'PCT_EDU_LTHS', 'PCT_LINGISO', 'PCT_NON_HISP',
                               'PCT_NON_HISP_WHITE', 'PCT_NON_HISP_BLACK', 'PCT_NON_HISP_AMERIND', 'PCT_NON_HISP_OTHER',
                               'PCT_HISP_WHITE', 'PCT_HISP_BLACK', 'PCT_HISP_AMERIND', 'PCT_HISP_OTHER',
                               'FRACT_25UP']
        self.strColumns = ['ID', 'POVERTY_FLAG', 'EDUCATION_FLAG', 'LING_ISO_FLAG']

        df = self.readFromPath(self.getColumns())

        self.dataframe = df

        # These are not in our data set natively but can be calculated from available fields...
        #self.dataframe['PCT_AGE_GT25'] = self.dataframe.apply(lambda row: self.create_edu_universe(row), axis=1)

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
            Logger.logMessage(str(e))
        else:
            return df

    @staticmethod
    def is_numeric(x):
        try:
            float(x)
            return x
        except:
            return "nan"
