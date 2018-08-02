import os
from writer.excel import ExcelWriter

class OverlappingSourceReceptors(ExcelWriter):
    """
    Provides a list of receptors that were identified as located within the user-specified overlap distance of an
    emission source.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_overlapping_source_receptors.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['rec_type', 'fips', 'block', 'population', 'utm_east', 'utm_north', 'source_id', 'sw_corner',
                        'nw_corner', 'ne_corner', 'se_corner']

        # TODO
        self.data = []