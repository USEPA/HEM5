from com.sca.hem4.writer.excel.AcuteChemicalMax import AcuteChemicalMax
from com.sca.hem4.writer.excel.AcuteChemicalMaxNonCensus import AcuteChemicalMaxNonCensus
from com.sca.hem4.writer.excel.RiskBreakdown import *
from com.sca.hem4.writer.excel.summary.AltRecAwareSummary import AltRecAwareSummary
import os

from com.sca.hem4.upload.DoseResponse import DoseResponse

hq_rel = 'hq_rel'
hq_aegl1 = 'hq_aegl1'
hq_erpg1 = 'hq_erpg1'
hq_aegl2 = 'hq_aegl2'
hq_erpg2 = 'hq_erpg2'

class AcuteImpacts(ExcelWriter, InputFile, AltRecAwareSummary):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Acute Impacts Summary"
        self.categoryName = parameters[0]
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds

        path = os.path.join(targetDir, self.categoryName + "_acute_impacts.xlsx")

        firstFacility = facilityIds[0]

        InputFile.__init__(self, path, False)

        self.filename = path
        self.targetDir = targetDir
        self.altrec = self.determineAltRec(self.categoryFolder)

    def getHeader(self):
        # Get acute benchmark names from Dose Response file. Remove any newlines
        # and characters after the newline.
        bench_names = []
        for item in DoseResponse.getAcuteNames():
            # Split the string at the first occurrence of a newline character
            # and take the first part
            bench_item = item.split('\n')[0]
            bench_names.append(bench_item)

        if self.altrec == 'Y':
            header_list = ['Facility ID', 'Pollutant', 'CONC_MG/M3', bench_names[4]
                           , bench_names[0], bench_names[2], bench_names[1], bench_names[3]
                           , 'HQ_'+bench_names[4], 'HQ_'+bench_names[0], 'HQ_'+bench_names[2]
                           , 'HQ_'+bench_names[1], 'HQ_'+bench_names[3]
                           , 'Receptor ID', 'Distance', 'Angle']
            
            return header_list
        else:
            header_list = ['Facility ID', 'Pollutant', 'CONC_MG/M3', bench_names[4]
                           , bench_names[0], bench_names[2], bench_names[1], bench_names[3]
                           , 'HQ_'+bench_names[4], 'HQ_'+bench_names[0], 'HQ_'+bench_names[2]
                           , 'HQ_'+bench_names[1], 'HQ_'+bench_names[3]
                           , 'FIPS', 'Block', 'Distance', 'Angle']
            
            return header_list


    def getColumns(self):
        if self.altrec == 'Y':
            return[fac_id, pollutant, aconc, rel, aegl_1_1h, erpg_1, aegl_2_1h, erpg_2,
               hq_rel, hq_aegl1, hq_erpg1, hq_aegl2, hq_erpg2, rec_id, distance, angle]
        else:
            return [fac_id, pollutant, aconc, rel, aegl_1_1h, erpg_1, aegl_2_1h, erpg_2,
               hq_rel, hq_aegl1, hq_erpg1, hq_aegl2, hq_erpg2, fips, block, distance, angle]

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        anyAcute = "N"
        
        # Load the acute chemical max output for each facility
        allAcute_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId


            acute = AcuteChemicalMaxNonCensus(targetDir=targetDir, facilityId=facilityId) if self.altrec == 'Y' else \
                AcuteChemicalMax(targetDir=targetDir, facilityId=facilityId)

            # Does this facility have acute results?
            if os.path.isfile(acute.filename):

                acute_df = acute.createDataframe()

                acute_df[fac_id] = facilityId

                allAcute_df = pd.concat([allAcute_df, acute_df])
                if not allAcute_df.empty:
                    anyAcute = "Y"
                    
            else:
                Logger.logMessage("Skipped facility " + facilityId + ". Couldn't find acute information.")

        if anyAcute == "Y":
            
            # Unit conversion for acute concentration
            allAcute_df[aconc] = allAcute_df.apply(lambda x: (x[aconc] / 1000), axis=1)
    
            # The hazard quotients are calculated by dividing the acute concentration by the benchmark value
            allAcute_df[hq_rel] = allAcute_df.apply(lambda x: (x[aconc] / x[rel]) if x[rel] > 0 else 0, axis=1)
            allAcute_df[hq_aegl1] = allAcute_df.apply(lambda x: (x[aconc] / x[aegl_1_1h]) if x[aegl_1_1h] > 0 else 0, axis=1)
            allAcute_df[hq_erpg1] = allAcute_df.apply(lambda x: (x[aconc] / x[erpg_1]) if x[erpg_1] > 0 else 0, axis=1)
            allAcute_df[hq_aegl2] = allAcute_df.apply(lambda x: (x[aconc] / x[aegl_2_1h]) if x[aegl_2_1h] > 0 else 0, axis=1)
            allAcute_df[hq_erpg2] = allAcute_df.apply(lambda x: (x[aconc] / x[erpg_2]) if x[erpg_2] > 0 else 0, axis=1)
    
            if self.altrec == 'Y':
                allAcute_df = allAcute_df[[fac_id, pollutant, aconc, rel, aegl_1_1h, erpg_1, aegl_2_1h, erpg_2,
                       hq_rel, hq_aegl1, hq_erpg1, hq_aegl2, hq_erpg2, rec_id, distance, angle]]
            else:
                allAcute_df = allAcute_df[[fac_id, pollutant, aconc, rel, aegl_1_1h, erpg_1, aegl_2_1h, erpg_2,
                       hq_rel, hq_aegl1, hq_erpg1, hq_aegl2, hq_erpg2, fips, block, distance, angle]]
    
            allAcute_df.sort_values(by=[fac_id, pollutant], ascending=True, inplace=True)
            allAcute_df.reset_index(inplace=True, drop=True)
    
            # Put final df into array
            self.dataframe = allAcute_df
            self.data = self.dataframe.values
            yield self.dataframe
            
        else:
            
            Logger.logMessage("There was no acute data to generate the Acute Impacts summary.")

    def createDataframe(self):
        # Type setting for XLS reading
        self.numericColumns = [aconc, rel, aegl_1_1h, erpg_1, aegl_2_1h, erpg_2,
                               hq_rel, hq_aegl1, hq_erpg1, hq_aegl2, hq_erpg2, distance, angle]

        if self.altrec == 'Y':
            self.strColumns = [fac_id, pollutant, rec_id]
        else:
            self.strColumns = [fac_id, pollutant, fips, block]

        self.skiprows = 0
        df = self.readFromPath(self.getColumns())
        return df.fillna("")