import os, fnmatch
import pandas as pd

from com.sca.hem4.writer.csv.AllOuterReceptors import AllOuterReceptors
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.upload.HAPEmissions import *
from com.sca.hem4.upload.FacilityList import *
from com.sca.hem4.upload.DoseResponse import *
from com.sca.hem4.upload.UserReceptors import *
from com.sca.hem4.model.Model import *
from com.sca.hem4.support.UTM import *
from com.sca.hem4.FacilityPrep import *
from com.sca.hem4.writer.csv.AllInnerReceptors import *
import traceback

notes = 'notes';
aconc_sci = 'aconc_sci';

class AcuteChemicalPopulated(ExcelWriter, InputFile):
    """
    Provides the maximum acute concentration for each modeled pollutant occurring at a populated(census block or
    user-defined) receptor, the acute benchmarks associated with each pollutant, and other max receptor
    information.
    """

    def __init__(self, targetDir=None, facilityId=None, model=None, plot_df=None, filenameOverride=None,
                 createDataframe=False):
        # Initialization for file reading/writing. If no file name override, use the
        # default construction.
        filename = facilityId + "_acute_chem_pop.xlsx" if filenameOverride is None else filenameOverride
        path = os.path.join(targetDir, filename)

        ExcelWriter.__init__(self, model, plot_df)
        InputFile.__init__(self, path, createDataframe)

        self.filename = path
        self.targetDir = targetDir
         

    def getHeader(self):
        return ['Pollutant', 'Conc (µg/m3)', 'Conc sci (µg/m3)', 'Aegl_1 1hr (mg/m3)',
                'Aegl_2 1hr (mg/m3)', 'Erpg_1 (mg/m3)', 'Erpg_2 (mg/m3)',
                'Acute Rel (mg/m3)', 'Population',
                'Distance (in meters)', 'Angle (from north)', 'Elevation (in meters)', 'Hill Height (in meters)',
                'Fips', 'Block', 'Utm easting', 'Utm northing', 'Latitude', 'Longitude', 'Receptor type', 'Notes']

    def getColumns(self):
        return [pollutant, aconc, aconc_sci, aegl_1_1h,aegl_2_1h,erpg_1,erpg_2,
                rel, population, distance, angle, elev, hill, fips, block,
                utme, utmn, lat, lon, rec_type, notes]

    def generateOutputs(self):

        try:
                        
            # Set-up a dataframe to hold the running max conc for each pollutant along with location of the receptor
            pols = self.model.runstream_hapemis[pollutant].str.lower().unique().tolist()
            cols = [aconc, lon, lat, notes]
            fillval = [0, 0, 0, '']
            filler = [fillval for p in pols]
            maxconc_df = pd.DataFrame(data=filler, index=pols, columns=cols)
            
            # dataframe of pollutants with their acute benchmarks
            polinfo_cols = [pollutant, aegl_1_1h, aegl_2_1h, erpg_1, erpg_2, rel]
            polinfo = self.model.haplib.dataframe[polinfo_cols][
                      self.model.haplib.dataframe[pollutant].str.lower().isin([x.lower() for x in pols])]
            polinfo[pollutant] = polinfo.apply(lambda x: x[pollutant].lower(), axis=1)
            polinfo.set_index([pollutant], inplace=True, drop=False)
            
            # Define aggregation columns and new column names
            aggs = {'blkid':'first', pollutant:'first', lat:'first', lon:'first', 
                    population:'first', overlap:'first', rec_type:'first', aconc:'sum'}
            newcolumns = ['blkid', pollutant, lat, lon, population, overlap, rec_type, aconc]
            
            # 1) First search the discrete (inner) receptors for the max acute conc per pollutant
            #    Note: population at receptor must be > 0 or receptor must be a user receptor
            #    to be considered
            
            if self.model.all_inner_receptors_df.empty == False:
                inner_df = self.model.all_inner_receptors_df.copy()
                inner_df['blkid'] = inner_df['fips'] + inner_df['block']
                # Sum acute conc to unique lat/lons
                innsum = inner_df.groupby([pollutant, lat, lon]).agg(aggs)[newcolumns]
                        
                # loop over each pollutant and find the discrete receptor with the max acute conc
                for x in pols:
                    if innsum[((innsum[pollutant].str.lower() == x)
                                           & ((innsum[population] > 0) |
                                              (innsum[rec_type] == 'P'))
                                           & (innsum[overlap] == 'N'))].empty == False:
                
                        max_idx = innsum[((innsum[pollutant].str.lower() == x)
                                           & ((innsum[population] > 0) |
                                              (innsum[rec_type] == 'P')))][aconc].idxmax()
                        # Overlap?
                        if innsum[overlap].loc[max_idx] == 'N':
                            maxconc_df.loc[x, aconc] = innsum[aconc].loc[max_idx]
                            maxconc_df.loc[x, lon] = innsum[lon].loc[max_idx]
                            maxconc_df.loc[x, lat] = innsum[lat].loc[max_idx]
                            maxconc_df.loc[x, notes] = 'Discrete'
                        else:
                            max_idx = innsum[((innsum[pollutant].str.lower() == x)
                                           & ((innsum[population] > 0) |
                                              (innsum[rec_type] == 'P'))
                                           & (innsum[overlap] == 'N'))][aconc].idxmax()
                            maxconc_df.loc[x, aconc] = innsum[aconc].loc[max_idx]
                            maxconc_df.loc[x, lon] = innsum[lon].loc[max_idx]
                            maxconc_df.loc[x, lat] = innsum[lat].loc[max_idx]
                            maxconc_df.loc[x, notes] = 'Discrete overlapped source. Next highest discrete.'
                
                    else:
                        
                        maxconc_df.loc[x, aconc] = 0
                        maxconc_df.loc[x, lon] = 0
                        maxconc_df.loc[x, lat] = 0
                        maxconc_df.loc[x, notes] = 'No max acute value for this pollutant'
                             
            # 2) Next, search the outer receptor concs
            
            if not self.model.outerblks_df.empty:
                
                outercolumns = [fips, block, lat, lon, source_id, emis_type, pollutant, conc, 
                                aconc, elev, population, overlap]
                
                # Get a list of the all_outer_receptor files (could be more than one)
                listOuter = []
                listDirfiles = os.listdir(self.targetDir)
                pattern = "*_all_outer_receptors*.csv"
                for entry in listDirfiles:
                    if fnmatch.fnmatch(entry, pattern):
                        listOuter.append(entry)
                 
                # Loop over each pollutant and outer receptor file and see if max acute conc
                # is larger than the stored value
                for f in listOuter:
                    allouter = AllOuterReceptors(targetDir=self.targetDir, filenameOverride=f)
                    outer_df = allouter.createDataframe()
                    outer_df['blkid'] = outer_df['fips'] + outer_df['block']
                    # Sum to unique lat/lons
                    outsum = outer_df.groupby([pollutant, lat, lon]).agg(aggs)[newcolumns]
        
                    for p in pols:
                        if outsum[((outsum[pollutant].str.lower() == p)
                                           & ((outsum[population] > 0) |
                                              (outsum[rec_type] == 'P')))].empty == False:
                    
                            max_idx = outsum[((outsum[pollutant].str.lower() == p)
                                               & ((outsum[population] > 0) |
                                                  (outsum[rec_type] == 'P')))][aconc].idxmax()
                            # Overlap?
                            if outsum[overlap].loc[max_idx] == 'Y':
                                # Look for next highest with no overlap
                                max_idx = outsum[((outsum[pollutant].str.lower() == p)
                                                & ((outsum[population] > 0) |
                                                  (outsum[rec_type] == 'P'))
                                                & (outsum[overlap] == 'N'))][aconc].idxmax()
                                noteTxt = 'Interpolated overlapped source. Next highest interpolated.'
                            else:
                                noteTxt = 'Interpolated'
        
                            # Compare to stored value                        
                            if outsum[aconc].loc[max_idx] > maxconc_df[aconc].loc[p]:
                                maxconc_df.loc[p, aconc] = outsum[aconc].loc[max_idx]
                                maxconc_df.loc[p, lon] = outsum[lon].loc[max_idx]
                                maxconc_df.loc[p, lat] = outsum[lat].loc[max_idx]
                                maxconc_df.loc[p, notes] = noteTxt
            
            # 3) Build output dataframe
            acute_df = polinfo.join(maxconc_df, how='inner')
            acute_df[aconc_sci] = acute_df.apply(lambda x: format(x[aconc], ".1e"), axis=1)
            acute_df[elev] = 0
            acute_df[hill] = 0
            acute_df[distance] = 0
            acute_df[angle] = 0
            acute_df[population] = 0
            acute_df[utme] = 0
            acute_df[utmn] = 0
            acute_df[fips] = ''
            acute_df[block] = ''
                   
            for index, row in acute_df.iterrows():
                if row[notes].split(" ")[0] == 'Interpolated':
                    acute_df.at[index,elev] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), elev].values[0]
                    acute_df.at[index,hill] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), hill].values[0]
                    acute_df.at[index,population] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), population].values[0]
                    acute_df.at[index,distance] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), distance].values[0]
                    acute_df.at[index,angle] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), angle].values[0]
                    acute_df.at[index,utmn] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lon] == row[lon]), utmn].values[0]
                    acute_df.at[index,utme] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), utme].values[0]
                    acute_df.at[index,fips] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), fips].values[0]
                    acute_df.at[index,block] = self.model.outerblks_df[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat])]['blockid'].values[0][-10:]
                    acute_df.at[index,rec_type] = self.model.outerblks_df.loc[(self.model.outerblks_df[lon] == row[lon]) & 
                                                   (self.model.outerblks_df[lat] == row[lat]), rec_type].values[0]
                elif row[notes].split(" ")[0] == 'Discrete':
                    acute_df.at[index,elev] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), elev].values[0]
                    acute_df.at[index,hill] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), hill].values[0]
                    acute_df.at[index,population] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), population].values[0]
                    acute_df.at[index,distance] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), distance].values[0]
                    acute_df.at[index,angle] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), angle].values[0]
                    acute_df.at[index,utmn] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lon] == row[lon]), utmn].values[0]
                    acute_df.at[index,utme] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), utme].values[0]
                    acute_df.at[index,fips] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), fips].values[0]
                    acute_df.at[index,block] = self.model.innerblks_df[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat])]['blockid'].values[0][-10:]
                    acute_df.at[index,rec_type] = self.model.innerblks_df.loc[(self.model.innerblks_df[lon] == row[lon]) & 
                                                   (self.model.innerblks_df[lat] == row[lat]), rec_type].values[0]

                else:
                    acute_df.at[index,elev] = 0
                    acute_df.at[index,hill] = 0
                    acute_df.at[index,population] = 0
                    acute_df.at[index,distance] = 0
                    acute_df.at[index,angle] = 0
                    acute_df.at[index,utmn] = 0
                    acute_df.at[index,utme] = 0
                    acute_df.at[index,rec_id] = ''
                    acute_df.at[index,rec_type] = ''
            
            cols = self.getColumns()
            acute_df = acute_df[cols]
                    
            self.dataframe = acute_df
            self.data = self.dataframe.values
            yield self.dataframe

        except BaseException as e:
        
            var = traceback.format_exc()
            Logger.logMessage(var)
        

    def compute_s1s2r1r2(self, row):
        # define the four surrounding polar sector/rings for this outer block
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
        return pd.Series((s1, s2, r1, r2))
    
    
    def assign_sr(self, row):
        # assign a sector and ring number to a utm coordinate
        record = self.model.polargrid.loc[(self.model.polargrid[utme] == row[utme]) & (self.model.polargrid[utmn] == row[utmn])]
        sector_num = record.iloc[0][sector]
        ring_num = record.iloc[0][ring]
        return pd.Series((sector_num, ring_num))

    def createDataframe(self):
        # Type setting for XLS reading
        self.numericColumns = [aconc, aconc_sci, aegl_1_1h,aegl_2_1h,erpg_1,erpg_2,rel,
                               population, distance, angle, elev, hill, utme, utmn, lat, lon]
        self.strColumns = [pollutant, fips, block, rec_type, notes]

        df = self.readFromPath(self.getColumns())
        return df.fillna("")

        