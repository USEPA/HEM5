from com.sca.hem4.upload.PollutantCrosswalk import PollutantCrosswalk, pollutant_name
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.writer.excel.RiskBreakdown import *

risk_contrib = 'risk_contrib'

class MultiPathway(ExcelWriter):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Cancer Drivers Summary"
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds

        self.filename = os.path.join(targetDir, "cancer_drivers.xlsx")

    def getHeader(self):
        return ['Facility ID', 'MIR', 'Pollutant', 'Cancer Risk', 'Risk Contribution', 'Source ID']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        # The first step is to load the risk breakdown output for each facility so that we
        # can recover the risk for each pollutant.
        allrisk_df = pd.DataFrame()
        facilityMaxRiskAndHI = FacilityMaxRiskandHI(targetDir=self.categoryFolder)
        facilityMaxRiskAndHI_df = facilityMaxRiskAndHI.createDataframe()

        pollutantCrosswalk = PollutantCrosswalk(targetDir=self.categoryFolder)
        pollutantCrosswalk_df = pollutantCrosswalk.createDataframe()

        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            maxIndivRisks = MaximumIndividualRisks(targetDir=targetDir, facilityId=facilityId)
            maxIndivRisks_df = maxIndivRisks.createDataframe()

            riskBkdn = RiskBreakdown(targetDir=targetDir, facilityId=facilityId)
            riskBkdn_df = maxIndivRisks.createDataframe()
            riskBkdn_df = riskBkdn_df.loc[(riskBkdn_df[site_type] == 'Max indiv risk') &
                                    (riskBkdn_df[parameter] == 'Cancer risk') &
                                    (riskBkdn_df[source_id].str.contains('Total')) &
                                    (~riskBkdn_df[pollutant].str.contains('All '))]

            # Filter out records whose pollutant is not in crosswalk
            rbkdn_df = riskBkdn_df.merge(pollutantCrosswalk_df, left_on=[pollutant], right_on=[pollutant_name])


        allrisk_df.drop_duplicates().reset_index(drop=True)

        # Put final df into array
        self.dataframe = allrisk_df
        self.data = self.dataframe.values
        yield self.dataframe

    def rollup(self, facid, df):
        df.loc[df.fac_id == facid, pollutant] = 'None'
        df.loc[df.fac_id == facid, source_id] = 'None'
        df.loc[df.fac_id == facid, value] = 0
        df.loc[df.fac_id == facid, risk_contrib] = 0