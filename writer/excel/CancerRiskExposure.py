import os
from math import log10, floor
from pandas import DataFrame
from writer.excel.ExcelWriter import ExcelWriter


class CancerRiskExposure(ExcelWriter):
    """
    Provides the population with a cancer risk greater than or equal to 6 different risk levels.
    """

    def __init__(self, targetDir, facilityId, model, plot_df, block_summary_chronic_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_cancer_risk_exposure.xlsx")
        self.block_summary_chronic_df = block_summary_chronic_df

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        #print("Rounded " + str(x) + " to " + str(rounded))
        return rounded

    def calculateOutputs(self):

        self.headers = ['level', 'population']

        bucketHeaders = ["Greater than or equal to 1 in 1,000", "Greater than or equal to 1 in 10,000",
                         "Greater than or equal to 1 in 20,000", "Greater than or equal to 1 in 100,000",
                         "Greater than or equal to 1 in 1,000,000", "Greater than or equal to 1 in 10,000,000"]

        scalingFactor = 1000000

        df = self.block_summary_chronic_df.copy()
        levels =[1000, 100, 50, 10, 1, 0.1]
        populations = []

        for level in levels:
            indexed = df[df.apply(lambda x: (self.round_to_sigfig(scalingFactor*x['mir'])) > level, axis=1)]
            populations.append(0 if indexed.empty else indexed['population'].agg('sum'))

        buckets = list(zip(bucketHeaders, populations))
        result = DataFrame(buckets)

        self.data = result.values