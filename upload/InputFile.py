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
        return pd.read_excel(open(self.path, "rb"), names=colnames, converters=typeconverters)

    def read(self, path):
        return pd.read_excel(open(path, "rb"))

    def to_numeric(self, slice):
        return pd.to_numeric(slice,errors="coerce")