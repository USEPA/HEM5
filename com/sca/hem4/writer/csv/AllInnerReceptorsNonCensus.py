from com.sca.hem4.CensusBlocks import *
from com.sca.hem4.writer.csv.AllInnerReceptors import aresult, adry, awet
from com.sca.hem4.writer.csv.CsvWriter import CsvWriter
from com.sca.hem4.upload.HAPEmissions import *
from com.sca.hem4.FacilityPrep import *
import os

emis_type = 'emis_type';
block = 'block';
drydep = 'drydep';
wetdep = 'wetdep';
aconc = 'aconc';
aresult = 'aresult';

class AllInnerReceptorsNonCensus(CsvWriter, InputFile):
    """
    Provides the annual average concentration modeled at every census block within the modeling cutoff distance,
    specific to each source ID and pollutant, along with receptor information, and acute concentration (if modeled) and
    wet and dry deposition flux (if modeled). Notably though, this module does NOT include FIPs and block information
    that is only present when using census data. This corresponds to a "user receptors only" scenario.
    """

    def __init__(self, targetDir=None, facilityId=None, model=None, plot_df=None, acuteyn=None,
                 filenameOverride=None, createDataframe=False):
        # Initialization for CSV reading/writing. If no file name override, use the
        # default construction.
        self.targetDir = targetDir
        filename = facilityId + "_all_inner_receptors.csv" if filenameOverride is None else filenameOverride
        path = os.path.join(self.targetDir, filename)

        CsvWriter.__init__(self, model, plot_df)
        InputFile.__init__(self, path, createDataframe)

        self.innerBlocksCache = {}
        self.filename = path
        self.acute_yn = acuteyn
        

    def getHeader(self):
        if self.acute_yn == 'Y':
            return ['Receptor ID', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                    'Conc (µg/m3)', 'Acute Conc (µg/m3)', 'Elevation (m)',
                    'Dry deposition (g/m2/yr)', 'Wet deposition (g/m2/yr)', 'Population', 'Overlap',
                    'Receptor Type']
        else:
            return ['Receptor ID', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                    'Conc (µg/m3)', 'Elevation (m)',
                    'Dry deposition (g/m2/yr)', 'Wet deposition (g/m2/yr)', 'Population', 'Overlap',
                    'Receptor Type']
            

    def getColumns(self):
        if self.acute_yn == 'N':
            return [rec_id, lat, lon, source_id, emis_type, pollutant, conc,
                    elev, drydep, wetdep, population, overlap, rec_type]
        else:
            return [rec_id, lat, lon, source_id, emis_type, pollutant, conc, aconc,
                    elev, drydep, wetdep, population, overlap, rec_type]


    def generateOutputs(self):
        """
        Compute source and pollutant specific air concentrations at inner receptors.
        """

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        # Aermod runtype (with or without deposition) determines what columns are in the aermod plotfile.
        # Set accordingly in a dictionary.
        self.rtype = self.model.model_optns['runtype']
        self.plotcols = {0: [utme,utmn,source_id,result,aresult,emis_type]}
        self.plotcols[1] = [utme,utmn,source_id,result,ddp,wdp,aresult,emis_type]
        self.plotcols[2] = [utme,utmn,source_id,result,ddp,aresult,emis_type]
        self.plotcols[3] = [utme,utmn,source_id,result,wdp,aresult,emis_type]


        # Extract Chronic inner concs from Chronic plotfile and round the utm coordinates
        innercplot_df = self.plot_df.query("net_id != 'POLGRID1'").copy()
        innercplot_df.utme = innercplot_df.utme.round()
        innercplot_df.utmn = innercplot_df.utmn.round()

        # If acute was run for this facility, extract inner concs from acute plotfile and join to
        # Chronic inner concs.
        # Otherwise, add column of 0's for acute result
        if self.acute_yn == 'Y':
            inneraplot_df = self.model.acuteplot_df.query("net_id != 'POLGRID1'").copy()
            inneraplot_df.utme = inneraplot_df.utme.round()
            inneraplot_df.utmn = inneraplot_df.utmn.round()
            innerplot_df = pd.merge(innercplot_df, inneraplot_df[[emis_type, source_id, utme, utmn, aresult]], 
                                    how='inner', on = [emis_type, source_id, utme, utmn])
        else:
            innerplot_df = innercplot_df.copy()
            innerplot_df[aresult] = 0

        # create array of unique source_id's
        srcids = innerplot_df[source_id].unique().tolist()

        dlist = []
        col_list = self.getColumns()

        # process inner concs one source_id at a time
        for x in srcids:
            innerplot_onesrcid = innerplot_df[self.plotcols[self.rtype]].loc[innerplot_df[source_id] == x]
            hapemis_onesrcid = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]].loc[self.model.runstream_hapemis[source_id] == x]
            for row1 in innerplot_onesrcid.itertuples():
                for row2 in hapemis_onesrcid.itertuples():

                    record = None
                    key = (row1[1], row1[2])
                    if key in self.innerBlocksCache:
                        record = self.innerBlocksCache.get(key)
                    else:
                        record = self.model.innerblks_df.loc[(self.model.innerblks_df[utme] == row1[1]) & (self.model.innerblks_df[utmn] == row1[2])]
                        self.innerBlocksCache[key] = record

                    d_rectype = record[rec_type].values[0]
                    d_recid = record[rec_id].values[0]
                    d_lat = record[lat].values[0]
                    d_lon = record[lon].values[0]
                    d_sourceid = row1.source_id
                    d_pollutant = row2.pollutant
                    d_elev = record[elev].values[0]
                    d_population = record[population].values[0]
                    d_overlap = record[overlap].values[0]
                    d_emistype = row1.emis_type
                    if d_emistype == 'C':
                        d_conc = row1.result * row2.emis_tpy * self.cf
                        d_aconc = row1.aresult * row2.emis_tpy * self.cf * self.model.facops.iloc[0][multiplier]
                        d_drydep = "" if self.rtype in [0,3] else row1.ddp * row2.emis_tpy * self.cf
                        d_wetdep = "" if self.rtype in [0,2] else row1.wdp * row2.emis_tpy * self.cf
                    elif d_emistype == 'P':
                        d_conc = row1.result * row2.emis_tpy * self.cf * row2.part_frac
                        d_aconc = row1.aresult * row2.emis_tpy * self.cf * self.model.facops.iloc[0][multiplier] \
                                                * row2.part_frac
                        d_drydep = "" if self.rtype in [0,3] else row1.ddp * row2.emis_tpy * self.cf * row2.part_frac
                        d_wetdep = "" if self.rtype in [0,2] else row1.wdp * row2.emis_tpy * self.cf * row2.part_frac
                    else:
                        d_conc = row1.result * row2.emis_tpy * self.cf * (1 - row2.part_frac)
                        d_aconc = row1.aresult * row2.emis_tpy * self.cf * self.model.facops.iloc[0][multiplier] \
                                                * (1 - row2.part_frac)
                        d_drydep = "" if self.rtype in [0,3] else row1.ddp * row2.emis_tpy * self.cf * (1 - row2.part_frac)
                        d_wetdep = "" if self.rtype in [0,2] else row1.wdp * row2.emis_tpy * self.cf * (1 - row2.part_frac)
                    
                    if self.acute_yn == 'N':
                        datalist = [d_recid, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc,
                                    d_elev, d_drydep, d_wetdep, d_population, d_overlap, d_rectype]
                    else:
                        datalist = [d_recid, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc,
                                    d_aconc, d_elev, d_drydep, d_wetdep, d_population, d_overlap, d_rectype]
                        
                    dlist.append(dict(zip(col_list, datalist)))

        innerconc_df = pd.DataFrame(dlist, columns=col_list)

        # dataframe to array
        self.dataframe = innerconc_df
        self.data = self.dataframe.values
        yield self.dataframe


    def createDataframe(self):
        # Type setting for CSV reading
        if self.acute_yn == 'N':
            self.numericColumns = [lat, lon, conc, elev, drydep, wetdep, population]
        else:
            self.numericColumns = [lat, lon, conc, aconc, elev, drydep, wetdep, population]

        self.strColumns = [rec_id, source_id, emis_type, pollutant, overlap, rec_type]

        df = self.readFromPathCsv(self.getColumns())
        return df.fillna("")        