import os
import pandas as pd
from writer.csv.CsvWriter import CsvWriter

class AllInnerReceptors(CsvWriter):
    """
    Provides the annual average concentration modeled at every census block within the modeling cutoff distance,
    specific to each source ID and pollutant, along with receptor information, and acute concentration (if modeled) and
    wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_inner_receptors.csv")

        self.innerBlocksCache = {}

    def calculateOutputs(self):
        """
        Compute source and pollutant specific air concentrations at inner receptors.
        """

        self.headers = ['Fips', 'Block', 'Lat', 'Lon', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m2',
                        'Elevation', 'Ddp_g_m2', 'Wdp_g_m2', 'Population', 'Overlap']

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        #extract inner concs from plotfile and round the utm coordinates
        innerplot_df = self.plot_df.query("net_id != 'POLGRID1'").copy()
        innerplot_df.utme = innerplot_df.utme.round()
        innerplot_df.utmn = innerplot_df.utmn.round()

        # create array of unique source_id's
        srcids = innerplot_df['source_id'].unique().tolist()

        dlist = []

        # process inner concs one source_id at a time
        for x in srcids:
            innerplot_onesrcid = innerplot_df[["utme","utmn","source_id","result"]].loc[innerplot_df['source_id'] == x]
            hapemis_onesrcid = self.model.runstream_hapemis[["source_id","pollutant","emis_tpy"]].loc[self.model.runstream_hapemis['source_id'] == x]
            for row1 in innerplot_onesrcid.itertuples():
                for row2 in hapemis_onesrcid.itertuples():

                    record = None
                    key = (row1[1], row1[2])
                    if key in self.innerBlocksCache:
                        record = self.innerBlocksCache.get(key)
                    else:
                        record = self.model.innerblks_df.loc[(self.model.innerblks_df["utme"] == row1[1]) & (self.model.innerblks_df["utmn"] == row1[2])]
                        self.innerBlocksCache[key] = record

                    d_fips = record["FIPS"].values[0]
                    idmarplot = record["IDMARPLOT"].values[0]
                    d_block = idmarplot[-10:]
                    d_lat = record["LAT"].values[0]
                    d_lon = record["LON"].values[0]
                    d_sourceid = row1[3]
                    d_emistype = "C"
                    d_pollutant = row2[2]
                    d_conc = row1[4] * row2[3] * self.cf
                    d_aconc = ""
                    d_elev = record["ELEV"].values[0]
                    d_drydep = ""
                    d_wetdep = ""
                    d_population = record["POPULATION"].values[0]
                    d_overlap = record["overlap"].values[0]
                    datalist = [d_fips, d_block, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc, 
                                d_aconc, d_elev, d_drydep, d_wetdep, d_population, d_overlap]
                    dlist.append(dict(zip(self.headers, datalist)))
                    
        innerconc_df = pd.DataFrame(dlist, columns=self.headers)

        # dataframe to array
        self.data = innerconc_df.values