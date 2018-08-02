import os
from writer.excel import ExcelWriter

class CancerRiskExposure(ExcelWriter):
    """
    Provides the population with a cancer risk greater than or equal to 6 different risk levels.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_cancer_risk_exposure.xlsx")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['level', 'population']

        # TODO
        self.data = []