import os
from writer.csv.CsvWriter import CsvWriter

class AllInnerReceptors(CsvWriter):
    """
    Provides the annual average concentration modeled at every census block within the modeling cutoff distance,
    specific to each source ID and pollutant, along with receptor information, and acute concentration (if modeled) and
    wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):

        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_inner_receptors.csv")

    def calculateOutputs(self):
        """
        Do something with the model and plot dataframes, setting self.headers and self.data in the process.
        """

        self.headers = ['Lat',	'Lon', 'Overlap', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m2',
                        'Elevation', 'Ddp_g_m2', 'Wdp_g_m2', 'Population', 'Fips', 'Block']

        # TODO
        self.data = []