from abc import ABC
from abc import abstractmethod
import pandas as pd

class InputFile(ABC):

    def __init__(self, path):
        self.path = path
        self.dataframe = None
        self.log = []
        self.createDataframe()

    @abstractmethod
    def createDataframe(self):
        return

    def readFromPath(self, colnames, typeconverters):
        with open(self.path, "rb") as f:
            return pd.read_excel(f, names=colnames, converters=typeconverters)

    def read(self, path):
        with open(path, "rb") as f:
            return pd.read_excel(f)

    def to_numeric(self, slice):
        return pd.to_numeric(slice,errors="coerce")