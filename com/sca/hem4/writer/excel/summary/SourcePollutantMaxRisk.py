import datetime
import fnmatch
import os
import re
import pandas as pd

from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DoseResponse import DoseResponse, ure, rfc
from com.sca.hem4.writer.csv.AllInnerReceptors import AllInnerReceptors, block, fips, lat, lon, pollutant, overlap, \
    conc, fac_id, source_id, population
from com.sca.hem4.writer.csv.AllInnerReceptorsNonCensus import AllInnerReceptorsNonCensus
from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors, mir
from com.sca.hem4.writer.csv.AllOuterReceptorsNonCensus import AllOuterReceptorsNonCensus
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.writer.excel.InputSelectionOptions import InputSelectionOptions
from com.sca.hem4.writer.excel.summary.MaxRisk import risk
from com.sca.hem4.writer.excel.summary.AltRecAwareSummary import AltRecAwareSummary

class SourcePollutantMaxRisk(ExcelWriter):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Maximum Risk by Source and Pollutant Summary"
        self.categoryName = parameters[0]

        # Parameters specify which part of the source id contains the code
        self.codePosition = parameters[1][0]
        self.codeLength = parameters[1][1]

        self.riskCache = {}
        self.haplib_df = DoseResponse().dataframe
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds
        self.filename = os.path.join(targetDir, self.categoryName + "_facility_risk_hi_bysrchap.xlsx")

        # Record whether or not alternate receptors used
        altrecfinder = AltRecAwareSummary()
        self.altrec = altrecfinder.determineAltRec(self.categoryFolder)

    def getHeader(self):
        return ['Facility', 'Facility MIR', 'Facility Incidence', 'Facility Max HI', 'Max HI Type', 'Source Type',
                'Pollutant', 'Risk by Source and HAP', 'HQ by Source and HAP', 'Incidence by Source and HAP']

    def getColumns(self):
        return [fac_id, 'fac_mir', 'fac_incidence', 'max_hi', 'hi_type', 'type', pollutant, mir, 'hq', 'incidence']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        print(datetime.datetime.now())

        # The first step is to load the risk breakdown output for each facility so that we
        # can recover the risk for each pollutant.
        filename = self.categoryName + "_facility_max_risk_and_hi.xlsx"
        facilityMaxRiskAndHI = FacilityMaxRiskandHI(targetDir=self.categoryFolder, filenameOverride=filename)
        facilityMaxRiskAndHI_df = facilityMaxRiskAndHI.createDataframe()

        final_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            print("Inspecting facility folder " + facilityId + " for output files...")

            maxRiskAndHI_df = facilityMaxRiskAndHI_df.loc[facilityMaxRiskAndHI_df['Facil_id'] == facilityId]

            try:
                targetDir = self.categoryFolder + "/" + facilityId

                # Determine if this facility was run with acute or not
                inputops = InputSelectionOptions(targetDir=targetDir, facilityId=facilityId)
                inputops_df = inputops.createDataframe()
                acute_yn = inputops_df['acute_yn'].iloc[0]

                # Open the inner file and create df                
                allinner = AllInnerReceptorsNonCensus(targetDir=targetDir, facilityId=facilityId, acuteyn=acute_yn) if self.altrec \
                        else AllInnerReceptors(targetDir=targetDir, facilityId=facilityId, acuteyn=acute_yn)
                allinner_df = allinner.createDataframe()

                # Don't consider schools and monitors (if using census data)
                if not self.altrec:
                    allinner_df = allinner_df.loc[(~allinner_df[block].str.contains('S')) &
                                                  (~allinner_df[block].str.contains('M')) &
                                                  (allinner_df[overlap] == 'N')]

                allinner_df[[mir, 'hq']] = allinner_df.apply(lambda row: self.calculateRisks(row[pollutant], row[conc]), axis=1)
                allinner_df = allinner_df.loc[(allinner_df[mir] + allinner_df['hq'] > 0)]

                # convert source ids to the code part only, and then group and sum
                allinner_df['type'] = allinner_df[source_id]\
                    .apply(lambda x: x[self.codePosition:self.codePosition+self.codeLength])

                # Aggregate risk, grouped by FIPS/block (or receptor id if we're using alternates) and source
                aggs = {mir:'sum', 'hq':'sum'}
                byCols = [lat, lon, population, 'type', pollutant]
                inner_summed = allinner_df.groupby(by=byCols, as_index=False).agg(aggs).reset_index(drop=True)
                inner_summed['incidence'] = inner_summed[mir] * inner_summed[population] / 70

                # Open any/all outer files and create df
                allouter_combined = pd.DataFrame()
                listOuter = []
                listDirfiles = os.listdir(targetDir)
                pattern = "*_all_outer_receptors*.csv"
                for entry in listDirfiles:
                    if fnmatch.fnmatch(entry, pattern):
                        listOuter.append(entry)

                for f in listOuter:
                    allouter = AllOuterReceptorsNonCensus(targetDir=targetDir, acuteyn=acute_yn, filenameOverride=f) if self.altrec \
                            else AllOuterReceptors(targetDir=targetDir, acuteyn=acute_yn, filenameOverride=f)
                    allouter_df = allouter.createDataframe()

                    if not allouter_df.empty:

                        # Don't consider schools and monitors (if using census data)
                        if not self.altrec:
                            allouter_df = allouter_df.loc[(~allouter_df[block].str.contains('S')) &
                                                          (~allouter_df[block].str.contains('M')) &
                                                          (allouter_df[overlap] == 'N')]

                        # Using apply with self.calculateRisks() takes way too long for the outer receptors, so instead
                        # we perform vector operations. Note the use of a reciprocal for the RFC value to avoid
                        # divide-by-zero errors. Also note that we don't need to worry about URE/RFC values not being
                        # in the cache here, because we already processed them all for the inner receptors.
                        allouter_df[ure] = allouter_df[pollutant].apply(lambda x: self.riskCache[x][ure])
                        allouter_df[rfc] = allouter_df[pollutant].apply(lambda x: 1 / self.riskCache[x][rfc] if self.riskCache[x][rfc] != 0 else 0)
                        allouter_df[mir] = allouter_df[conc] * allouter_df[ure]
                        allouter_df['hq'] = (allouter_df[conc] * allouter_df[rfc]) / 1000

                        allouter_df = allouter_df.loc[(allouter_df[mir] + allouter_df['hq'] > 0)]

                        # convert source ids to the code part only, and then group and sum
                        allouter_df['type'] = allouter_df[source_id] \
                            .apply(lambda x: x[self.codePosition:self.codePosition+self.codeLength])

                        # Aggregate risk, grouped by FIPS/block (or receptor id if we're using alternates) and source
                        aggs = {mir:'sum', 'hq':'sum'}
                        byCols = [lat, lon, population, 'type', pollutant]
                        outer_summed = allouter_df.groupby(by=byCols, as_index=False).agg(aggs).reset_index(drop=True)
                        outer_summed['incidence'] = inner_summed[mir] * inner_summed[population] / 70

                        allouter_combined = allouter_combined.append(outer_summed)

            except BaseException as e:
                print("Error gathering output information: " + repr(e))
                print("Skipping facility " + facilityId)
                continue

            all_df = pd.concat([inner_summed, allouter_combined])

            grouped_df = all_df.groupby(by=['type', pollutant], as_index=False) \
                .agg({mir:'max', 'hq':'max', 'incidence':'sum'}).reset_index(drop=True)

            for index, row in grouped_df.iterrows():
                grouped_df[fac_id] = facilityId
                grouped_df['fac_mir'] = maxRiskAndHI_df['mx_can_rsk'].iloc[0]
                grouped_df['fac_incidence'] = maxRiskAndHI_df['incidence'].iloc[0]
                self.find_max_hi_risk_and_type(grouped_df, maxRiskAndHI_df)

            final_df = final_df.append(grouped_df)

        self.dataframe = pd.DataFrame(data=final_df, columns=self.getColumns())
        self.data = self.dataframe.values
        yield self.dataframe

    def calculateRisks(self, pollutant_name, conc):

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant_name) + '$'

        # Since it's relatively expensive to get these values from their respective libraries, cache them locally.
        # Note that they are cached as a pair (i.e. if one is in there, the other one will be too...)
        if pollutant_name in self.riskCache:
            URE = self.riskCache[pollutant_name][ure]
            RFC = self.riskCache[pollutant_name][rfc]
        else:
            row = self.haplib_df.loc[
                self.haplib_df[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                URE = 0
                RFC = 0
            else:
                URE = row.iloc[0][ure]
                RFC = row.iloc[0][rfc]

            self.riskCache[pollutant_name] = {ure : URE, rfc : RFC}

        risks = []
        MIR = conc * URE
        risks.append(MIR)

        hazard_index = (0 if RFC == 0 else (conc/1000/RFC))
        risks.append(hazard_index)
        return pd.Series(risks)

    def find_max_hi_risk_and_type(self, record_df, df):
        # column name with max duration value
        max_col_name = df.filter(regex='_hi$', axis=1).max().idxmax()
        type_name = max_col_name[:-3] # strip the "_hi" from the name...

        # index of max_col_name
        max_col_idx = df.columns.get_loc(max_col_name)

        # output with .loc
        max_value = df.iloc[0, max_col_idx]

        record_df['max_hi'] = max_value
        record_df['hi_type'] = type_name