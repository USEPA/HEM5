import os
import pandas as pd

from com.sca.hem4.CensusBlocks import *
from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.CsvWriter import CsvWriter

class Temporal(CsvWriter):
    """
    Provides the annual average pollutant concentrations at different time periods (depending on the temporal option
    chosen) for all pollutants and receptors.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_temporal.csv")

        self.resolution = 4 # should come from model.facops or similar...
        self.seasonal = True # again, needs to come from model opts

    def getHeader(self):
        defaultHeader = ['Fips', 'Block', 'Population', 'Lat', 'Lon', 'Pollutant', 'Emis_type', 'Overlap', 'Block type']
        return self.extendsCols(defaultHeader)

    def getColumns(self):
        defaulsCols = [fips, block, population, lat, lon, pollutant, emis_type, overlap, block]
        return self.extendsCols(defaulsCols)

    def extendsCols(self, default):
        n_seas = 4 if self.seasonal else 1
        n_hrblk = round(24/self.resolution)
        concCols = n_seas * n_hrblk

        for c in range(1, concCols+1):
            colnum = str(c)
            if len(colnum) < 2:
                colnum = "0" + colnum
            colName = "C_" + colnum
            default.append(colName)

        return default

    def generateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        dlist = []
        col_list = self.getColumns()
        innerconc_df = pd.DataFrame(dlist, columns=col_list)

        # dataframe to array
        self.dataframe = innerconc_df
        self.data = self.dataframe.values

        yield self.dataframe