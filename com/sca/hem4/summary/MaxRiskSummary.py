from com.sca.hem4.log import Logger
from com.sca.hem4.writer.csv.AllInnerReceptors import AllInnerReceptors
from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors


class MaxRiskSummary():

    def __init__(self):
        self.name = "Maximum Risk Summary"
        self.inner_df = None
        self.outer_df = None

    def create(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        innerReceptors = AllInnerReceptors(targetDir="output/HCL2/01129110000605051/", facilityId="01129110000605051")
        self.inner_df = innerReceptors.createDataframe()

        #Logger.log("inner receptors:", self.inner_df, False)

        # Next, load all outer receptor files
        outerReceptors = AllOuterReceptors(targetDir="output/HCL2/01129110000605051/", facilityId="01129110000605051")
        self.outer_df = outerReceptors.createDataframe()

        #Logger.log("outer receptors:", self.outer_df, False)