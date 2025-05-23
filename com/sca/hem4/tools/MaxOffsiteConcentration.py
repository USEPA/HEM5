import fnmatch
from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors
from com.sca.hem4.writer.csv.AllPolarReceptors import AllPolarReceptors
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.writer.excel.InputSelectionOptions import InputSelectionOptions
from com.sca.hem4.log.Logger import Logger


class MaxOffsiteConcentration(ExcelWriter):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Maximum Offsite Concentration Summary"
        self.categoryName = parameters[0]
        self.hap = parameters[1]
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds
        self.filename = os.path.join(targetDir, "max_offsite_conc.xlsx")

    def getHeader(self):
        return ['Facility ID', 'Pollutant', 'Max Conc', 'Lat', 'Lon', 'Receptor Type', 'Fips', 'Block']

    def getColumns(self):
        return [fac_id, pollutant, conc, lat, lon, rec_type, fips, block]

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        all_df = pd.DataFrame()

        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            # Determine if this facility was run with acute or not
            inputops = InputSelectionOptions(targetDir=targetDir, facilityId=facilityId)
            inputops_df = inputops.createDataframe()
            acute_yn = inputops_df['acute_yn'].iloc[0]

            # Polar recs
            allpolar = AllPolarReceptors(targetDir=targetDir, facilityId=facilityId, acuteyn=acute_yn)
            allpolar_df = allpolar.createDataframe()

            allpolar_df = allpolar_df.loc[~(allpolar_df[overlap] == 'Y')]

            allpolar_df = allpolar_df.loc[allpolar_df[pollutant].str.contains(self.hap, regex=True)]

            if len(allpolar_df) > 0:
                allpolar_df = allpolar_df.groupby(by=[lat, lon, pollutant], as_index=False) \
                    .sum().reset_index(drop=True)
                allpolar_df[fips] = ''
                allpolar_df[block] = ''
                allpolar_df[rec_type] = 'P'
                allpolar_df[fac_id] = facilityId

                all_df = pd.concat([all_df, allpolar_df])

            # Inner recs
            allinner = AllInnerReceptors(targetDir=targetDir, facilityId=facilityId, acuteyn=acute_yn)
            allinner_df = allinner.createDataframe()

            allinner_df = allinner_df.loc[~((allinner_df[block].str.contains('S')) |
                                           (allinner_df[block].str.contains('M')) |
                                           (allinner_df[overlap] == 'Y'))]

            allinner_df = allinner_df.loc[allinner_df[pollutant].str.contains(self.hap, regex=True)]

            if len(allinner_df) > 0:
                allinner_df = allinner_df.groupby(by=[fips, block, lat, lon, pollutant], as_index=False) \
                    .sum().reset_index(drop=True)

                allinner_df[rec_type] = allinner_df.apply(lambda row: MaxOffsiteConcentration.add_rec_type(row), axis=1)
                allinner_df[fac_id] = facilityId
                all_df = pd.concat([all_df, allinner_df])

            # Outer recs
            listOuter = []
            listDirfiles = os.listdir(targetDir)
            pattern = "*_all_outer_receptors*.csv"
            for entry in listDirfiles:
                if fnmatch.fnmatch(entry, pattern):
                    listOuter.append(entry)

            for f in listOuter:
                allouter = AllOuterReceptors(targetDir=targetDir, acuteyn=acute_yn, filenameOverride=f)
                allouter_df = allouter.createDataframe()

                if not allouter_df.empty:

                    allouter_df = allouter_df.loc[~((allouter_df[block].str.contains('S')) |
                                                    (allouter_df[block].str.contains('M')) |
                                                    (allouter_df[overlap] == 'Y'))]
                    allouter_df = allouter_df.loc[allouter_df[pollutant].str.contains(self.hap, regex=True)]

                    if len(allouter_df) > 0:
                        allouter_df = allouter_df.groupby(by=[fips, block, lat, lon, pollutant], as_index=False) \
                            .sum().reset_index(drop=True)

                        allouter_df[fac_id] = facilityId
                        allouter_df[rec_type] = allouter_df.apply(lambda row: MaxOffsiteConcentration.add_rec_type(row), axis=1)

                        all_df = pd.concat([all_df, allouter_df])

        # Group by pollutant and then find the max
        max_conc_df = all_df.groupby(by=[fac_id, pollutant], as_index=False).max().reset_index(drop=True)

        # Put final df into array
        self.dataframe = pd.DataFrame(data=max_conc_df, columns=self.getColumns())
        self.data = self.dataframe.values
        yield self.dataframe

    def add_rec_type(row):
        return 'U' if 'U' in row[block] else 'C'

