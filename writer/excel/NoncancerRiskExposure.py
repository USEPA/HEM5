import os
from writer.excel import ExcelWriter

class NoncancerRiskExposure(ExcelWriter):
    """
    Provides the population for each of the 14 TOSHIs that are greater than 6 different HI levels.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_noncancer_risk_exposure.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['level', 'resp_hi', 'liver_hi', 'neuro_hi', 'develop_hi', 'repro_hi', 'kidney_hi', 'endo_hi',
                        'hema_hi', 'immune_hi', 'skel_hi', 'spleen_hi', 'thyroid_hi', 'wholeb_hi', 'ocular_hi']

        # TODO
        self.data = []