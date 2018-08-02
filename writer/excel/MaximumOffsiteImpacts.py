import os
from writer.excel import ExcelWriter

class MaximumOffsiteImpacts(ExcelWriter):
    """
    Provides the maximum cancer risk and all 14 TOSHIs at any receptor, either a populated (census block, user defined)
    or an unpopulated (polar grid) receptor, as well as additional receptor information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_maximum_offsite_impacts.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['Parameter', 'Value', 'Value_rnd', 'Value_sci', 'Population', 'Distance (in meters)',
                        'Angle (from north)', 'Elevation (in meters)', 'Hill Height (in meters)', 'Fips', 'Block',
                        'Utm_east', 'Utm_north', 'Latitude', 'Longitude', 'Rec_type', 'Notes', 'Warning']

        # TODO
        self.data = []