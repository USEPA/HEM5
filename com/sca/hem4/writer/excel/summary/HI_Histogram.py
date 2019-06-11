import os
import pandas as pd

from com.sca.hem4.log import Logger
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter


class HI_Histogram(ExcelWriter):

    def __init__(self, targetDir, facilityIds):
        self.name = "Non-cancer Histogram"
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds

        self.filename = os.path.join(targetDir, "histogram_risk.xlsx")

    def getHeader(self):
        return ['Risk level', 'Population', 'Facility count']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        blocksummary_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            blockSummaryChronic = BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId)
            bsc_df = blockSummaryChronic.createDataframe()
            blocksummary_df = blocksummary_df.append(bsc_df)

        blocksummary_df.drop_duplicates().reset_index(drop=True)

        # Drop records that (are not user receptors AND have population = 0)
        blocksummary_df.drop(blocksummary_df[(blocksummary_df.population == 0) & ("U" not in blocksummary_df.block)].index,
                             inplace=True)

        aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', rec_type:'first',
                utmn:'first', hill:'first', fips:'first', block:'first', population:'first',
                mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

        # Aggregate concentration, grouped by FIPS/block
        risk_summed = blocksummary_df.groupby([fips, block]).agg(aggs)[blockSummaryChronic.getColumns()]

        mir_row = risk_summed.loc[risk_summed[mir].idxmax()]
        hi_resp_row = risk_summed.loc[risk_summed[hi_resp].idxmax()]
        hi_live_row = risk_summed.loc[risk_summed[hi_live].idxmax()]
        hi_neur_row = risk_summed.loc[risk_summed[hi_neur].idxmax()]
        hi_deve_row = risk_summed.loc[risk_summed[hi_deve].idxmax()]
        hi_repr_row = risk_summed.loc[risk_summed[hi_repr].idxmax()]
        hi_kidn_row = risk_summed.loc[risk_summed[hi_kidn].idxmax()]
        hi_ocul_row = risk_summed.loc[risk_summed[hi_ocul].idxmax()]
        hi_endo_row = risk_summed.loc[risk_summed[hi_endo].idxmax()]
        hi_hema_row = risk_summed.loc[risk_summed[hi_hema].idxmax()]
        hi_immu_row = risk_summed.loc[risk_summed[hi_immu].idxmax()]
        hi_skel_row = risk_summed.loc[risk_summed[hi_skel].idxmax()]
        hi_sple_row = risk_summed.loc[risk_summed[hi_sple].idxmax()]
        hi_thyr_row = risk_summed.loc[risk_summed[hi_thyr].idxmax()]
        hi_whol_row = risk_summed.loc[risk_summed[hi_whol].idxmax()]

        risks = [
            ['mir', mir_row[4], mir_row[5], mir_row[9], mir_row[10]] if mir_row[10] > 0
            else ['mir', '', '', 0, 0],
            ['respiratory', hi_resp_row[4], hi_resp_row[5], hi_resp_row[9], hi_resp_row[11]] if hi_resp_row[11] > 0
            else ['respiratory', '', '', 0, 0],
            ['liver', hi_live_row[4], hi_live_row[5], hi_live_row[9], hi_live_row[12]] if hi_live_row[12] > 0
            else ['liver', '', '', 0, 0],
            ['neurological', hi_neur_row[4], hi_neur_row[5], hi_neur_row[9], hi_neur_row[13]] if hi_neur_row[13] > 0
            else ['neurological', '', '', 0, 0],
            ['developmental', hi_deve_row[4], hi_deve_row[5], hi_deve_row[9], hi_deve_row[14]] if hi_deve_row[14] > 0
            else ['developmental', '', '', 0, 0],
            ['reproductive', hi_repr_row[4], hi_repr_row[5], hi_repr_row[9], hi_repr_row[15]] if hi_repr_row[15] > 0
            else ['reproductive', '', '', 0, 0],
            ['kidney', hi_kidn_row[4], hi_kidn_row[5], hi_kidn_row[9], hi_kidn_row[16]] if hi_kidn_row[16] > 0
            else ['kidney', '', '', 0, 0],
            ['ocular', hi_ocul_row[4], hi_ocul_row[5], hi_ocul_row[9], hi_ocul_row[17]] if hi_ocul_row[17] > 0
            else ['ocular', '', '', 0, 0],
            ['endocrine', hi_endo_row[4], hi_endo_row[5], hi_endo_row[9], hi_endo_row[18]] if hi_endo_row[18] > 0
            else ['endocrine', '', '', 0, 0],
            ['hematological', hi_hema_row[4], hi_hema_row[5], hi_hema_row[9], hi_hema_row[19]] if hi_hema_row[19] > 0
            else ['hematological', '', '', 0, 0],
            ['immunological', hi_immu_row[4], hi_immu_row[5], hi_immu_row[9], hi_immu_row[20]] if hi_immu_row[20] > 0
            else ['immunological', '', '', 0, 0],
            ['skeletal', hi_skel_row[4], hi_skel_row[5], hi_skel_row[9], hi_skel_row[21]] if hi_skel_row[21] > 0
            else ['skeletal', '', '', 0, 0],
            ['spleen', hi_sple_row[4], hi_sple_row[5], hi_sple_row[9], hi_sple_row[22]] if hi_sple_row[22] > 0
            else ['spleen', '', '', 0, 0],
            ['thyroid', hi_thyr_row[4], hi_thyr_row[5], hi_thyr_row[9], hi_thyr_row[23]] if hi_thyr_row[23] > 0
            else ['thyroid', '', '', 0, 0],
            ['whole body', hi_whol_row[4], hi_whol_row[5], hi_whol_row[9], hi_whol_row[24]] if hi_whol_row[24] > 0
            else ['whole body', '', '', 0, 0],
        ]
        maxrisk_df = pd.DataFrame(risks, columns=[risktype, fips, block, population, risk])

        # Put final df into array
        self.dataframe = maxrisk_df
        self.data = self.dataframe.values
        yield self.dataframe