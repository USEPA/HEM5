from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.writer.csv.BlockSummaryChronic import *

risktype = 'risktype'
risk = 'risk'
class MaxRiskSummary(ExcelWriter):

    def __init__(self, targetDir, facilityIds):
        self.name = "Maximum Risk Summary"
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds
        self.blocksummary_df = pd.DataFrame()

        self.filename = os.path.join(targetDir, "max_risk.xlsx")

    def getHeader(self):
        return ['Risk Type', 'FIPS', 'Block', 'Population', 'Risk']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId
            print("Looking for receptor files in directory " + targetDir)

            blockSummaryChronic = BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId)
            bsc_df = blockSummaryChronic.createDataframe()
            self.blocksummary_df = self.blocksummary_df.append(bsc_df)

        self.blocksummary_df.drop_duplicates().reset_index(drop=True)
        print("Rows block summary: " + str(len(self.blocksummary_df.index)))

        risks = [
            ['mir', '', '', 0, 0],
            ['respiratory', '', '', 0, 0],
            ['liver', '', '', 0, 0],
            ['neurological', '', '', 0, 0],
            ['developmental', '', '', 0, 0],
            ['reproductive', '', '', 0, 0],
            ['kidney', '', '', 0, 0],
            ['ocular', '', '', 0, 0],
            ['endocrine', '', '', 0, 0],
            ['hematological', '', '', 0, 0],
            ['immunological', '', '', 0, 0],
            ['skeletal', '', '', 0, 0],
            ['spleen', '', '', 0, 0],
            ['thyroid', '', '', 0, 0],
            ['whole body', '', '', 0, 0]
        ]
        maxrisk_df = pd.DataFrame(risks, columns=[risktype, fips, block, population, risk])

        # Put final df into array
        self.dataframe = maxrisk_df
        self.data = self.dataframe.values
        yield self.dataframe