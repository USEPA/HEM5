import math
import re

import pandas as pd
import numpy as np
from pandas import Series
from functools import reduce
from com.sca.hem4.FacilityPrep import *
from com.sca.hem4.log.Logger import Logger
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
aresult = 'aresult';
utme = 'utme';
utmn = 'utmn';
elev = 'elev';
hill = 'hill';
flag = 'flag';
avg_time = 'avg_time';
source_id = 'source_id';
num_yrs = 'num_yrs';
net_id = 'net_id';


class AllOuterReceptors(CsvWriter, InputFile):
    """
    Provides the annual average concentration interpolated at every census block beyond the modeling cutoff distance but
    within the modeling domain, specific to each source ID and pollutant, along with receptor information, and acute
    concentration (if modeled) and wet and dry deposition flux (if modeled). This class can act as both a writer and a
    reader of the csv file that holds outer receptor information.
    """

    def __init__(self, targetDir=None, facilityId=None, model=None, plot_df=None, acuteyn=None, 
                 filenameOverride=None, createDataframe=False):
        # Initialization for CSV reading/writing. If no file name override, use the
        # default construction.
        filename = facilityId + "_all_outer_receptors.csv" if filenameOverride is None else filenameOverride
        path = os.path.join(targetDir, filename)

        CsvWriter.__init__(self, model, plot_df)
        InputFile.__init__(self, path, createDataframe)
        
        self.targetDir = targetDir
        self.filename = path
        self.acute_yn = acuteyn
        self.plot_df = plot_df

        self.riskCache = {}
        self.organCache = {}

        # No need to go further if we are instantiating this class to read in a CSV file...
        if self.model is None:
            return

        # Fill local caches for URE/RFC and organ endpoint values
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
        self.columns = self.getColumns()

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

    def getColumns(self):
        return [fips, block, lat, lon, source_id, ems_type, pollutant, conc, aconc, elev, population, overlap]


    def generateOutputs(self):
        """
        Interpolate polar pollutant concs to outer receptors.
        """

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        # If acute was run for this facility, read the acute plotfile
        if self.acute_yn == 'Y':
            apfile = open(self.targetDir + "maxhour.plt", "r")
            self.aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,aresult,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9], 
                converters={utme:np.float64,utmn:np.float64,aresult:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str
                       ,concdate:np.str},
                comment='*') 
        
        #extract Chronic polar concs from the Chronic plotfile and round the utm coordinates
        polarcplot_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
        polarcplot_df.utme = polarcplot_df.utme.round()
        polarcplot_df.utmn = polarcplot_df.utmn.round()

        # If acute was run for this facility, extract polar concs from Acute plotfile and join to
        # chronic polar concs, otherwise, add column of 0's for acute result
        if self.acute_yn == 'Y':
            polaraplot_df = self.aplot_df.query("net_id == 'POLGRID1'").copy()
            polaraplot_df.utme = polaraplot_df.utme.round()
            polaraplot_df.utmn = polaraplot_df.utmn.round()
            polarplot_df = pd.merge(polarcplot_df, polaraplot_df[[source_id, utme, utmn, aresult]], 
                                    how='inner', on = [source_id, utme, utmn])
        else:
            polarplot_df = polarcplot_df.copy()
            polarplot_df[aresult] = 0.0


        # Assign sector and ring to polar concs from polarplot_df and set an index
        # of source_id + sector + ring
        self.polarconcs = pd.merge(polarplot_df, self.model.polargrid[['utme', 'utmn', 'sector', 'ring']], 
                             how='inner', on=['utme', 'utmn'])
        self.polarconcs['newindex'] = self.polarconcs['source_id'] \
                                        + 's' + self.polarconcs['sector'].apply(str) \
                                        + 'r' + self.polarconcs['ring'].apply(str)
        self.polarconcs.set_index(['newindex'], inplace=True)
        
        # QA - make sure merge retained all rows
        if self.polarconcs.shape[0] != polarplot_df.shape[0]:
            print("Error! self.polarconcs has wrong number of rows in AllOuterReceptors")
            #TODO stop this facility

        #subset outer blocks DF to needed columns and sort by increasing distance
        outerblks_subset = self.model.outerblks_df[[fips, idmarplot, lat, lon, elev,
                                                    'distance', 'angle', population, overlap,
                                                    's', 'ring_loc']].copy()
        outerblks_subset['block'] = outerblks_subset['idmarplot'].str[5:]
        outerblks_subset.sort_values(by=['distance'], axis=0, inplace=True)

        #Debug
        import pdb; pdb.set_trace() 


        # Define sector/ring of 4 surrounding polar receptors of each outer receptor
        a_s = outerblks_subset['s'].values
        a_ringloc = outerblks_subset['ring_loc'].values
        as1, as2, ar1, ar2 = self.compute_s1s2r1r2(a_s, a_ringloc)
        outerblks_subset['s1'] = as1.tolist()
        outerblks_subset['s2'] = as2.tolist()
        outerblks_subset['r1'] = ar1.tolist()
        outerblks_subset['r2'] = ar2.tolist()

        # Assign each source_id to every outer receptor
        srcids = self.polarconcs['source_id'].unique().tolist()
        srcid_df = pd.DataFrame(srcids, columns=['source_id'])
        srcid_df['key'] = 1
        outerblks_subset['key'] = 1
        outer_for_interp = pd.merge(outerblks_subset, srcid_df, on=['key'])
        
        
        # Get the 4 surrounding polar Aermod concs of each outer receptor
        cs1r1 = pd.merge(outer_for_interp, self.polarconcs[['sector','ring','source_id','result']],
                         how='left', left_on=['s1','r1','source_id'],
                         right_on=['sector','ring','source_id'])
        a_s1 = outer_for_interp['s1'].values
        a_s2 = outer_for_interp['s2'].values
        a_r1 = outer_for_interp['r1'].values
        a_r2 = outer_for_interp['r2'].values
        a_sid = outer_for_interp['source_id'].values        
        a_ccs1r1, a_ccs1r2, a_ccs2r1, a_ccs2r2, a_ccemistype = self.get4Corners(a_s1, a_s2, a_r1, a_r2, a_sid)        

        # Interpolate polar Aermod concs to each outer receptor
        a_sectfrac = outer_for_interp['s'].values
        a_ringfrac = outer_for_interp['ring_loc'].values
        a_intconc = self.interpolate(a_ccs1r1, a_ccs1r2, a_ccs2r1, a_ccs2r2, a_sectfrac, a_ringfrac)
        
        #........ Apply emissions to interpolated outer concs and write...............
        
        # First build dataframes of pollutant info from hapemis for each source_id
        srcpol_dfs = {}
        for src in srcids:
            dfname = src + '_df'
            srcpol_dfs[dfname] = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]] \
                            .loc[self.model.runstream_hapemis[source_id] == src]
        # initialize output list
        dlist = []
        collist = self.getColumns()

        # Compute pollutant specific concs and write when needed       
        k = 0
        for row1 in outer_for_interp.itertuples():
            d_fips = row1.fips
            d_block = row1.block
            d_lat = row1.lat
            d_lon = row1.lon
            d_elev = row1.elev
            d_population = row1.population
            d_overlap = row1.overlap
            d_emistype = a_ccemistype[k]
            d_sourceid = row1.source_id
            
            srcdfname = d_sourceid + '_df'
            poll_df = srcpol_dfs[srcdfname]
            for row2 in poll_df.itertuples():
                d_pollutant = row2.pollutant
                d_conc = a_intconc[k] * row2.emis_tpy * self.cf
                d_aconc = 0
#                d_aconc = row1.aresult * row2.emis_tpy * self.cf * self.model.facops.iloc[0][multiplier]    
                datalist = [d_fips, d_block, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc,
                            d_aconc, d_elev, d_population, d_overlap]
                dlist.append(dict(zip(collist, datalist)))

            # Check if we need to write a batch and run the analyze function.            
            if len(dlist) >= self.batchSize:
                yield pd.DataFrame(dlist, columns=self.columns)
                dlist = []

        # Done. Dataframe to array
        outerconc_df = pd.DataFrame(dlist, columns=self.columns)
        self.dataframe = outerconc_df
        self.data = self.dataframe.values
        yield self.dataframe
            
        
#        #Debug
#        import pdb; pdb.set_trace() 
#
#
#        #Define the number of polar grid sectors and rings
#        num_sectors = len(self.model.all_polar_receptors_df['sector'].unique())
#        num_rings = len(self.model.all_polar_receptors_df['ring'].unique())
#
#        # Create a working copy of all_polar_receptors_df and define an index
#        self.allpolar_work = self.model.all_polar_receptors_df.copy()
#        self.allpolar_work['newindex'] = self.allpolar_work['sector'].apply(str) \
#                                         + self.allpolar_work['ring'].apply(str) \
#                                         + self.allpolar_work['ems_type'] \
#                                         + self.allpolar_work['source_id'] \
#                                         + self.allpolar_work['pollutant']
#        self.allpolar_work.set_index(['newindex'], inplace=True)
#        
#
#
#        # initialize output list
#        dlist = []
#        
#        #Process the outer blocks within a box defined by the corners (s1,r1), (s1,r2), (s1,r1), (s2,r2)
#        for isector in range(1, num_sectors + 1):
#            for iring in range(1, num_rings + 1):
#
#                is1 = isector
#                is2 = num_sectors if isector==num_sectors-1 else (isector + 1) % num_sectors
#                ir1 = iring
#                ir2 = num_rings if iring==num_rings-1 else (iring + 1) % num_rings
#                                
#                #Get all outer receptors within this box. If none, then go to the next box.
#                outerblks_inbox = outerblks_subset.query('s1==@is1 and s2==@is2 and r1==@ir1 and r2==@ir2').copy()
#                if outerblks_inbox.size == 0:
#                    continue
#                
#                # Query allpolar for sector and ring
#                qry_s1r1 = self.allpolar_work.query('(sector==@is1 and ring==@ir1)').copy()
#                qry_s1r1['idxcol'] = 's1r1'
#                qry_s1r2 = self.allpolar_work.query('(sector==@is1 and ring==@ir2)').copy()
#                qry_s1r2['idxcol'] = 's1r2'
#                qry_s2r1 = self.allpolar_work.query('(sector==@is2 and ring==@ir1)').copy()
#                qry_s2r1['idxcol'] = 's2r1'
#                qry_s2r2 = self.allpolar_work.query('(sector==@is2 and ring==@ir2)').copy()
#                qry_s2r2['idxcol'] = 's2r2'
#                qry_all = pd.concat([qry_s1r1, qry_s1r2, qry_s2r1, qry_s2r2])
#
#                # --------- Handle chronic concs ------------------------
#                
#                # Organize chronic concs into a pivot table
#                qry_cpivot = pd.pivot_table(qry_all, values='conc', index=['ems_type', 'source_id', 'pollutant'],
#                                                    columns = 'idxcol')
#                qry_cpivot.reset_index(inplace=True)
#                
#                # merge outerblks_inbox with qry_cpivot as one to all
#                outerblks_inbox['key'] = 1
#                qry_cpivot['key'] = 1
#                outerplus = pd.merge(outerblks_inbox, qry_cpivot, on='key').drop('key', axis=1)
#                
#                # interpolate chronic concs
#                a_s1r1 = outerplus['s1r1'].values
#                a_s1r2 = outerplus['s1r2'].values
#                a_s2r1 = outerplus['s2r1'].values
#                a_s2r2 = outerplus['s2r2'].values
#                a_s = outerplus['s'].values
#                a_ringloc = outerplus['ring_loc'].values
#                int_conc = self.interpolate(a_s1r1, a_s1r2, a_s2r1, a_s2r2, a_s, a_ringloc)
#                outerplus['conc'] = int_conc.tolist()
# 
#                    
#                # --------- If necessary, handle acute concs ------------------------
#              
#                if self.acute_yn == 'N':
#                    
#                    outerplus['aconc'] = 0
#                    
#                else:
#                    
#                    # Organize acute concs into a pivot table
#                    qry_apivot = pd.pivot_table(qry_all, values='aconc', index=['ems_type', 'source_id', 'pollutant'],
#                                                        columns = 'idxcol')
#                    qry_apivot.reset_index(inplace=True)
#                    
#                    # merge outerblks_inbox with qry_apivot as one to all
#                    qry_apivot['key'] = 1
#                    outerplus_a = pd.merge(outerblks_inbox, qry_apivot, on='key').drop('key', axis=1)
#                    
#                    # interpolate acute concs
#                    a_s1r1 = outerplus_a['s1r1'].values
#                    a_s1r2 = outerplus_a['s1r2'].values
#                    a_s2r1 = outerplus_a['s2r1'].values
#                    a_s2r2 = outerplus_a['s2r2'].values
#                    a_s = outerplus_a['s'].values
#                    a_ringloc = outerplus_a['ring_loc'].values
#                    int_aconc = self.interpolate(a_s1r1, a_s1r2, a_s2r1, a_s2r2, a_s, a_ringloc)
#                    outerplus_a['aconc'] = int_aconc.tolist()
#                    
#                    # join aconc column to outerplus DF
#                    outerplus = outerplus.join(outerplus_a['aconc'])
#                    
#                datalist = outerplus[['fips', 'block', 'lat', 'lon', 'source_id', 'ems_type',
#                                      'pollutant', 'conc', 'aconc', 'elev', 'population', 'overlap']].values.tolist()
#                dlist.extend(datalist)
#
#                # Finished this box
#                # Check if we need to write a batch and run the analyze function.            
#                if len(dlist) >= self.batchSize:
#                    yield pd.DataFrame(dlist, columns=self.columns)
#                    dlist = []
#
#        # Done. Dataframe to array
#        outerconc_df = pd.DataFrame(dlist, columns=self.columns)
#        self.dataframe = outerconc_df
#        self.data = self.dataframe.values
#        yield self.dataframe
                


    def get4Corners(self, s1, s2, r1, r2, srcid):

        # Initialize output arrays
        cc_s1r1 = np.zeros(len(s1), dtype=float)
        cc_s1r2 = np.zeros(len(s1), dtype=float)
        cc_s2r1 = np.zeros(len(s1), dtype=float)
        cc_s2r2 = np.zeros(len(s1), dtype=float)
        cc_emistype = np.zeros(len(s1), dtype=str)
        
        for i in np.arange(len(s1)):
            cc_s1r1[i] = self.polarconcs['result'].loc[srcid[i]+'s'+str(s1[i])+'r'+str(r1[i])]
            cc_s1r2[i] = self.polarconcs['result'].loc[srcid[i]+'s'+str(s1[i])+'r'+str(r2[i])]
            cc_s2r1[i] = self.polarconcs['result'].loc[srcid[i]+'s'+str(s2[i])+'r'+str(r1[i])]
            cc_s2r2[i] = self.polarconcs['result'].loc[srcid[i]+'s'+str(s2[i])+'r'+str(r2[i])]
            cc_emistype[i] = self.polarconcs['emis_type'].loc[srcid[i]+'s'+str(s2[i])+'r'+str(r2[i])]
            i = i + 1
            
        return cc_s1r1, cc_s1r2, cc_s2r1, cc_s2r2, cc_emistype
    


    def interpolate(self, conc_s1r1, conc_s1r2, conc_s2r1, conc_s2r2, s, ring_loc):
        # Interpolate 4 concentrations to the point defined by (s, ring_loc)
        
        # initialize the output array
        ic = np.zeros(len(conc_s1r1), dtype=float)
        
        for i in np.arange(len(conc_s1r1)):
            
            if conc_s1r1[i] == 0 or conc_s1r2[i] == 0:
                R_s12 = max(conc_s1r1[i], conc_s1r2[i])
            else:
                Lnr_s12 = ((math.log(conc_s1r1[i]) * (int(ring_loc[i])+1-ring_loc[i])) +
                           (math.log(conc_s1r2[i]) * (ring_loc[i]-int(ring_loc[i]))))
                R_s12 = math.exp(Lnr_s12)
    
            if conc_s2r1[i] == 0 or conc_s2r2[i] == 0:
                R_s34 = max(conc_s2r1[i], conc_s2r2[i])
            else:
                Lnr_s34 = ((math.log(conc_s2r1[i]) * (int(ring_loc[i])+1-ring_loc[i])) +
                           (math.log(conc_s2r2[i]) * (ring_loc[i]-int(ring_loc[i]))))
                R_s34 = math.exp(Lnr_s34)
    
            ic[i] = R_s12*(int(s[i])+1-s[i]) + R_s34*(s[i]-int(s[i]))
        
        return ic


    def compute_s1s2r1r2(self, ar_s, ar_r):
        # Define the four surrounding polar sector/rings for each outer block
        
        # Initialize output arrays
        s1 = np.zeros(len(ar_s), dtype=int)
        s2 = np.zeros(len(ar_s), dtype=int)
        r1 = np.zeros(len(ar_s), dtype=int)
        r2 = np.zeros(len(ar_s), dtype=int)
        
        for i in np.arange(len(ar_s)):
            if int(ar_s[i]) == self.model.numsectors:
                s1[i] = self.model.numsectors
                s2[i] = 1
            else:
                s1[i] = int(ar_s[i])
                s2[i] = int(ar_s[i]) + 1
                
            r1[i] = int(ar_r[i])
            if r1[i] == self.model.numrings:
                r1[i] = r1[i] - 1
            r2[i] = int(ar_r[i]) + 1
            if r2[i] > self.model.numrings:
                r2[i] = self.model.numrings
            
        return s1, s2, r1, r2



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
                self.outerAgg = pd.DataFrame(columns=blksumm_cols)
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
            box_receptors_wrisk['inc'] = (box_receptors_wrisk[mir] * box_receptors_wrisk[population])/70
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

    def createDataframe(self):
        # Type setting for CSV reading
        self.numericColumns = [lat, lon, conc, aconc, elev, population]
        self.strColumns = [fips, block, source_id, ems_type, pollutant, overlap]

        df = self.readFromPathCsv(self.getColumns())
        return df.fillna("")