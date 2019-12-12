from math import floor, log10

from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.AllOuterReceptors import *
from com.sca.hem4.writer.csv.AllPolarReceptors import AllPolarReceptors, sector, ring
from com.sca.hem4.writer.csv.BlockSummaryChronic import BlockSummaryChronic
from com.sca.hem4.writer.csv.hem3.Hem3AllInnerReceptors import Hem3AllInnerReceptors
from com.sca.hem4.writer.csv.hem3.Hem3AllOuterReceptors import Hem3AllOuterReceptors
from com.sca.hem4.writer.csv.hem3.Hem3AllPolarReceptors import Hem3AllPolarReceptors
from com.sca.hem4.writer.csv.hem3.Hem3BlockSummaryChronic import Hem3BlockSummaryChronic
from com.sca.hem4.writer.excel.MaximumIndividualRisks import MaximumIndividualRisks, value, parameter
from com.sca.hem4.writer.excel.RiskBreakdown import RiskBreakdown, site_type, mir
from com.sca.hem4.writer.excel.hem3.Hem3MaximumIndividualRisks import Hem3MaximumIndividualRisks
from com.sca.hem4.writer.excel.hem3.Hem3RiskBreakdown import Hem3RiskBreakdown

hem3Dirname = r"\\sfudge-pc\HEM3_for_HEM4_compare\hem3_output_unittest\01043110000366247"
hem4Dirname = r"C:\Git_HEM4\HEM4\output\Unit\01043110000366247"

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
        hem3File = "01043110000366247_all_inner_receptors.csv"
        hem4File = "01043110000366247_all_inner_receptors.csv"
        diffFile = "diff_all_inner_receptors.csv"
        joinColumns = [fips, block, source_id, pollutant]
        diffColumns = [conc, aconc]
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
        hem3File = "01043110000366247_all_polar_receptors.csv"
        hem4File = "01043110000366247_all_polar_receptors.csv"
        diffFile = "diff_all_polar_receptors.csv"
        joinColumns = [sector, ring, source_id, pollutant]
        diffColumns = [conc, aconc]
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
        hem3File = "01043110000366247_maximum_indiv_risks.xlsx"
        hem4File = "01043110000366247_maximum_indiv_risks.xlsx"
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

        #---------- Risk breakdown -----------#
        hem3File = "FAC1-NC_risk_breakdown.xlsx"
        hem4File = "FAC1-NC_risk_breakdown.xlsx"
        diffFile = "diff_risk_breakdown.xlsx"
        joinColumns = [site_type, parameter, source_id, pollutant]
        diffColumns = [value]
        #------------------------------------------#
        hem4risks = RiskBreakdown(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
                                           filenameOverride=hem4File)
        hem3risks = Hem3RiskBreakdown(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
                                               filenameOverride=hem3File)
        risks_diff = RiskBreakdown(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
                                            filenameOverride=diffFile)
        risks_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3risks, hem4risks, joinColumns, diffColumns)
        risks_diff.appendToFile(diff_df)

        #---------- Block Summary Chronic -----------#
        hem3File = "FAC1-NC_Block_summary_chronic.csv"
        hem4File = "FAC1-NC_block_summary_chronic.csv"
        diffFile = "diff_block_summary_chronic.csv"
        joinColumns = [fips, block]
        diffColumns = [mir, hi_resp, hi_live, hi_neur, hi_deve,
                       hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
        #------------------------------------------#
        hem4summary = BlockSummaryChronic(targetDir=self.hem4Dir, facilityId=None, model=None, plot_df=None,
                                  filenameOverride=hem4File)
        hem3summary = Hem3BlockSummaryChronic(targetDir=self.hem3Dir, facilityId=None, model=None, plot_df=None,
                                      filenameOverride=hem3File)
        summary_diff = BlockSummaryChronic(targetDir=self.diff_target, facilityId=None, model=None, plot_df=None,
                                   filenameOverride=diffFile)
        summary_diff.writeHeader()
        diff_df = self.calculateNumericDiffs(hem3summary, hem4summary, joinColumns, diffColumns)
        summary_diff.appendToFile(diff_df)


        #---------- All outer receptors -----------#
        hem3File = "01043110000366247_all_outer_receptors.csv"
        hem4File = "01043110000366247_all_outer_receptors.csv"
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

        # Percent Change = ((HEM4- HEM3)/HEM3) * 100

        hem4_df = hem4_entity.createDataframe()
        hem3_df = hem3_entity.createDataframe()

        merged_df = hem4_df.merge(hem3_df, on=joinColumns, suffixes=('', '_y'))
        for numericCol in diffColumns:

            merged_df[numericCol] = merged_df[numericCol].apply(self.scrub_zero)
            merged_df[numericCol+"_y"] = merged_df[numericCol+"_y"].apply(self.scrub_zero)

            hem3Value = merged_df[numericCol+"_y"]
            hem4Value = merged_df[numericCol]

            merged_df[numericCol] = 100*(hem4Value - hem3Value) / hem3Value
            merged_df[numericCol] = merged_df[numericCol].apply(self.round_to_sigfig, args=[3])

        merged_df.drop(list(merged_df.filter(regex='_y$')), axis=1, inplace=True)
        return merged_df

    # Change 0 to "very small" so we can compute a percentage change...
    def scrub_zero(self, x):
        if x == 0:
            return 0.000001
        else:
            return x

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded


comparer = Hem3Comparer(hem3Dirname, hem4Dirname)
comparer.compare()
