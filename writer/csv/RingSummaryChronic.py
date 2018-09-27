import os
from writer.csv.CsvWriter import CsvWriter

class RingSummaryChronic(CsvWriter):
    """
    Provides the risk and each TOSHI for every census block modeled, as well as additional receptor information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_ring_summary_chronic.csv")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        self.headers = ['X', 'Y', 'Lat', 'Lon', 'Overlap', 'Distance', 'Angle', 'Sector', 'Elevation', 'Hill', 'Mir',
                        'Hi_resp', 'Hi_liver', 'Hi_neuro', 'Hi_devel', 'Hi_repro', 'Hi_kidney', 'Hi_ocular', 'Hi_endoc',
                        'Hi_hemato', 'Hi_immune', 'Hi_skel', 'Hi_spleen', 'Hi_thyroid', 'Hi_whol_bo']


        #extract polar concs from plotfile and round the utm coordinates
        polgrid_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
        polgrid_df.utme = polgrid_df.utme.round()
        polgrid_df.utmn = polgrid_df.utmn.round()


        # TODO
        self.data = self.createData(polgrid_df)

    def createData(self, polgrid_df):

        summary = polgrid_df[['utme', 'utmn', 'elev', 'hill']].copy()
        summary.insert(2, column='lat', value=0)
        summary.insert(3, column='lon', value=0)

        return summary.values
