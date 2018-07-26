import os

import pandas as pd

from writer.csv.CsvWriter import CsvWriter

class AllPolarReceptors(CsvWriter):
    """
    Provides the annual average concentration modeled at every census block within the modeling cutoff distance,
    specific to each source ID and pollutant, along with receptor information, and acute concentration (if modeled) and
    wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_polar_receptors.csv")

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """

        self.headers = ["source_id", "emis_type", "pollutant", "conc_ugm3", "distance_m",
                        "angle", "sector_num", "ring_num", "elev_m", "lat", "lon", "overlap"]

        #extract polar concs from plotfile and round the utm coordinates
        polgrid_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
        polgrid_df.utme = polgrid_df.utme.round()
        polgrid_df.utmn = polgrid_df.utmn.round()

        #call creation function
        all_polar_receptors_df = self.create_all_polar_receptors(polgrid_df)
        #dataframe to array
        self.data = all_polar_receptors_df.values

    def create_all_polar_receptors(self, polarplot_df):

        """

        Create the facility specific All Polar Receptor output file.

        This is a CSV formatted file with the following fields:
            source_id
            emis_type
            pollutant
            conc_ug_m3
            distance (m)
            angle
            sector number
            ring number
            elevation (m)
            latitude
            longitude
            overlap (Y/N)

        """
        self.cf = 2000*0.4536/3600/8760

        # array of unique source_id's
        srcids = polarplot_df['source_id'].unique().tolist()

        # process polar concs one source_id at a time
        for x in srcids:
            polarplot_onesrcid = polarplot_df[["utme","utmn","source_id","result"]].loc[polarplot_df['source_id'] == x]
            hapemis_onesrcid = self.model.runstream_hapemis[["source_id","pollutant","emis_tpy"]].loc[self.model.runstream_hapemis['source_id'] == x]
            collist = ["source_id", "emis_type", "pollutant", "conc_ug_m3", "distance", "angle", "sector", "ring_no", "elev", "lat", "lon", "overlap"]
            dlist = []
            for row1 in polarplot_onesrcid.itertuples():
                for row2 in hapemis_onesrcid.itertuples():
                    d_sourceid = row1[3]
                    d_emistype = "C"
                    d_pollutant = row2[2]
                    d_conc = row1[4] * row2[3] * self.cf
                    d_distance = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "distance"].values[0]
                    d_angle = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "angle"].values[0]
                    d_sector = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "sector"].values[0]
                    d_ring_no = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "ring"].values[0]
                    d_elev = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "elev"].values[0]
                    d_lat = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "lat"].values[0]
                    d_lon = self.model.runstream_polar_recs.loc[(self.model.runstream_polar_recs["utme"] == row1[1]) & (self.model.runstream_polar_recs["utmn"] == row1[2]), "lon"].values[0]
                    d_overlap = ""
                    datalist = [d_sourceid, d_emistype, d_pollutant, d_conc, d_distance, d_angle, d_sector, d_ring_no, d_elev, d_lat, d_lon, d_overlap]
                    dlist.append(dict(zip(collist, datalist)))

        polarconc_df = pd.DataFrame(dlist, columns=collist)

        return polarconc_df