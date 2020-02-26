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
        # Now do outer receptors...
        # --------------------------------------------------------------------------------------------------
        if self.seasonal:
            self.temporal_outer_df.sort_values(by=[source_id, utme, utmn, seas, hour], inplace=True)
        else:
            self.temporal_outer_df.sort_values(by=[source_id, utme, utmn, hour], inplace=True)

        # copy the emission types from the regular plot_df
        self.temporal_outer_df = self.temporal_outer_df.merge(right=self.plot_df, on=[source_id, utme, utmn, elev, hill])

        polarplot_df = self.temporal_outer_df[new_cols].copy()
        
        # add the new concentration columns, based on user selections
        polarplot_df = pd.concat([innerplot_df, pd.DataFrame(columns=self.conc_cols)])
        polarplot_df.reset_index()
        
        # create array of unique source_id's
        srcids = polarplot_df[source_id].unique().tolist()        
        dlist = []

        iterate over self.model.outerblks_df:
            link blk to
        for x in srcids:
            polarplot_onesrcid = polarplot_df[self.plotcols[self.rtype]].loc[polarplot_df[source_id] == x]
            hapemis_onesrcid = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]] \
                .loc[self.model.runstream_hapemis[source_id] == x]
            for row1 in polarplot_onesrcid.itertuples():
                for row2 in hapemis_onesrcid.itertuples():
        
                    record = None
                    key = (row1.utme, row1.utmn)
                    if key in self.innblkCache:
                        record = self.innblkCache.get(key)
                    else:
                        record = self.model.outerblks_df.loc[(self.model.outerblks_df[utme] == row1[1]) & (self.model.outerblks_df[utmn] == row1[2])]
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
                    d_modeled = 'I'

                    # ring and sector of this outer block
                    # ring_loc = row[19]
                    # cs = row[17]
                    #
                    # # define the four surrounding polar sector/rings for this outer block
                    # s = ((row[14] * self.model.numsectors)/360.0 % self.model.numsectors) + 1
                    #
                    # if int(s) == self.model.numsectors:
                    #     s1 = self.model.numsectors
                    #     s2 = 1
                    # else:
                    #     s1 = int(s)
                    #     s2 = int(s) + 1
                    #
                    # r1 = int(row[19])
                    # if r1 == self.model.numrings:
                    #     r1 = r1 - 1
                    #
                    # r2 = int(row[19]) + 1
                    # if r2 > self.model.numrings:
                    #     r2 = self.model.numrings
                    #
                    # s1r1 = np.logical_and(self.model.all_polar_receptors_df[:, 6] == s1, self.model.all_polar_receptors_df[:,7] == r1 )
                    # s1r2 = np.logical_and(self.model.all_polar_receptors_df[:, 6] == s1, self.model.all_polar_receptors_df[:,7] == r2 )
                    # s2r1 = np.logical_and(self.model.all_polar_receptors_df[:, 6] == s2, self.model.all_polar_receptors_df[:,7] == r1 )
                    # s2r2 = np.logical_and(self.model.all_polar_receptors_df[:, 6] == s2, self.model.all_polar_receptors_df[:,7] == r2 )
                    #
                    # co1 = self.model.all_polar_receptors_df[s1r1]
                    # co2 = self.model.all_polar_receptors_df[s1r2]
                    # co3 = self.model.all_polar_receptors_df[s2r1]
                    # co4 = self.model.all_polar_receptors_df[s2r2]
                    #
                    # # full has polar conc records for the 4 surrounding polar receptors
                    # full = np.concatenate((co1, co2, co3, co4), axis=0)


                    # subset to specific source id and pollutant
                    # sub = full[(full[:,0] == srcpolrow[0]) & (full[:,2] == srcpolrow[1])]
                    #
                    # # polar concs of 4 surrounding polar receptors
                    # concentration = sub[:, 3]
                    #
                    # d_sourceid = srcpolrow[0]
                    # d_pollutant = srcpolrow[1]
                    #
                    # # interpolate
                    # if concentration[0] == 0 or concentration[1] == 0:
                    #     R_s12 = max(concentration[0], concentration[1])
                    # else:
                    #     Lnr_s12 = (math.log(conc[0]) * (int(ring_loc)+1-ring_loc)) + (math.log(concentration[1]) * (ring_loc-int(ring_loc)))
                    #     R_s12 = math.exp(Lnr_s12)
                    #
                    # if concentration[2] == 0 or concentration[3] == 0:
                    #     R_s34 = max(concentration[2], concentration[3] )
                    # else:
                    #     Lnr_s34 = (math.log(concentration[2]) * (int(ring_loc)+1-ring_loc)) + (math.log(concentration[3] ) * (ring_loc-int(ring_loc)))
                    #     R_s34 = math.exp(Lnr_s34)

                    d_concs = []
                    records_to_avg = int(96 / len(self.conc_cols))
                    recs = innerplot_df.loc[(innerplot_df[utme] == row1[1]) & (innerplot_df[utmn] == row1[2])]

                    column = 0
                    for c in self.conc_cols:
                        offset = int(column * records_to_avg)
                        values = recs[conc].values[offset:offset+records_to_avg]
                        average = sum(values) / records_to_avg

                        d_concs.append(average * row2.emis_tpy * self.cf) # R_s12*(int(cs)+1-cs) + R_s34*(cs-int(cs)
                        column+= 1


        datalist = [d_fips, d_block, d_population, d_lat, d_lon, d_pollutant, d_emistype, d_overlap, d_modeled]
        datalist.extend(d_concs)

        dlist.append(datalist)
        outerconc_df = pd.DataFrame(dlist, columns=self.headers)

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