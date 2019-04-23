from com.sca.hem4.log import Logger
from com.sca.hem4.writer.csv.AllInnerReceptors import AllInnerReceptors


class MaxRiskSummary():

    def __init__(self):
        self.name = "Maximum Risk Summary"
        self.inner_df = None
        self.outer_df = None

    def create(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        innerReceptors = AllInnerReceptors(targetDir="output/HCL2/01129110000605051/", facilityId="01129110000605051")
        self.inner_df = innerReceptors.createDataframe()