from math import log10, floor
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.FacilityPrep import *

risklevel = 'risklevel'
resp_population = 'resp_population'
resp_facilitycount = 'resp_facilitycount'
neuro_population = 'neuro_population'
neuro_facilitycount = 'neuro_facilitycount'
repr_population = 'repr_population'
repr_facilitycount = 'repr_facilitycount'

class HI_Histogram(ExcelWriter):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Non-cancer Histogram"
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds

        self.filename = os.path.join(targetDir, "hi_histogram_risk.xlsx")

    def getHeader(self):
        return ['HI Level',	 'Respiratory Pop',	'Respiratory Facilities',
                'Neurological Pop',	'Neurological Facilities',
                'Reproductive Pop',	'Reproductive Facilities']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        self.facilityMap = {}

        # Data structure to keep track of the needed histogram values.
        # There are 5 sub lists corresponding to the five buckets.
        counts = [[0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0]]

        blocksummary_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            blockSummaryChronic = BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId)
            bsc_df = blockSummaryChronic.createDataframe()

            # Get max resp value that has a population > 0
            respMax = bsc_df.loc[bsc_df[(bsc_df[population] > 0)][hi_resp].idxmax()]
            rounded = self.round_to_sigfig(respMax[hi_resp])
            if rounded > 1000:
                counts[0][1] = counts[0][1] + 1
            if rounded > 100:
                counts[1][1] = counts[1][1] + 1
            if rounded > 10:
                counts[2][1] = counts[2][1] + 1
            if rounded > 1:
                counts[3][1] = counts[3][1] + 1
            if rounded <= 1:
                counts[4][1] = counts[4][1] + 1

            neuroMax = bsc_df.loc[bsc_df[(bsc_df[population] > 0)][hi_neur].idxmax()]
            rounded = self.round_to_sigfig(neuroMax[hi_neur])
            if rounded > 1000:
                counts[0][3] = counts[0][3] + 1
            if rounded > 100:
                counts[1][3] = counts[1][3] + 1
            if rounded > 10:
                counts[2][3] = counts[2][3] + 1
            if rounded > 1:
                counts[3][3] = counts[3][3] + 1
            if rounded <= 1:
                counts[4][3] = counts[4][3] + 1

            reproMax = bsc_df.loc[bsc_df[(bsc_df[population] > 0)][hi_repr].idxmax()]
            rounded = self.round_to_sigfig(reproMax[hi_repr])
            if rounded > 1000:
                counts[0][5] = counts[0][5] + 1
            if rounded > 100:
                counts[1][5] = counts[1][5] + 1
            if rounded > 10:
                counts[2][5] = counts[2][5] + 1
            if rounded > 1:
                counts[3][5] = counts[3][5] + 1
            if rounded <= 1:
                counts[4][5] = counts[4][5] + 1

            blocksummary_df = blocksummary_df.append(bsc_df)

        blocksummary_df.drop_duplicates().reset_index(drop=True)

        aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', rec_type:'first',
                utmn:'first', hill:'first', fips:'first', block:'first', population:'first',
                mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

        # Aggregate concentration, grouped by FIPS/block
        risk_summed = blocksummary_df.groupby([fips, block]).agg(aggs)[blockSummaryChronic.getColumns()]

        for index, row in risk_summed.iterrows():
            roundedResp = self.round_to_sigfig(row[hi_resp])
            roundedNeuro = self.round_to_sigfig(row[hi_neur])
            roundedRepr = self.round_to_sigfig(row[hi_repr])

            if roundedResp > 1000:
                counts[0][0] = counts[0][0] + row[population]
            if roundedResp > 100:
                counts[1][0] = counts[1][0] + row[population]
            if roundedResp > 10:
                counts[2][0] = counts[2][0] + row[population]
            if roundedResp > 1:
                counts[3][0] = counts[3][0] + row[population]
            if roundedResp <= 1:
                counts[4][0] = counts[4][0] + row[population]

            if roundedNeuro > 1000:
                counts[0][2] = counts[0][2] + row[population]
            if roundedNeuro > 100:
                counts[1][2] = counts[1][2] + row[population]
            if roundedNeuro > 10:
                counts[2][2] = counts[2][2] + row[population]
            if roundedNeuro > 1:
                counts[3][2] = counts[3][2] + row[population]
            if roundedNeuro <= 1:
                counts[4][2] = counts[4][2] + row[population]

            if roundedRepr > 1000:
                counts[0][4] = counts[0][4] + row[population]
            if roundedRepr > 100:
                counts[1][4] = counts[1][4] + row[population]
            if roundedRepr > 10:
                counts[2][4] = counts[2][4] + row[population]
            if roundedRepr > 1:
                counts[3][4] = counts[3][4] + row[population]
            if roundedRepr <= 1:
                counts[4][4] = counts[4][4] + row[population]

        risks = [
            ['> 1000', counts[0][0], counts[0][1], counts[0][2], counts[0][3], counts[0][4], counts[0][5]],
            ['> 100', counts[1][0], counts[1][1], counts[1][2], counts[1][3], counts[1][4], counts[1][5]],
            ['> 10', counts[2][0], counts[2][1], counts[2][2], counts[2][3], counts[2][4], counts[2][5]],
            ['> 1', counts[3][0], counts[3][1], counts[3][2], counts[3][3], counts[3][4], counts[3][5]],
            ['<= 1', counts[4][0], counts[4][1], counts[4][2], counts[4][3], counts[4][4], counts[4][5]]
        ]
        histogram_df = pd.DataFrame(risks, columns=[risklevel, resp_population, resp_facilitycount, neuro_population,
            neuro_facilitycount, repr_population, repr_facilitycount]).astype(dtype=int, errors='ignore')

        # Put final df into array
        self.dataframe = histogram_df
        self.data = self.dataframe.values
        yield self.dataframe

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded