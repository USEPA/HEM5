import math
import re
import time

import pandas as pd
import numpy as np
from pandas import Series
from functools import reduce

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

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        columns = [fips, block, lat, lon, source_id, ems_type, pollutant, conc, aconc, elev, population, overlap]

        #extract polar concs from Aermod plotfile and round the utm coordinates
        polarplot_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
        polarplot_df.utme = polarplot_df.utme.round()
        polarplot_df.utmn = polarplot_df.utmn.round()

        #array of unique source_id's from polarplot DF
        srcids = polarplot_df[source_id].unique().tolist()


        #merge polarplot DF with polargrid DF and set an index
        polargrid_concs = pd.merge(polarplot_df[['utme', 'utmn', 'source_id', 'result']],
                                   self.model.polargrid[['utme', 'utmn', 'sector', 'ring']],
                                   on=['utme', 'utmn'], how='left')
        polargrid_concs.set_index(['source_id', 'sector', 'ring'], inplace=True, drop=False)
        polargrid_concs.sort_index(inplace=True)
        
        
        #subset outer blocks DF to needed columns
        outerblks_subset = self.model.outerblks_df[[fips, idmarplot, lat, lon, elev, 
                                                    'angle', population, overlap, 's', 
                                                    'ring_loc']].copy()

        #define sector/ring of 4 surrounding polar receptors for each outer receptor and set an index
        outerblks_subset[["s1", "s2", "r1", "r2"]] = outerblks_subset.apply(self.compute_s1s2r1r2, axis=1)
        outerblks_subset.set_index(['s1', 's2', 'r1', 'r2'], inplace=True, drop=False)
        outerblks_subset.sort_index(inplace=True)


        num_sectors = len(polargrid_concs['sector'].unique())
        num_rings = len(polargrid_concs['ring'].unique())

          
        dlist = []


        #Process all outer blocks within a box defined by the corners (s1,r1), (s1,r2), (s1,r1), (s2,r2)
        for isector in range(1, num_sectors):
            for iring in range(1, num_rings):
                
                #timer
                box_starttime = time.clock()
                
                sector1 = isector
                sector2 = isector + 1
                ring1 = iring
                ring2 = iring + 1
                
                #If sector1,sector2,ring1,ring2 are in the index of outerblks_subset, then
                #create a DF of outer blocks within this box. Otherwise go to next box.
                if (sector1, sector2, ring1, ring2) in outerblks_subset.index:
                    outerblks_touse = outerblks_subset.loc[sector1, sector2, ring1, ring2]
                else:
                    continue
                
#                outerblks_touse = outerblks_subset.loc[(outerblks_subset['s1'] == sector1) & 
#                                                       (outerblks_subset['s2'] == sector2) &
#                                                       (outerblks_subset['r1'] == ring1) &
#                                                       (outerblks_subset['r2'] == ring2)]
#                
#                #if no outer blocks, go to the next box
#                if outerblks_touse.empty == True:
#                    continue
                
                #work on one source_id at a time to optimize retrieval time
                for isrc in srcids:
                    
#                    #subset the polargrid_concs DF to this source_id and set of sectors and rings
#                    sectorlist = [sector1, sector2]
#                    ringlist = [ring1, ring2]
#                    polargrid_concs_1srcid = polargrid_concs[['sector', 'ring', 'source_id', 'result']].query \
#                        ('source_id == @isrc and sector == @sectorlist and ring == @ringlist')
#                    polargrid_concs_1srcid.set_index(['sector', 'ring'], inplace=True)

                    #subset the hapemis DF to this source_id
                    hapemis_onesrcid = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]] \
                                       .loc[self.model.runstream_hapemis[source_id] == isrc]
                    
                    #Interpolate polar Aermod concs to each outer block in this box
                    #Also apply emissions to the interpolated conc
                    for row_id, row in enumerate(outerblks_touse.values):
                        d_fips = row[0]
                        d_block = row[1][6:]
                        d_lat = row[2]
                        d_lon = row[3]
                        d_elev = row[4]
                        d_population = row[6]
                        d_aconc = 0.0
                        d_overlap = row[7]
                        d_sourceid = isrc
                        d_emistype = "C"
                        ring_loc = row[9]
                        s = row[8]
                        conc_interp = self.interpolate(polargrid_concs, isrc, sector1, sector2,
                                                  ring1, ring2, s, ring_loc)
                        #multiply pollutant specific emissions by interpolated conc
                        for ipoll in hapemis_onesrcid.itertuples():
                            d_pollutant = ipoll[2]
                            d_conc = conc_interp * ipoll[3] * self.cf
                            datalist = [d_fips, d_block, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, 
                                        d_conc, d_aconc, d_elev, d_population, d_overlap]
                            dlist.append(datalist)
                
                #timer
                box_endtime = time.clock()
                print("One box took ", box_endtime - box_starttime, " seconds")
                
                # End of iteration for this box...time to check if we
                # need to write a batch.
                if len(dlist) >= self.batchSize:
                    yield pd.DataFrame(dlist, columns=columns)
                    dlist = []
                
                
        outerconc_df = pd.DataFrame(dlist, columns=columns)

        #Debug

        #import pdb; pdb.set_trace()

        # dataframe to array
        self.dataframe = outerconc_df
        self.data = self.dataframe.values
        yield self.dataframe


    def interpolate(self, pconcs, srcid, s1, s2, r1, r2, s, ring_loc):
        conc_s1r1 = pconcs['result'].loc[srcid, s1, r1]
        conc_s1r2 = pconcs['result'].loc[srcid, s1, r2]
        conc_s2r1 = pconcs['result'].loc[srcid, s2, r1]
        conc_s2r2 = pconcs['result'].loc[srcid, s2, r2]

#        conc_s1r1 = pconcs['result'].loc[(pconcs['sector']==s1) & (pconcs['ring']==r1)].iat[0]
#        conc_s1r2 = pconcs['result'].loc[(pconcs['sector']==s1) & (pconcs['ring']==r2)].iat[0]
#        conc_s2r1 = pconcs['result'].loc[(pconcs['sector']==s2) & (pconcs['ring']==r1)].iat[0]
#        conc_s2r2 = pconcs['result'].loc[(pconcs['sector']==s2) & (pconcs['ring']==r2)].iat[0]
        
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


#    def interpolate(self, conc_s1r1, conc_s2r1, conc_s1r2, conc_s2r2, s, ring_loc):
#        interp_conc = np.zeros(len(conc_s1r1))
#        for i in np.arange(len(conc_s1r1)):
#            if conc_s1r1[i] == 0 or conc_s1r2[i] == 0:
#                R_s12 = max(conc_s1r1[i], conc_s1r2[i])
#            else:
#                Lnr_s12 = ((math.log(conc_s1r1[i]) * (int(ring_loc)+1-ring_loc)) + 
#                          (math.log(conc_s1r2[i]) * (ring_loc-int(ring_loc))))
#                R_s12 = math.exp(Lnr_s12)
#    
#            if conc_s2r1[i] == 0 or conc_s2r2[i] == 0:
#                R_s34 = max(conc_s2r1[i], conc_s2r2[i] )
#            else:
#                Lnr_s34 = ((math.log(conc_s2r1[i]) * (int(ring_loc)+1-ring_loc)) + 
#                          (math.log(conc_s2r2[i]) * (ring_loc-int(ring_loc))))
#                R_s34 = math.exp(Lnr_s34)
#    
#            interp_conc[i] = R_s12*(int(s)+1-s) + R_s34*(s-int(s))       
#        return interp_conc
    
        

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