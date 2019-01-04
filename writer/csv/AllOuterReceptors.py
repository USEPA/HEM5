import math
import re

from pandas import Series

from log import Logger
from upload.DoseResponse import *
from writer.csv.AllInnerReceptors import *
from writer.excel.Incidence import inc

mir = 'mir';
hi_resp = 'hi_resp';
hi_live = 'hi_live';
hi_neur = 'hi_neur';
hi_deve = 'hi_deve';
hi_repr = 'hi_repr';
hi_kidn = 'hi_kidn';
hi_ocul = 'hi_ocul';
hi_endo = 'hi_endo';
hi_hema = 'hi_hema';
hi_immu = 'hi_immu';
hi_skel = 'hi_skel';
hi_sple = 'hi_sple';
hi_thyr = 'hi_thyr';
hi_whol = 'hi_whol';

class AllOuterReceptors(CsvWriter):
    """
    Provides the annual average concentration interpolated at every census block beyond the modeling cutoff distance but
    within the modeling domain, specific to each source ID and pollutant, along with receptor information, and acute
    concentration (if modeled) and wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_outer_receptors.csv")

        # Local cache for URE/RFC values
        self.riskCache = {}

        # Local cache for organ endpoint values
        self.organCache = {}

        self.outerblocks = self.model.outerblks_df[[lat, lon, utme, utmn, hill]]
        self.outerAgg = None
        self.outerInc = None

    def getHeader(self):
        return ['FIPs', 'Block', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                'Conc (µg/m3)', 'Acute Conc (µg/m3)', 'Elevation (m)',
                'Population', 'Overlap']

    def generateOutputs(self):
        """
        Interpolate polar pollutant concs to outer receptors.
        """
        # Logger.log("Polar data", self.model.all_polar_receptors_df, False)

        #list of unique source ids/pollutants from polar concs
        uniqsrcpol = self.model.all_polar_receptors_df[[source_id, pollutant]].drop_duplicates().as_matrix()
        #        uniqsrcpol = [list(x) for x in set(tuple(x) for x in srcpol)]

        #convert outer blocks dataframe to matrix
        outerblks_m = self.model.outerblks_df.as_matrix()

        #convert all polar receptors dataframe to matrix
        all_polar_receptors_m = self.model.all_polar_receptors_df.as_matrix()


        dlist = []
        columns = [fips, block, lat, lon, source_id, ems_type, pollutant, conc, aconc, elev, population, overlap]

        print("total size: " + str(outerblks_m.size))

        #process each outer block
        for row in outerblks_m:

            d_fips = row[1]
            d_block = row[3][6:]
            d_lat = row[4]
            d_lon = row[5]
            d_elev = row[0]
            d_population = row[7]
            d_emistype = "C"
            d_aconc = 0.0
            d_overlap = row[15]

            #ring and sector of this outer block
            ring_loc = row[19]
            cs = row[17]

            #define the four surrounding polar sector/rings for this outer block
            s = ((row[14] * self.model.numsectors)/360.0 % self.model.numsectors) + 1
            if int(s) == self.model.numsectors:
                s1 = self.model.numsectors
                s2 = 1
            else:
                s1 = int(s)
                s2 = int(s) + 1
            r1 = int(row[19])
            if r1 == self.model.numrings:
                r1 = r1 - 1
            r2 = int(row[19]) + 1
            if r2 > self.model.numrings:
                r2 = self.model.numrings

            s1r1 = np.logical_and(all_polar_receptors_m[:, 6] == s1, all_polar_receptors_m[:,7] == r1 )
            s1r2 = np.logical_and(all_polar_receptors_m[:, 6] == s1, all_polar_receptors_m[:,7] == r2 )
            s2r1 = np.logical_and(all_polar_receptors_m[:, 6] == s2, all_polar_receptors_m[:,7] == r1 )
            s2r2 = np.logical_and(all_polar_receptors_m[:, 6] == s2, all_polar_receptors_m[:,7] == r2 )

            co1 = all_polar_receptors_m[s1r1]
            co2 = all_polar_receptors_m[s1r2]
            co3 = all_polar_receptors_m[s2r1]
            co4 = all_polar_receptors_m[s2r2]

            #full has polar conc records for the 4 surrounding polar receptors
            full = np.concatenate((co1, co2, co3, co4), axis=0)


            #work on one source/pollutant at a time
            for srcpolrow in uniqsrcpol:

                #subset to specific source id and pollutant
                sub = full[(full[:,0] == srcpolrow[0]) & (full[:,2] == srcpolrow[1])]

                #polar concs of 4 surrounding polar receptors
                concentration = sub[:, 3]

                d_sourceid = srcpolrow[0]
                d_pollutant = srcpolrow[1]

                #interpolate
                if concentration[0] == 0 or concentration[1] == 0:
                    R_s12 = max(concentration[0], concentration[1])
                else:
                    Lnr_s12 = (math.log(concentration[0]) * (int(ring_loc)+1-ring_loc)) + (math.log(concentration[1]) * (ring_loc-int(ring_loc)))
                    R_s12 = math.exp(Lnr_s12)

                if concentration[2] == 0 or concentration[3] == 0:
                    R_s34 = max(concentration[2], concentration[3] )
                else:
                    Lnr_s34 = (math.log(concentration[2]) * (int(ring_loc)+1-ring_loc)) + (math.log(concentration[3] ) * (ring_loc-int(ring_loc)))
                    R_s34 = math.exp(Lnr_s34)

                d_conc = R_s12*(int(cs)+1-cs) + R_s34*(cs-int(cs))

                datalist = [d_fips, d_block, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc,
                            d_aconc, d_elev, d_population, d_overlap]

                dlist.append(datalist)

            # End of iteration for this outer receptor...time to check if we
            # need to write a batch.
            if len(dlist) >= self.batchSize:
                yield pd.DataFrame(dlist, columns=columns)
                dlist = []

        outerconc_df = pd.DataFrame(dlist, columns=columns)

        # dataframe to array
        self.dataframe = outerconc_df
        self.data = self.dataframe.values
        yield self.dataframe

    def analyze(self, data):
        columns = [pollutant, conc, lat, lon, fips, block, overlap, elev,
           utme, utmn, population, hill]

        allouter_df = data

        # join outer receptor df with the outer block df and then select columns
        Logger.logMessage("before allouter merge")
        outermerged = allouter_df.merge(self.outerblocks, on=[lat, lon])[columns]

        Logger.logMessage("before outermerged apply")
        outermerged[[mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo,
                     hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]] = \
            outermerged.apply(lambda row: self.calculateRisks(row[pollutant], row[conc]), axis=1)

        aggs = {pollutant:'first', lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first',
                utmn:'first', hill:'first', conc:'first', fips:'first', block:'first', population:'first',
                mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

        columns = [lat, lon, overlap, elev, fips, block, utme, utmn, hill, population,
                   mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                   hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]

        Logger.logMessage("before outermerged groupby...size = " + str(outermerged.size))

        outeragg = outermerged.groupby([lat, lon]).agg(aggs)[columns]

        Logger.logMessage("before outerAgg append")
        if self.outerAgg is None:
            storage = self.model.outerblks_df.shape[0]
            Logger.logMessage("STORAGE: " + str(storage))
            self.outerAgg = pd.DataFrame(columns=columns, index=range(storage))
        self.outerAgg = self.outerAgg.append(outeragg)


        Logger.logMessage("before outerInc apply")
        # compute incidence for each Outer rececptor row and then sum incidence by source_id and pollutant
        allouter_df['inc'] = allouter_df.apply(lambda row: self.calculateMirRisk(row[pollutant],
                                                                              row[conc]) * row[population]/70, axis=1)

        Logger.logMessage("before outerInc groupby")
        outerInc = allouter_df.groupby([source_id, pollutant, ems_type], as_index=False)[[inc]].sum()

        Logger.logMessage("before outerInc append")
        if self.outerInc is None:
            storage = self.model.outerblks_df.shape[0]
            self.outerInc = pd.DataFrame(columns=columns, index=range(storage))
        self.outerInc = self.outerInc.append(outerInc)




        # maxes = {mir: 0, hi_resp: 0, hi_live: 0, hi_neur: 0, hi_deve: 0, hi_repr: 0, hi_kidn: 0, hi_ocul: 0, hi_endo: 0,
        #         hi_hema: 0, hi_immu: 0, hi_skel: 0, hi_sple: 0, hi_thyr: 0, hi_whol: 0}
        #
        # for index, row in outeragg.iterrows():
        #     self.updateMaxes(maxes, row)

    def calculateMirRisk(self, pollutant_name, conc):
        URE = None

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant_name) + '$'

        # Since it's relatively expensive to get this from the dose response library, cache them locally.
        if pollutant_name in self.riskCache:
            URE = self.riskCache[pollutant_name][ure]
        else:
            row = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                msg = 'Could not find pollutant ' + pollutant_name + ' in the haplib!'
                Logger.logMessage(msg)
                # Logger.log(msg, self.model.haplib.dataframe, False)
                URE = 0
            else:
                URE = row.iloc[0][ure]

            self.riskCache[pollutant_name] = {ure : URE}


        mir = conc * URE
        return mir

    def calculateRisks(self, pollutant_name, conc):
        URE = None
        RFC = None

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
            row = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                msg = 'Could not find pollutant ' + pollutant_name + ' in the haplib!'
                Logger.logMessage(msg)
                # Logger.log(msg, self.model.haplib.dataframe, False)
                URE = 0
                RFC = 0
            else:
                URE = row.iloc[0][ure]
                RFC = row.iloc[0][rfc]

            self.riskCache[pollutant_name] = {ure : URE, rfc : RFC}

        organs = None
        if pollutant_name in self.organCache:
            organs = self.organCache[pollutant_name]
        else:
            row = self.model.organs.dataframe.loc[
                self.model.organs.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                # Couldn't find the pollutant...set values to 0 and log message
                # Logger.logMessage('Could not find pollutant ' + pollutant_name + ' in the target organs.')
                listed = []
            else:
                listed = row.values.tolist()

            # Note: sometimes there is a pollutant with no effect on any organ (RFC == 0). In this case it will
            # not appear in the organs library, and therefore 'listed' will be empty. We will just assign a
            # dummy list in this case...
            organs = listed[0] if len(listed) > 0 else list(range(16))
            self.organCache[pollutant_name] = organs

        risks = []
        MIR = conc * URE
        risks.append(MIR)

        # Note: indices 2-15 correspond to the organ response value columns in the organs library...
        for i in range(2, 16):
            hazard_index = (0 if RFC == 0 else (conc/RFC/1000)*organs[i])
            risks.append(hazard_index)
        return Series(risks)