from math import floor, log10

from pandas.core.dtypes.common import is_numeric_dtype

from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors
from com.sca.hem4.writer.csv.AllPolarReceptors import AllPolarReceptors, sector, ring
from com.sca.hem4.writer.csv.hem3.Hem3AllInnerReceptors import Hem3AllInnerReceptors
from com.sca.hem4.writer.csv.hem3.Hem3AllOuterReceptors import Hem3AllOuterReceptors
from com.sca.hem4.writer.csv.hem3.Hem3AllPolarReceptors import Hem3AllPolarReceptors
from com.sca.hem4.writer.excel.MaximumIndividualRisks import MaximumIndividualRisks, value, parameter
from com.sca.hem4.writer.excel.hem3.Hem3MaximumIndividualRisks import Hem3MaximumIndividualRisks


class Hem3Comparer():

    def __init__(self, hem3Dir, hem4Dir):
        self.hem3Dir = hem3Dir
        self.hem4Dir = hem4Dir
        self.diff_target = self.hem4Dir + "\diff"

        if not (os.path.exists(self.diff_target) or os.path.isdir(self.diff_target)):
            print("Creating diff directory for results...")
            os.mkdir(self.diff_target)

    def compare(self):
        
        #---------- All inner receptors -----------#
        hem3File = "FAC1-NC_all_inner_receptors.csv"
        hem4File = "FAC1-NC_all_inner_receptors.csv"
        diffFile = "diff_all_inner_receptors.csv"
        joinColumns = [fips, block, source_id, pollutant]
        diffColumns = [conc]
        #------------------------------------------#
        hem4allinner = AllInnerReceptors(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem4File)
        hem3allinner = Hem3AllInnerReceptors(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem3File)
        allinner_diff = AllInnerReceptors(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
            filenameOverride=diffFile)
        allinner_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3allinner, hem4allinner, joinColumns, diffColumns)
        allinner_diff.appendToFile(diff_df)

        #---------- All polar receptors -----------#
        hem3File = "FAC1-NC_all_polar_receptors.csv"
        hem4File = "FAC1-NC_all_polar_receptors.csv"
        diffFile = "diff_all_polar_receptors.csv"
        joinColumns = [sector, ring, source_id, pollutant]
        diffColumns = [conc]
        #------------------------------------------#
        hem4allpolar = AllPolarReceptors(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem4File)
        hem3allpolar = Hem3AllPolarReceptors(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem3File)
        allpolar_diff = AllPolarReceptors(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
            filenameOverride=diffFile)
        allpolar_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3allpolar, hem4allpolar, joinColumns, diffColumns)
        allpolar_diff.appendToFile(diff_df)

        #---------- Maximum individual risks -----------#
        hem3File = "FAC1-NC_maximum_indiv_risks.xlsx"
        hem4File = "FAC1-NC_maximum_indiv_risks.xlsx"
        diffFile = "diff_maximum_indiv_risks.xlsx"
        joinColumns = [parameter]
        diffColumns = [value]
        #------------------------------------------#
        hem4risks = MaximumIndividualRisks(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
                                           filenameOverride=hem4File)
        hem3risks = Hem3MaximumIndividualRisks(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
                                               filenameOverride=hem3File)
        risks_diff = MaximumIndividualRisks(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
                                            filenameOverride=diffFile)
        risks_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3risks, hem4risks, joinColumns, diffColumns)
        risks_diff.appendToFile(diff_df)
        
        #---------- All outer receptors -----------#
        hem3File = "FAC1-NC_all_outer_receptors.csv"
        hem4File = "FAC1-NC_all_outer_receptors.csv"
        diffFile = "diff_all_outer_receptors.csv"
        joinColumns = [fips, block, source_id, pollutant]
        diffColumns = [conc]
        #------------------------------------------#
        hem4allouter = AllOuterReceptors(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem4File)
        hem3allouter = Hem3AllOuterReceptors(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
             filenameOverride=hem3File)
        allouter_diff = AllOuterReceptors(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
            filenameOverride=diffFile)
        allouter_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3allouter, hem4allouter, joinColumns, diffColumns)
        allouter_diff.appendToFile(diff_df)

    # Note: for this method to work correctly, none of the columns in diffColumns can be
    # present in joinColumns
    def calculateNumericDiffs(self, hem3_entity, hem4_entity, joinColumns, diffColumns):
        differences = []

        hem4_df = hem4_entity.createDataframe()
        hem3_df = hem3_entity.createDataframe()

        merged_df = hem4_df.merge(hem3_df, on=joinColumns, suffixes=('', '_y'))
        for numericCol in diffColumns:
            merged_df[numericCol] = 100*(merged_df[numericCol] -
                      merged_df[numericCol+"_y"]) / merged_df[numericCol+"_y"]
            merged_df[numericCol] = merged_df[numericCol].apply(self.round_to_sigfig, args=[3])

        merged_df.drop(list(merged_df.filter(regex='_y$')), axis=1, inplace=True)
        return merged_df

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded

comparer = Hem3Comparer("C:\HEM-inputs\comparison\HEM3", "C:\HEM-inputs\comparison\HEM4")
comparer.compare()
