import os
from abc import ABC
from abc import abstractmethod
import pandas as pd

class InputFile(ABC):

    def __init__(self, path, createDataframe=True):
        self.path = path
        self.dataframe = None
        self.log = []
        self.numericColumns = []
        self.strColumns = []
        self.skiprows = 0

        if createDataframe:
            print(self.path)
            self.createDataframe()

    @abstractmethod
    def createDataframe(self):
        return

    # Read values in from a source .xls(x) file. Note that we initially read everything in as a string,
    # and then convert columns which have been specified as numeric to a float64. That way, all empty
    # values in the resultant dataframe become NaN values. All values will either be strings or float64s.
    def readFromPath(self, colnames):
        with open(self.path, "rb") as f:
            df = pd.read_excel(f, skiprows=self.skiprows, names=colnames, dtype=str, na_values=[''], keep_default_na=False)
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
            df = pd.read_csv(f, skiprows=self.skiprows, names=colnames, dtype=str, na_values=[''], keep_default_na=False)
            df = df.astype(str).applymap(self.convertEmptyToNaN)
            types = self.get_column_types()
            df = df.astype(dtype=types)
            return df

    # This method is being applied to every cell to guard against values which
    # have only whitespace.
    def convertEmptyToNaN(self, x):
        y = x.strip()
        if len(y) == 0:
            return 'nan'
        else:
            return y

    def read(self, path):
        with open(path, "rb") as f:
            return pd.read_excel(f)

    def get_column_types(self):
        floatTypes = {col: pd.np.float64 for col in self.numericColumns}

        dtypes = {col: str for col in self.strColumns}

        # merge both converter dictionaries and return
        dtypes.update(floatTypes)
        return dtypes

    def to_numeric(self, slice):
        return pd.to_numeric(slice,errors="coerce")