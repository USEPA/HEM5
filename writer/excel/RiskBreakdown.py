import os
from writer.excel import ExcelWriter

class RiskBreakdown(ExcelWriter):
    """
    Provides the max cancer risk and max TOSHI values at populated block (“MIR”) sites and at any (“max offsite impact”)
    sites broken down by source and pollutant, including total sources and all modeled pollutants combined, as well as
    the pollutant concentration, URE and RfC values.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_risk_breakdown.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['site_type', 'parameter', 'source_id', 'pollutant', 'emis_type', 'value', 'value_rnd',
                        'conc (µg/m3)', 'conc rnd (µg/m3)', 'emis tpy', 'ure 1/(µg/m3)', 'rfc (mg/m3)']

        # TODO
        self.data = []