import os
from com.sca.hem4.writer.csv.CsvWriter import CsvWriter

class Temporal(CsvWriter):
    """
    Provides the annual average pollutant concentrations at different time periods (depending on the temporal option
    chosen) for all pollutants and receptors.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_temporal.csv")

    def getHeader(self):
        return ['Fips', 'Block', 'Population', 'Lat', 'Lon', 'Pollutant', 'Emis_type', 'Overlap', 'Modeled',
                'C_01', 'C_02', 'C_03', 'C_04 ', 'etc, depending on temporal variations selected']

    def generateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        # TODO
        self.data = []
        yield self.dataframe