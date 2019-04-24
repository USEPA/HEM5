from com.sca.hem4.log import Logger
from com.sca.hem4.writer.csv.AllInnerReceptors import AllInnerReceptors, pd
from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors


class MaxRiskSummary():

    def __init__(self):
        self.name = "Maximum Risk Summary"
        self.inner_df = pd.DataFrame()
        self.outer_df = pd.DataFrame()

    def create(self, categoryFolder, facilityIds):
        Logger.log("Creating " + self.name + " report...", None, False)

        for facilityId in facilityIds:
            targetDir = "output/" + categoryFolder + "/" + facilityId
            print("Looking for receptor files in directory " + targetDir)

            innerReceptors = AllInnerReceptors(targetDir=targetDir, facilityId=facilityId)
            inner_df = innerReceptors.createDataframe()
            self.inner_df = self.inner_df.append(inner_df)

            # Next, load all outer receptor files
            outerReceptors = AllOuterReceptors(targetDir=targetDir, facilityId=facilityId)
            outer_df = outerReceptors.createDataframe()
            self.outer_df = self.outer_df.append(outer_df)

        self.inner_df.drop_duplicates().reset_index(drop=True)
        self.outer_df.drop_duplicates().reset_index(drop=True)

        print("Rows outer: " + str(len(self.outer_df.index)))

        #Logger.log("inner receptors:", self.inner_df, False)
        #Logger.log("outer receptors:", self.outer_df, False)