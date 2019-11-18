from math import floor, log10

from pandas.core.dtypes.common import is_numeric_dtype

from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.hem3.Hem3AllInnerReceptors import Hem3AllInnerReceptors


class Hem3Comparer():

    def __init__(self, hem3Dir, hem4Dir):
        self.hem3Dir = hem3Dir
        self.hem4Dir = hem4Dir


    def compare(self):
        hem4allinner = AllInnerReceptors(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride="FAC1-NC_all_inner_receptors.csv")
        hem4_allinner_df = hem4allinner.createDataframe()

        # Now do the same for hem3 file...
        hem3allinner = Hem3AllInnerReceptors(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
                                     filenameOverride="FAC1-NC_all_inner_receptors.csv")
        hem3_allinner_df = hem3allinner.createDataframe()

        differences = []

        for index, hem4Series in hem4_allinner_df.iterrows():

            # Find the corresponding row in the hem3 dataframe, and get it as a series
            hem3Row = hem3_allinner_df.loc[(hem3_allinner_df[fips] == hem4Series[fips]) &
               (hem3_allinner_df[block] == hem4Series[block]) & (hem3_allinner_df[pollutant] == hem4Series[pollutant]) &
               (hem3_allinner_df[source_id] == hem4Series[source_id])]
            hem3Series = hem3Row.iloc[0]

            for numericCol in hem4allinner.numericColumns:
                if numericCol in hem3allinner.numericColumns:
                    if is_numeric_dtype(hem4_allinner_df[numericCol]):
                        if is_numeric_dtype(hem3_allinner_df[numericCol]):
                            hem4Series[numericCol] = self.round_to_sigfig(100*(hem4Series[numericCol] -
                                                               hem3Series[numericCol]) / hem3Series[numericCol], 5)

            differences.append(hem4Series)

        diff_df = pd.DataFrame(differences)
        allinner_diff = AllInnerReceptors(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
                                          filenameOverride="diff_all_inner_receptors.csv")

        allinner_diff.writeHeader()
        allinner_diff.appendToFile(diff_df)

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded

comparer = Hem3Comparer("C:\HEM-inputs\comparison\HEM3", "C:\HEM-inputs\comparison\HEM4")
comparer.compare()
