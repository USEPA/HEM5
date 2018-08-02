import os
from writer.excel import ExcelWriter

class Incidence(ExcelWriter):
    """
    Provides the incidence value for the total of all sources and all modeled pollutants as well
    as the incidence value for each source and each pollutant.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_incidence.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['Source_id', 'Pollutant', 'Emis_type', 'Incidence', 'Inc_rnd']

        # TODO
        self.data = []