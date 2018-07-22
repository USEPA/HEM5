import os

from writer.excel.ExcelWriter import ExcelWriter

class AcuteBreakdown(ExcelWriter):
    """
    Provides the contribution of each emission source to the receptors (both populated and unpopulated) of maximum acute
    impact for each pollutant.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_acute_bkdn.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot file, setting self.headers and self.data in the process.
        """
        self.headers = ['pollutant', 'Source_id', 'Emis_type', 'maxcon_pop (µg/m3)', 'flag_1', 'maxcon_all (µg/m3)',
                        'Flag_2']

        # TODO
        self.data = []