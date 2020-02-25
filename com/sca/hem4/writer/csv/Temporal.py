import os
import pandas as pd

from com.sca.hem4.CensusBlocks import *
from com.sca.hem4.writer.csv.AllInnerReceptors import *
from com.sca.hem4.writer.csv.CsvWriter import CsvWriter

modeled = 'modeled'
nhrs = 'nhrs'
seas = 'seas'
hour = 'hour'
timeblk = 'timeblk'
class Temporal(CsvWriter):
    """
    Provides the annual average pollutant concentrations at different time periods (depending on the temporal option
    chosen) for all pollutants and receptors.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.fac_dir = targetDir
        self.filename = os.path.join(targetDir, facilityId + "_temporal.csv")

        # initialize cache for inner census block data
        self.innblkCache = {}

        self.rtype = model.model_optns['runtype']
        self.resolution = 12 # should come from model.facops or similar...
        self.seasonal = 'N' # again, needs to come from model opts

        self.temporal_inner_df = None
        self.temporal_outer_df = None

    def getHeader(self):
        defaultHeader = ['Fips', 'Block', 'Population', 'Lat', 'Lon', 'Pollutant', 'Emis_type', 'Overlap', 'Modeled']
        return self.extendsCols(defaultHeader)

    def getColumns(self):
        defaulsCols = [fips, block, population, lat, lon, pollutant, emis_type, overlap, modeled]
        return self.extendsCols(defaulsCols)

    def extendsCols(self, default):
        n_seas = 4 if self.seasonal == 'Y' else 1
        n_hrblk = round(24/self.resolution)
        concCols = n_seas * n_hrblk

        self.conc_cols = []
        for c in range(1, concCols+1):
            colnum = str(c)
            if len(colnum) < 2:
                colnum = "0" + colnum
            colName = "C_" + colnum
            self.conc_cols.append(colName)

        default.extend(self.conc_cols)
        return default

    def generateOutputs(self):

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        # Aermod runtype (with or without deposition) determines what columns are in the aermod plotfile.
        # Set accordingly in a dictionary.
        self.rtype = self.model.model_optns['runtype']
        self.plotcols = {0: [utme,utmn,source_id,conc, emis_type],
                         1: [utme,utmn,source_id,conc,ddp,wdp, emis_type],
                         2: [utme,utmn,source_id,conc,ddp, emis_type],
                         3: [utme,utmn,source_id,conc,wdp, emis_type]}
        
        # Open up the temporal plot file and set up both inner and outer slices
        pfile = open(self.fac_dir + '/seasonhr.plt', "r")
        self.readPlotfile(pfile)

        # sort by receptor, season?, hour
        if self.seasonal:
            self.temporal_inner_df.sort_values(by=[source_id, utme, utmn, seas, hour], inplace=True)
        else:
            self.temporal_inner_df.sort_values(by=[source_id, utme, utmn, hour], inplace=True)

        # copy the emission types from the regular plot_df
        self.temporal_inner_df = self.temporal_inner_df.merge(right=self.plot_df, on=[source_id, utme, utmn, elev, hill])

        new_cols = [utme, utmn, elev, hill, source_id, conc, emis_type]
        innerplot_df = self.temporal_inner_df[new_cols].copy()

        # add the new concentration columns, based on user selections
        innerplot_df = pd.concat([innerplot_df, pd.DataFrame(columns=self.conc_cols)])
        innerplot_df.reset_index()

        # create array of unique source_id's
        srcids = innerplot_df[source_id].unique().tolist()

        # --------------------------------------------------------------------------------------------------
        # Start the algorithm for inner receptors...this is a slight variant of the logic found in AllInnerReceptors.
        # --------------------------------------------------------------------------------------------------
        dlist = []
        col_list = self.getColumns()

        # process inner concs one source_id at a time
        for x in srcids:
            innerplot_onesrcid = innerplot_df[self.plotcols[self.rtype]].loc[innerplot_df[source_id] == x]
            hapemis_onesrcid = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]] \
                .loc[self.model.runstream_hapemis[source_id] == x]
            for row1 in innerplot_onesrcid.itertuples():
                for row2 in hapemis_onesrcid.itertuples():

                    record = None
                    key = (row1.utme, row1.utmn)
                    if key in self.innblkCache:
                        record = self.innblkCache.get(key)
                    else:
                        record = self.model.innerblks_df.loc[(self.model.innerblks_df[utme] == row1[1]) & (self.model.innerblks_df[utmn] == row1[2])]
                        self.innblkCache[key] = record

                    d_fips = record[fips].values[0]
                    d_idmarplot = record[idmarplot].values[0]
                    d_block = d_idmarplot[-10:]
                    d_lat = record[lat].values[0]
                    d_lon = record[lon].values[0]
                    d_pollutant = row2.pollutant
                    d_population = record[population].values[0]
                    d_overlap = record[overlap].values[0]
                    d_emistype = row1.emis_type
                    d_modeled = 'D'

                    d_concs = []
                    records_to_avg = int(96 / len(self.conc_cols))
                    recs = innerplot_df.loc[(innerplot_df[utme] == row1[1]) & (innerplot_df[utmn] == row1[2])]

                    column = 0
                    for c in self.conc_cols:
                        offset = int(column * records_to_avg)
                        values = recs[conc].values[offset:offset+records_to_avg]
                        average = sum(values) / records_to_avg

                        if d_emistype == 'C':
                            d_concs.append(average * row2.emis_tpy * self.cf)
                        elif d_emistype == 'P':
                            d_concs.append(average * row2.emis_tpy * self.cf * row2.part_frac)
                        else:
                            d_concs.append(average * row2.emis_tpy * self.cf * (1 - row2.part_frac))
                        column+= 1

                    datalist = [d_fips, d_block, d_population, d_lat, d_lon, d_pollutant, d_emistype, d_overlap, d_modeled]
                    datalist.extend(d_concs)

                    dlist.append(dict(zip(col_list, datalist)))

        innerconc_df = pd.DataFrame(dlist, columns=col_list)

        # --------------------------------------------------------------------------------------------------
        # Now do outer receptors...this is a slight variant of the logic found in AllOuterReceptors.
        # --------------------------------------------------------------------------------------------------

        # sort by receptor, season?, hour
        if self.seasonal:
            self.temporal_outer_df.sort_values(by=[source_id, utme, utmn, seas, hour], inplace=True)
        else:
            self.temporal_outer_df.sort_values(by=[source_id, utme, utmn, hour], inplace=True)

        # copy the emission types from the regular plot_df
        self.temporal_outer_df = self.temporal_outer_df.merge(right=self.plot_df, on=[source_id, utme, utmn, elev, hill])

        polarplot_df = self.temporal_outer_df

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

        #subset outer blocks DF to needed columns and sort by increasing distance
        outerblks_subset = self.model.outerblks_df[[fips, idmarplot, lat, lon, elev,
                                                    'distance', 'angle', population, overlap,
                                                    's', 'ring_loc']].copy()
        outerblks_subset['block'] = outerblks_subset['idmarplot'].str[5:]
        outerblks_subset.sort_values(by=['distance'], axis=0, inplace=True)

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
        outerblks_subset2 = pd.merge(outerblks_subset, srcid_df, on=['key'])

        # Get the 4 surrounding polar Aermod concs of each outer receptor
        cs1r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','conc','emis_type']],
                         how='left', left_on=['s1','r1','source_id'],
                         right_on=['sector','ring','source_id'])
        cs1r1.rename(columns={"conc":"result_s1r1"}, inplace=True)
        cs1r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','conc']],
                         how='left', left_on=['s1','r2','source_id'],
                         right_on=['sector','ring','source_id'])
        cs1r2.rename(columns={"conc":"result_s1r2"}, inplace=True)
        cs2r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','conc']],
                         how='left', left_on=['s2','r1','source_id'],
                         right_on=['sector','ring','source_id'])
        cs2r1.rename(columns={"conc":"result_s2r1"}, inplace=True)
        cs2r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','conc']],
                         how='left', left_on=['s2','r2','source_id'],
                         right_on=['sector','ring','source_id'])
        cs2r2.rename(columns={"conc":"result_s2r2"}, inplace=True)

        outer4interp = cs1r1.copy()
        outer4interp['result_s1r2'] = cs1r2['result_s1r2']
        outer4interp['result_s2r1'] = cs2r1['result_s2r1']
        outer4interp['result_s2r2'] = cs2r2['result_s2r2']

        # Interpolate polar Aermod concs to each outer receptor; store results in arrays
        a_ccs1r1 = outer4interp['result_s1r1'].values
        a_ccs1r2 = outer4interp['result_s1r2'].values
        a_ccs2r1 = outer4interp['result_s2r1'].values
        a_ccs2r2 = outer4interp['result_s2r2'].values
        a_sectfrac = outer4interp['s'].values
        a_ringfrac = outer4interp['ring_loc'].values
        a_intconc = self.interpolate(a_ccs1r1, a_ccs1r2, a_ccs2r1, a_ccs2r2, a_sectfrac, a_ringfrac)

        #   Apply emissions to interpolated outer concs and write

        outerconcs = outer4interp[['fips', 'block', 'lat', 'lon', 'elev', 'population', 'overlap',
                                   'emis_type', 'source_id']]
        outerconcs['intconc'] = a_intconc

        num_rows_outer_recs = outerblks_subset.shape[0]
        num_rows_hapemis = self.model.runstream_hapemis.shape[0]
        num_rows_output = num_rows_outer_recs * num_rows_hapemis
        num_srcids = len(srcids)

        #  Write no more than 14,000,000 rows to a given CSV output file
        if num_rows_output <= 14000000:

            # One output file

            outer_polconcs = pd.merge(outerconcs, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                      on=[source_id])

            if 'C' in outer_polconcs['emis_type'].values:
                d_concs = []
                records_to_avg = int(96 / len(self.conc_cols))
                recs = polarplot_df.loc[(polarplot_df[utme] == row1[1]) & (innerplot_df[utmn] == row1[2])]

                column = 0
                for c in self.conc_cols:
                    offset = int(column * records_to_avg)
                    values = recs[conc].values[offset:offset+records_to_avg]
                    average = sum(values) / records_to_avg
                    d_concs.append(average * row2.emis_tpy * self.cf)
                    column+= 1
                outer_polconcs['conc'] = d_concs

            else:
                outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']

                p_concs = []
                v_concs = []
                for c in self.conc_cols:
                    p_concs.append(outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                   * outer_polconcs_p['part_frac'] * self.cf)
                    v_concs.append(outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                   * ( 1 - outer_polconcs_v['part_frac']) * self.cf)
                outer_polconcs_p['conc'] = p_concs
                outer_polconcs_v['conc'] = v_concs
                outer_polconcs = outer_polconcs_p.append(outer_polconcs_v, ignore_index=True)

            outerconc_df = outer_polconcs[col_list]

        else:

            # Multiple output files

            # compute the number of CSV files (batches) to output and number of rows from outerconcs to use in
            # each batch.
            num_batches = int(round(num_rows_output/14000000))
            num_outerconc_rows_per_batch = int(round(14000000 / num_rows_hapemis)) * num_srcids

            for k in range(num_batches):
                start = k * num_outerconc_rows_per_batch
                end = start + num_outerconc_rows_per_batch
                outerconcs_batch = outerconcs[start:end]
                outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]],
                                          on=[source_id])

                if 'C' in outer_polconcs['emis_type'].values:
                    d_concs = []
                    for c in self.conc_cols:
                        d_concs.append(outer_polconcs['intconc'] * outer_polconcs['emis_tpy'] * self.cf)
                    outer_polconcs['conc'] = d_concs

                else:
                    outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                    outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']

                    p_concs = []
                    v_concs = []
                    for c in self.conc_cols:
                        p_concs.append(outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                       * outer_polconcs_p['part_frac'] * self.cf)
                        v_concs.append(outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf)
                    outer_polconcs_p['conc'] = p_concs
                    outer_polconcs_v['conc'] = v_concs
                    outer_polconcs = outer_polconcs_p.append(outer_polconcs_v, ignore_index=True)

                outerconc_df = outer_polconcs[col_list]

            # Last batch
            outerconcs_batch = outerconcs[end:]
            outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]],
                                      on=[source_id])

            if 'C' in outer_polconcs['emis_type'].values:
                d_concs = []
                for c in self.conc_cols:
                    d_concs.append(outer_polconcs['intconc'] * outer_polconcs['emis_tpy'] * self.cf)
                outer_polconcs['conc'] = d_concs

            else:
                outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']

                p_concs = []
                v_concs = []
                for c in self.conc_cols:
                    p_concs.append(outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                   * outer_polconcs_p['part_frac'] * self.cf)
                    v_concs.append(outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                   * ( 1 - outer_polconcs_v['part_frac']) * self.cf)
                outer_polconcs_p['conc'] = p_concs
                outer_polconcs_v['conc'] = v_concs
                outer_polconcs = outer_polconcs_p.append(outer_polconcs_v, ignore_index=True)

            outerconc_df = outer_polconcs[col_list]

        self.dataframe = innerconc_df.append(outerconc_df)
        self.data = self.dataframe.values
        yield self.dataframe

    def readPlotfile(self, pfile):
        columns = [0,1,2,3,4,5,6,7,8,9,10]
        colnames = [utme,utmn,conc,elev,hill,flag,source_id,nhrs,seas,hour,net_id]
        type_converters = {utme:np.float64,utmn:np.float64,conc:np.float64,elev:np.float64,hill:np.float64,
            flag:np.float64,source_id:np.str,nhrs:np.int64,seas:np.int64,hour:np.int64,net_id:np.str}

        if self.rtype == 1:
            # Wet and dry dep
            columns.append(11)
            columns.append(12)
            colnames.insert(3, drydep)
            colnames.insert(4, wetdep)
            type_converters[drydep] = np.float64
            type_converters[wetdep] = np.float64
        elif self.rtype == 2:
            # Dry only
            columns.append(11)
            colnames.insert(3, drydep)
            type_converters[drydep] = np.float64
        elif self.rtype == 3:
            # Wet only
            columns.append(11)
            colnames.insert(3, wetdep)
            type_converters[wetdep] = np.float64

        plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, names=colnames, usecols=columns,
             converters=type_converters, comment='*')

        plot_df.utme = plot_df.utme.round()
        plot_df.utmn = plot_df.utmn.round()

        # Extract Chronic inner concs from temporal plotfile and round the utm coordinates
        self.temporal_inner_df = plot_df.query("net_id != 'POLGRID1'").copy()
        self.temporal_outer_df = plot_df.query("net_id == 'POLGRID1'").copy()

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