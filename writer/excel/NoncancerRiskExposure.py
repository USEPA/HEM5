import os
from math import log10, floor
from pandas import DataFrame

from writer.excel.ExcelWriter import ExcelWriter

class NoncancerRiskExposure(ExcelWriter):
    """
    Provides the population for each of the 14 TOSHIs that are greater than 6 different HI levels.
    """

    def __init__(self, targetDir, facilityId, model, plot_df, block_summary_chronic_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_noncancer_risk_exposure.xlsx")
        self.block_summary_chronic_df = block_summary_chronic_df

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded

    def calculateOutputs(self):

        self.headers = ['level', 'resp_hi', 'liver_hi', 'neuro_hi', 'develop_hi', 'repro_hi', 'kidney_hi', 'endo_hi',
                        'hema_hi', 'immune_hi', 'skel_hi', 'spleen_hi', 'thyroid_hi', 'wholeb_hi', 'ocular_hi']

        df = self.block_summary_chronic_df.copy()
        levels =[100, 50, 10, 1.0, 0.5, 0.2]
        toshis = ['hi_resp', 'hi_live', 'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul',
                  'hi_endo', 'hi_hema', 'hi_immu', 'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol']

        populations = []

        for level in levels:
            values = ["Greater than " + str(level)]

            for toshi in toshis:
                indexed = df[df.apply(lambda x: (self.round_to_sigfig(x[toshi])) > level, axis=1)]
                values.append(0 if indexed.empty else indexed['population'].agg('sum'))

            populations.append(values)

        result = DataFrame(populations)
        self.data = result.values