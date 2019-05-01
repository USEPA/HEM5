import math
import re

import pandas as pd
import numpy as np
from pandas import Series
from functools import reduce

from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DoseResponse import *
from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.excel.Incidence import inc

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

        # Fill local caches for URE/RFC and organ endpoint values
        self.riskCache = {}
        self.organCache = {}

        for index, row in self.model.haplib.dataframe.iterrows():

            # Change rfcs of 0 to -1. This simplifies HI calculations. Don't have to worry about divide by 0.
            if row[rfc] == 0:
                rfcval = -1
            else:
                rfcval = row[rfc]

            self.riskCache[row[pollutant].lower()] = {ure : row[ure], rfc : rfcval}

            # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
            # we are using a regex that is specified to be the entire value. Since pollutant names can
            # contain parentheses, escape them before constructing the pattern.
            pattern = '^' + re.escape(row[pollutant]) + '$'
            organrow = self.model.organs.dataframe.loc[
                self.model.organs.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if organrow.size == 0:
                listed = []
            else:
                listed = organrow.values.tolist()

            # Note: sometimes there is a pollutant with no effect on any organ (RFC == 0). In this case it will
            # not appear in the organs library, and therefore 'listed' will be empty. We will just assign a
            # dummy list in this case...
            dummylist = [row[pollutant], ' ', 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            organs = listed[0] if len(listed) > 0 else dummylist
            self.organCache[row[pollutant].lower()] = organs

        self.outerblocks = self.model.outerblks_df[[lat, lon, utme, utmn, hill]]
        self.outerAgg = None
        self.outerInc = None

        # AllOuterReceptor DF columns
        self.columns = [fips, block, lat, lon, source_id, ems_type, pollutant, conc, aconc, elev, population, overlap]

        # Initialize max_riskhi dictionary. Keys are mir, and HIs. Values are
        # lat, lon, and risk value. This dictionary identifies the lat/lon of the max receptor for
        # the mir and each HI.
        self.max_riskhi = {}
        self.riskhi_parms = [mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                             hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
        for icol in self.riskhi_parms:
            self.max_riskhi[icol] = [0, 0, 0]

        # Initialize max_riskhi_bkdn dictionary. This dictionary identifies the Lat/lon of the max receptor for
        # the mir and each HI, and has source/pollutant specific risk at that lat/lon.
        # Keys are: parameter, source_id, pollutant, and emis_type.
        # Values are: lat, lon, and risk value.
        self.srcpols = self.model.all_polar_receptors_df[[source_id, pollutant, ems_type]].drop_duplicates().values.tolist()
        self.max_riskhi_bkdn = {}
        self.outerInc = {}
        for jparm in self.riskhi_parms:
            for jsrcpol in self.srcpols:
                self.max_riskhi_bkdn[(jparm, jsrcpol[0], jsrcpol[1], jsrcpol[2])] = [0, 0, 0]

        # Initialize the outerInc dictionary. This dictionary contains cancer incidence by source, pollutant,
        # and emis_type.
        # Keys are: source_id, pollutant, and emis_type
        # Value is: incidence
        for jsrcpol in self.srcpols:
            self.outerInc[(jsrcpol[0], jsrcpol[1], jsrcpol[2])] = 0


    def getHeader(self):
        return ['FIPs', 'Block', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                'Conc (µg/m3)', 'Acute Conc (µg/m3)', 'Elevation (m)',
                'Population', 'Overlap']

    def generateOutputs(self):
        """
        Interpolate polar pollutant concs to outer receptors.
        """

        #Define the number of polar grid sectors and rings
        num_sectors = len(self.model.all_polar_receptors_df['sector'].unique())
        num_rings = len(self.model.all_polar_receptors_df['ring'].unique())


        #Put all_polar_receptors DF into an array
        polarconcs_m = self.model.all_polar_receptors_df.values


        #subset outer blocks DF to needed columns
        outerblks_subset = self.model.outerblks_df[[fips, idmarplot, lat, lon, elev,
                                                    'angle', population, overlap, 's',
                                                    'ring_loc']].copy()

        #define sector/ring of 4 surrounding polar receptors for each outer receptor and set an index
        outerblks_subset[["s1", "s2", "r1", "r2"]] = outerblks_subset.apply(self.compute_s1s2r1r2, axis=1)

        #Put outerblks_subset DF into an array
        outerblks_m = outerblks_subset.values

        dlist = []

        #Process the outer blocks within a box defined by the corners (s1,r1), (s1,r2), (s1,r1), (s2,r2)
        for isector in range(1, num_sectors+1):
            for iring in range(1, num_rings):

                sector1 = isector
                sector2 = (isector % num_sectors) + 1
                ring1 = iring
                ring2 = iring + 1

                #Get all outer receptors within this box. If none, then go to the next box.
                box_truth = np.logical_and.reduce((outerblks_m[:, 10] == sector1,
                                                   outerblks_m[:, 11] == sector2,
                                                   outerblks_m[:, 12] == ring1,
                                                   outerblks_m[:, 13] == ring2))
                outerblks_touse = outerblks_m[box_truth]
                if outerblks_touse.size == 0:
                    continue

                #Get the polar source/pollutant concs for each corner of the box
                s1r1 = np.logical_and(polarconcs_m[:, 7] == sector1, polarconcs_m[:, 8] == ring1 )
                s1r2 = np.logical_and(polarconcs_m[:, 7] == sector1, polarconcs_m[:, 8] == ring2 )
                s2r1 = np.logical_and(polarconcs_m[:, 7] == sector2, polarconcs_m[:, 8] == ring1 )
                s2r2 = np.logical_and(polarconcs_m[:, 7] == sector2, polarconcs_m[:, 8] == ring2 )
                pconc_s1r1_m = polarconcs_m[s1r1]
                pconc_s1r2_m = polarconcs_m[s1r2]
                pconc_s2r1_m = polarconcs_m[s2r1]
                pconc_s2r2_m = polarconcs_m[s2r2]

                #Interpolate to each outer receptor in this box
                for row in outerblks_touse:

                    l_fips = row[0]
                    l_block = row[1][5:]
                    l_lat = row[2]
                    l_lon = row[3]
                    l_elev = row[4]
                    l_population = row[6]
                    l_overlap = row[7]

                    for iprow in range(0, len(pconc_s1r1_m)):
                        l_sourceid = pconc_s1r1_m[iprow, 0]
                        l_emistype = pconc_s1r1_m[iprow, 1]
                        l_pollutant = pconc_s1r1_m[iprow, 2]
                        s = row[8]
                        ring_loc = row[9]
                        pcconc_s1r1 = pconc_s1r1_m[iprow, 3] # chronic
                        pcconc_s1r2 = pconc_s1r2_m[iprow, 3] # chronic
                        pcconc_s2r1 = pconc_s2r1_m[iprow, 3] # chronic
                        pcconc_s2r2 = pconc_s2r2_m[iprow, 3] # chronic
                        paconc_s1r1 = pconc_s1r1_m[iprow, 4] # acute
                        paconc_s1r2 = pconc_s1r2_m[iprow, 4] # acute
                        paconc_s2r1 = pconc_s2r1_m[iprow, 4] # acute
                        paconc_s2r2 = pconc_s2r2_m[iprow, 4] # acute

                        # Interpolate chronic concs
                        if pcconc_s1r1 == 0 or pcconc_s1r2 == 0:
                            R_s12 = max(pcconc_s1r1, pcconc_s1r2)
                        else:
                            Lnr_s12 = (math.log(pcconc_s1r1) * (int(ring_loc)+1-ring_loc)) + (math.log(pcconc_s1r2) * (ring_loc-int(ring_loc)))
                            R_s12 = math.exp(Lnr_s12)

                        if pcconc_s2r1 == 0 or pcconc_s2r2 == 0:
                            R_s34 = max(pcconc_s2r1, pcconc_s2r2 )
                        else:
                            Lnr_s34 = (math.log(pcconc_s2r1) * (int(ring_loc)+1-ring_loc)) + (math.log(pcconc_s2r2 ) * (ring_loc-int(ring_loc)))
                            R_s34 = math.exp(Lnr_s34)
                        l_cconc = R_s12*(int(s)+1-s) + R_s34*(s-int(s))

                        # Interpolate acute concs
                        if paconc_s1r1 == 0 or paconc_s1r2 == 0:
                            R_s12 = max(paconc_s1r1, paconc_s1r2)
                        else:
                            Lnr_s12 = (math.log(paconc_s1r1) * (int(ring_loc)+1-ring_loc)) + (math.log(paconc_s1r2) * (ring_loc-int(ring_loc)))
                            R_s12 = math.exp(Lnr_s12)

                        if paconc_s2r1 == 0 or paconc_s2r2 == 0:
                            R_s34 = max(paconc_s2r1, paconc_s2r2 )
                        else:
                            Lnr_s34 = (math.log(paconc_s2r1) * (int(ring_loc)+1-ring_loc)) + (math.log(paconc_s2r2 ) * (ring_loc-int(ring_loc)))
                            R_s34 = math.exp(Lnr_s34)
                        l_aconc = R_s12*(int(s)+1-s) + R_s34*(s-int(s))
                        
                        datalist = [l_fips, l_block, l_lat, l_lon, l_sourceid, l_emistype, l_pollutant,
                                    l_cconc, l_aconc, l_elev, l_population, l_overlap]
                        dlist.append(datalist)

                # End of iteration for this box...time to check if we
                # need to write a batch and run the analyze function.
                if len(dlist) >= self.batchSize:
                    yield pd.DataFrame(dlist, columns=self.columns)
                    dlist = []


        # dataframe to array
        outerconc_df = pd.DataFrame(dlist, columns=self.columns)
        self.dataframe = outerconc_df
        self.data = self.dataframe.values
        yield self.dataframe




    def interpolate(self, pconcs, srcid, s1, s2, r1, r2, s, ring_loc):
        conc_s1r1 = pconcs[srcid+str(s1)+str(r1)]
        conc_s1r2 = pconcs[srcid+str(s1)+str(r2)]
        conc_s2r1 = pconcs[srcid+str(s2)+str(r1)]
        conc_s2r2 = pconcs[srcid+str(s2)+str(r2)]


        if conc_s1r1 == 0 or conc_s1r2 == 0:
            R_s12 = max(conc_s1r1, conc_s1r2)
        else:
            Lnr_s12 = ((math.log(conc_s1r1) * (int(ring_loc)+1-ring_loc)) +
                       (math.log(conc_s1r2) * (ring_loc-int(ring_loc))))
            R_s12 = math.exp(Lnr_s12)

        if conc_s2r1 == 0 or conc_s2r2 == 0:
            R_s34 = max(conc_s2r1, conc_s2r2 )
        else:
            Lnr_s34 = ((math.log(conc_s2r1) * (int(ring_loc)+1-ring_loc)) +
                       (math.log(conc_s2r2) * (ring_loc-int(ring_loc))))
            R_s34 = math.exp(Lnr_s34)

        interp_conc = R_s12*(int(s)+1-s) + R_s34*(s-int(s))
        return interp_conc


    def compute_s1s2r1r2(self, row):
        #define the four surrounding polar sector/rings for this outer block
        if int(row['s']) == self.model.numsectors:
            s1 = self.model.numsectors
            s2 = 1
        else:
            s1 = int(row['s'])
            s2 = int(row['s']) + 1
        r1 = int(row['ring_loc'])
        if r1 == self.model.numrings:
            r1 = r1 - 1
        r2 = int(row['ring_loc']) + 1
        if r2 > self.model.numrings:
            r2 = self.model.numrings
        return Series((s1, s2, r1, r2))




    def analyze(self, data):

        # Skip if no data
        if data.size > 0:

            # DF of Outer receptors in this box
            box_receptors = pd.DataFrame(data, columns=self.columns)

            # compute risk and HI by sourceid/pollutant for each Outer receptor in this box
            risks_df = self.calculateRisks(box_receptors[pollutant], box_receptors[conc])
            box_receptors_wrisk = pd.concat([box_receptors, risks_df], axis=1)

            # Merge box_receptors_wrisk with the outerblocks DF and select columns
            blksumm_cols = [lat, lon, overlap, elev, fips, block, utme, utmn, hill, population,
                            mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                            hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
            boxmerged = box_receptors_wrisk.merge(self.outerblocks, on=[lat, lon])[blksumm_cols]


            #----------- Accumulate Outer receptor risks by lat/lon for later use in BlockSummaryChronic ----------------

            blksumm_aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', fips:'first',
                            block:'first', utme:'first', utmn:'first', hill:'first', population:'first',
                            mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                            hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                            hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

            outeragg = boxmerged.groupby([lat, lon]).agg(blksumm_aggs)[blksumm_cols]

            if self.outerAgg is None:
                storage = self.outerblocks.shape[0]
                self.outerAgg = pd.DataFrame(columns=blksumm_cols, index=range(storage))
            self.outerAgg = self.outerAgg.append(outeragg)


            #----------- Keep track of maximum risk and HI ---------------------------------------

            # sum risk and HIs to lat/lon
            aggs = {lat:'first', lon:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

            sum_columns = [lat, lon, mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                           hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
            riskhi_by_latlon = box_receptors_wrisk.groupby([lat, lon]).agg(aggs)[sum_columns]

            # Find max mir and each max HI for Outer receptors in this box. Update the max_riskhi and
            # max_riskhi_bkdn dictionaries.
            for iparm in self.riskhi_parms:
                idx = riskhi_by_latlon[iparm].idxmax()
                if riskhi_by_latlon[iparm].loc[idx] > self.max_riskhi[iparm][2]:
                    # Update the  max_riskhi dictionary
                    maxlat = riskhi_by_latlon[lat].loc[idx]
                    maxlon = riskhi_by_latlon[lon].loc[idx]
                    self.max_riskhi[iparm] = [maxlat, maxlon, riskhi_by_latlon[iparm].loc[idx]]
                    # Update the max_riskhi_bkdn dictionary
                    box_receptors_max = box_receptors_wrisk[(box_receptors_wrisk[lat]==maxlat) & (box_receptors_wrisk[lon]==maxlon)]
                    for index, row in box_receptors_max.iterrows():
                        self.max_riskhi_bkdn[(iparm, row[source_id], row[pollutant], row[ems_type])] = \
                            [maxlat, maxlon, row[iparm]]

            #--------------- Keep track of incidence -----------------------------------------

            # Compute incidence for each Outer rececptor and then sum incidence by source_id and pollutant
            box_receptors_wrisk['inc'] = box_receptors_wrisk.apply(lambda row: (row[mir] * row[population])/70, axis=1)
            boxInc = box_receptors_wrisk.groupby([source_id, pollutant, ems_type], as_index=False)[[inc]].sum()

            # Update the outerInc incidence dictionary
            for incdx, incrow in boxInc.iterrows():
                self.outerInc[(incrow[source_id], incrow[pollutant], incrow[ems_type])] = \
                    self.outerInc[(incrow[source_id], incrow[pollutant], incrow[ems_type])] + incrow['inc']


    def calculateRisks(self, pollutants, concs):

        risklist = []
        riskcols = [mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                    hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]

        mirlist = [n * self.riskCache[m.lower()][ure] for m, n in zip(pollutants, concs)]
        hilist = [((k/self.riskCache[j.lower()][rfc]/1000) * np.array(self.organCache[j.lower()][2:])).tolist()
                  for j, k in zip(pollutants, concs)]

        riskdf = pd.DataFrame(np.column_stack([mirlist, hilist]), columns=riskcols)
        # change any negative HIs to 0
        riskdf[riskdf < 0] = 0
        return riskdf
