import os

from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter

class AcuteBreakdown(ExcelWriter):
    """
    Provides the contribution of each emission source to the receptors (both populated and unpopulated) of maximum acute
    impact for each pollutant.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_acute_bkdn.xlsx")

    def getHeader(self):
        return ['pollutant', 'Source_id', 'Emis_type', 'maxcon_pop (µg/m3)', 'flag_1', 'maxcon_all (µg/m3)',
                'Flag_2']

    def generateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        # TODO
        self.data = []
        yield self.dataframe