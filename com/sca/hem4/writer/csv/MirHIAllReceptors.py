from math import floor, log10

from com.sca.hem4.support.Directory import Directory
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.writer.csv.BlockSummaryChronicNonCensus import BlockSummaryChronicNonCensus
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.CensusBlocks import haversineDistance
from tkinter import messagebox


class MirHIAllReceptors(CsvWriter, InputFile):

    def __init__(self, targetDir=None, facilityId=None, model=None, plot_df=None, acuteyn=None,
                 filenameOverride=None, createDataframe=False):

        self.output_dir = targetDir

        # The radius is hard-coded to the maximum, but we're including the distance for each block
        # in the result so we can filter down to other radius values if needed.
        self.radius = 50000

        filename = "MIR_HI_allreceptors.csv" if filenameOverride is None else filenameOverride
        path = os.path.join(self.output_dir, filename)

        CsvWriter.__init__(self, model, plot_df)
        InputFile.__init__(self, path, createDataframe)

        self.filename = path
        self.basepath = os.path.basename(os.path.normpath(self.output_dir))
        self.facilityIds = Directory.find_facilities(self.output_dir)
        self.altrec = self.determineAltRec(self.output_dir)

    def getHeader(self):
        return ['FIPS', 'Block', 'Lon', 'Lat', 'Population', 'MIR', 'MIR (rounded)', hi_resp, hi_live,
                hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple,
                hi_thyr, hi_whol, 'Facility count', 'Distance']

    def getColumns(self):
        return [fips, block, lon, lat, population, mir, 'mir_rounded', hi_resp, hi_live,
                hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple,
                hi_thyr, hi_whol, 'fac_count', distance]

    def generateOutputs(self):

        blocksummary_df = pd.DataFrame()

        # Used for finding the fac center
        try:
            maxRiskAndHI = FacilityMaxRiskandHI(targetDir=self.output_dir, filenameOverride=self.basepath + "_facility_max_risk_and_hi.xlsx")
            maxRiskAndHI_df = maxRiskAndHI.createDataframe()
        except FileNotFoundError:
            messagebox.showinfo("Missing facility max risk and hi",
                                "Unable to find the required file: \n" + self.basepath + "_facility_max_risk_and_hi.xlsx" +
                                "\nPlease correct and try again.")
            return            

        for facilityId in self.facilityIds:
            Logger.logMessage("Inspecting facility folder " + facilityId + " for output files...")

            try:
                targetDir = self.output_dir + "/" + facilityId

                maxrisk_df = maxRiskAndHI_df.loc[maxRiskAndHI_df['Facil_id'] == facilityId]
                center_lat = maxrisk_df.iloc[0]['fac_center_latitude']
                center_lon = maxrisk_df.iloc[0]['fac_center_longitude']
                ceny, cenx, zone, hemi, epsg = UTM.ll2utm(center_lat, center_lon)

                blockSummaryChronic = BlockSummaryChronicNonCensus(targetDir=targetDir, facilityId=facilityId) if \
                    self.altrec == 'Y' else BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId)

                bsc_df = blockSummaryChronic.createDataframe()
                # Remove rows where population is zero
                bsc_df = bsc_df[bsc_df['population'] != 0]
                bsc_df['fac_count'] = 1
                blkcoors = np.array(tuple(zip(bsc_df.lon, bsc_df.lat)))                
                bsc_df[distance] = haversineDistance(blkcoors, center_lon, center_lat)

                maxdist = self.radius
                bsc_df = bsc_df.query('distance <= @maxdist').copy()
                blocksummary_df = blocksummary_df.append(bsc_df)

            except BaseException as e:
                print("Error gathering output information: " + repr(e))
                print("Skipping facility " + facilityId)
                continue

        blocksummary_df.drop_duplicates().reset_index(drop=True)

        columns = [fips, block, lon, lat, population, mir, hi_resp, hi_live,
                   hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple,
                   hi_thyr, hi_whol, 'fac_count', distance]

        if self.altrec == 'N':

            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', blk_type:'first',
                    utmn:'first', hill:'first', fips:'first', block:'first', population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum', 'fac_count':'sum',
                    distance:'min'}

            # Aggregate concentration, grouped by FIPS/block
            risk_summed = blocksummary_df.groupby([fips, block]).agg(aggs)[columns]

        else:

            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', blk_type:'first',
                    utmn:'first', hill:'first', rec_id: 'first', population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum', 'fac_count':'sum',
                    distance:'min'}

            # Aggregate concentration, grouped by rec_id
            risk_summed = blocksummary_df.groupby([rec_id]).agg(aggs)[columns]

        risk_summed['mir_rounded'] = risk_summed[mir].apply(self.round_to_sigfig, 1)

        # Re-order columns
        risk_summed = risk_summed[self.getColumns()]

        # Weed out blocks that correspond to schools, monitors, etc.
        risk_summed = risk_summed.loc[(~risk_summed[block].str.contains('S')) & (~risk_summed[block].str.contains('M'))]

        # dataframe to array
        self.dataframe = risk_summed
        self.data = self.dataframe.values

        yield self.dataframe

    def determineAltRec(self, targetDir):

        # Check the Inputs folder for the existence of alt_receptors.csv
        fpath = os.path.join(targetDir, "Inputs", "alt_receptors.csv")
        if os.path.exists(fpath):
            altrecUsed = 'Y'
        else:
            altrecUsed = 'N'

        return altrecUsed

    def round_to_sigfig(self, x, sig=1):
        if x == 0:
            return 0;

        if math.isnan(x):
            return float('NaN')

        rounded = round(x, sig-int(floor(log10(abs(x))))-1)
        return rounded

    def createDataframe(self):
        self.numericColumns = [lat, lon, mir, 'mir_rounded', population, hi_resp, hi_live,
                               hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple,
                               hi_thyr, hi_whol, 'fac_count', distance]
        self.strColumns = [fips, block]
        df = self.readFromPathCsv(self.getColumns())
        return df.fillna("")

