from math import log10, floor

from com.sca.hem4.upload.EmissionsLocations import EmissionsLocations
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter

risklevel = 'risklevel'
resp_population = 'resp_population'
resp_facilitycount = 'resp_facilitycount'
neuro_population = 'neuro_population'
neuro_facilitycount = 'neuro_facilitycount'
repr_population = 'repr_population'
repr_facilitycount = 'repr_facilitycount'

class SourceTypeRiskHistogram(ExcelWriter):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Source Type Risk Histogram"
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds
        self.codePosition = parameters[0]
        self.codeLength = parameters[1]

        self.haplib_df = DoseResponse().dataframe
        self.filename = os.path.join(targetDir, "source_type_risk.xlsx")

        self.riskCache = {}

    def getHeader(self):
        header = ['', 'Maximum Overall']

        # Open the emisloc dataframe and find all unique source type codes
        emislocFile = os.path.join(self.categoryFolder, "inputs/emisloc.xlsx")
        emisloc = EmissionsLocations(emislocFile)

        sourceIds = emisloc.dataframe[source_id].unique()
        sourceTypes = [id[self.codePosition:self.codePosition+self.codeLength] for id in sourceIds]
        sourceTypes = list(set(sourceTypes))
        header.extend(sourceTypes)
        self.header = header
        return self.header

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)

        # Create a list that's the same length as the headers
        maximum = list(map(lambda x: 0, self.header))
        maximum[0] = 'Maximum (in 1 million)'
        hundo = list(map(lambda x: 100, self.header))
        hundo[0] = '>= 100 in 1 million'
        ten = list(map(lambda x: 10, self.header))
        ten[0] = '>= 10 in 1 million'
        one = list(map(lambda x: 1, self.header))
        one[0] = '>= 1 in 1 million'
        incidences = list(map(lambda x: 45, self.header))
        incidences[0] = 'Incidence'

        blocksummary_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            allinner = AllInnerReceptors(targetDir=targetDir, facilityId=facilityId)
            allinner_df = allinner.createDataframe()

            allinner_df['risk'] = allinner_df.apply(lambda x: self.calculateRisk(x[pollutant], x[conc]), axis=1)

            # convert source ids to the code part only, and then group and sum
            allinner_df[source_id] = allinner_df[source_id].apply(lambda x: x[self.codePosition:self.codePosition+self.codeLength])

            aggs = {fips:'first', block:'first', lat:'first', lon:'first', source_id:'first', ems_type:'first',
                    pollutant:'first', conc:'first', aconc:'first', elev:'first', drydep:'first', wetdep:'first',
                    population:'first', overlap:'first', 'risk':'sum'}

            # Aggregate concentration, grouped by FIPS/block
            inner_summed = allinner_df.groupby([fips, block, source_id]).agg(aggs)[
                [fips, block, lat, lon, source_id, ems_type, pollutant, conc, aconc, elev, drydep, wetdep, population,
                 overlap, 'risk']]

            print("hey")

            # Get a list of the all_outer_receptor files (could be more than one)
            # listOuter = []
            # listDirfiles = os.listdir(self.targetDir)
            # pattern = "*_all_outer_receptors*.csv"
            # for entry in listDirfiles:
            #     if fnmatch.fnmatch(entry, pattern):
            #         listOuter.append(entry)
            #
            # # Search each outer receptor file for the lat/lon in row
            # foundit = False
            # for f in listOuter:
            #     allouter = AllOuterReceptors(targetDir=self.targetDir, filenameOverride=f)
            #     outconcs = allouter.createDataframe()
            #
            #     concdata = outconcs[[lat,lon,source_id,pollutant,ems_type,conc]] \
            #         [(outconcs[lat]==row[lat]) & (outconcs[lon]==row[lon])]
            #     if not concdata.empty:
            #         foundit = True
            #         break
            # if not foundit:
            #     errmessage = """An error has happened while computing the Risk Breakdown. A max risk/HI
            #                           occured at an interpolated receptor but could not be found in the All Outer Receptor files """
            #     Logger.logMessage(errmessage)
            #     sys.exit()

            blocksummary_df = blocksummary_df.append(bsc_df)

            blocksummary_df.drop_duplicates().reset_index(drop=True)

            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', rec_type:'first',
                    utmn:'first', hill:'first', fips:'first', block:'first', population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

            # Aggregate concentration, grouped by FIPS/block
            risk_summed = blocksummary_df.groupby([fips, block]).agg(aggs)[blockSummaryChronic.getColumns()]

        allvalues = [['Cancer Risk'], maximum, ['Number of people'], hundo, ten, one, [''], incidences]

        histogram_df = pd.DataFrame(allvalues, columns=self.header).astype(dtype=int, errors='ignore')

        # Put final df into array
        self.dataframe = histogram_df
        self.data = self.dataframe.values
        yield self.dataframe

    def calculateRisk(self, pollutant_name, conc):
        URE = self.getRiskParams(pollutant_name)

        print("[conc:ure]= " + str(conc) + ":" + str(URE))
        return conc * URE

    def getRiskParams(self, pollutant_name):
        URE = 0.0

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant_name) + '$'

        # Since it's relatively expensive to get these values from their respective libraries, cache them locally.
        # Note that they are cached as a pair (i.e. if one is in there, the other one will be too...)
        if pollutant_name in self.riskCache:
            URE = self.riskCache[pollutant_name][ure]
        else:
            row = self.haplib_df.loc[
                self.haplib_df[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                URE = 0.0
            else:
                URE = row.iloc[0][ure]

            self.riskCache[pollutant_name] = {ure : URE}

        return URE

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded