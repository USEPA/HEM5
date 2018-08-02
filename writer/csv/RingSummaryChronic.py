import os
from writer.csv.CsvWriter import CsvWriter

class RingSummaryChronic(CsvWriter):
    """
    Provides the risk and each TOSHI for every census block modeled, as well as additional block information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_ring_summary_chronic.csv")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        self.headers = ['Lat', 'Lon', 'Overlap', 'Elevation', 'X', 'Y', 'Hill', 'Mir', 'Hi_resp', 'Hi_liver', 'Hi_neuro',
                        'Hi_devel', 'Hi_repro', 'Hi_kidney', 'Hi_ocular', 'Hi_endoc', 'Hi_hemato', 'Hi_immune', 'Hi_skel',
                        'Hi_spleen', 'Hi_thyroid', 'Hi_whol_bo', 'Distance', 'Angle', 'Sector']

        # TODO
        self.data = []