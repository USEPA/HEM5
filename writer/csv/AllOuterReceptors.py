import os
from writer.csv.CsvWriter import CsvWriter

class AllOuterReceptors(CsvWriter):
    """
    Provides the annual average concentration interpolated at every census block beyond the modeling cutoff distance but
    within the modeling domain, specific to each source ID and pollutant, along with receptor information, and acute
    concentration (if modeled) and wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_outer_receptors.csv")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        self.headers = ['Lat', 'Lon', 'Overlap', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m3',
                        'Population', 'Fips', 'Block', 'Elev']

        # TODO
        self.data = []