import os
from writer.excel.ExcelWriter import ExcelWriter

class AcuteChemicalPopulated(ExcelWriter):
    """
    Provides the maximum acute concentration for each modeled pollutant occurring at a populated(census block or
    user-defined) receptor, the acute benchmarks associated with each pollutant, and other max receptor
    information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_acute_chem_pop.xlsx")

    def getHeader(self):
        return ['Pollutant', 'Conc (µg/m3)', 'Conc sci (µg/m3)', 'Aegl_1 1hr (mg/m3)', 'Aegl_1 8hr (mg/m3)',
                'Aegl_2 1hr (mg/m3)', 'Aegl_2 8hr (mg/m3)', 'Erpg_1 (mg/m3)', 'Erpg_2 (mg/m3)', 'Idlh_10 (mg/m3)',
                'Mrl (mg/m3)', 'Rel (mg/m3)', 'Teel_0 (mg/m3)', 'Teel_1 (mg/m3)', 'Population',
                'Distance (in meters)', 'Angle (from north)', 'Elevation (in meters)', 'Hill Height (in meters)',
                'Fips', 'Block', 'Utm_east', 'Utm_north', 'Latitude', 'Longitude', 'Rec_type', 'Notes']

    def generateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        # TODO
        self.data = []
        yield self.dataframe