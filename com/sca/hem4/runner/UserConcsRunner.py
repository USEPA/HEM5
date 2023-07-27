import os
import time
import pandas as pd
from com.sca.hem4.writer.csv.AllInnerReceptors import AllInnerReceptors
from com.sca.hem4.writer.csv.AllInnerReceptorsNonCensus import AllInnerReceptorsNonCensus
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.model.Model import *
from datetime import datetime
import polars as pl
from scipy.interpolate import griddata
from com.sca.hem4.writer.csv.BlockSummaryChronic import BlockSummaryChronic
from com.sca.hem4.writer.csv.BlockSummaryChronicNonCensus import BlockSummaryChronicNonCensus
from com.sca.hem4.writer.excel.MaximumIndividualRisksUserconcs import MaximumIndividualRisksUserconcs
from com.sca.hem4.support.UTM import *
import numpy as np

class UserConcsRunner():

    def __init__(self, model, abort):
        self.model = model
        self.abort = abort
        self.start = time.time()
        self.facilityId = "Facility1"
        
        # determine if census or alternate receptors are used
        if 'altrec' not in self.model.dependencies:
            self.altrec = False
        else:
            self.altrec = True
        
        # define the user conc dataframe and determine if it contains acute data
        self.userconcs_df = model.userconcs.dataframe
        if self.userconcs_df['aconc'].sum() > 0:
            self.acuteyn = 'Y'
        else:
            self.acuteyn = 'N'
        
        # Either census or alternate receptors are used. Both are stored as lazyframes.
        if not self.altrec:
            self.census_df = model.census.dataframe
        else:
            self.census_df = model.altreceptr.dataframe


        # Prepare the output folder
        self.fac_folder =  "output/" + self.model.group_name + "/" + self.facilityId + "/"

        if os.path.exists(self.fac_folder):
            pass
        else:
            os.makedirs(self.fac_folder)        
        
    
    def interpolate(self):
        
        ''' Filter user data by pollutant, get block/alternate receptors within extents of user input data,
            interpolate the input data to the block/alternate receptors for each pollutant
            
            NOTE: would need to do this twice if we decide to do acute also
        '''
        
        Logger.logMessage('Interpolating user supplied concentrations...')
        
        self.polls = list(self.userconcs_df['pollutant'].unique())
        pollframes = []
        for poll in self.polls:
            tempuser_df = self.userconcs_df.loc[self.userconcs_df['pollutant'] == poll]
            minlat = tempuser_df['lat'].min()
            maxlat = tempuser_df['lat'].max()
            minlon = tempuser_df['lon'].min()
            maxlon = tempuser_df['lon'].max()
                
            census_filt = self.census_df.filter(
                (pl.col('lat') <= maxlat) & (pl.col('lat') >= minlat) 
                & (pl.col('lon') <= maxlon) & (pl.col('lon') >= minlon)).collect().to_pandas()
            
            x = tempuser_df['lon'].values
            y = tempuser_df['lat'].values
            z = tempuser_df['cconc'].values
                    
            xi = census_filt['lon'].values
            yi = census_filt['lat'].values
            
            zi = griddata((x, y), z, (xi, yi), method='linear') # Using griddata
                        
            census_filt['pollutant'] = poll
            census_filt['cconc'] = zi
            poll_df = census_filt.dropna(subset=['cconc']) # drop blocks with nan conc because outside hull
            pollframes.append(poll_df)            

        self.census_filt = census_filt
        self.all_inner_df = pd.concat(pollframes, ignore_index=True)
    
        Logger.logMessage('Finished interpolation of user supplied concentrations')
        

    def formatDF(self):
        '''
        Format the interpolated All Inner dataframe so that it can be used
        in the output modules. Formatting depends on whether the All Inner dataframe
        represents census data or alternate receptors.
        '''
            
        # Make some column changes
        if not self.altrec:
            # Census
            self.all_inner_df['block'] = self.all_inner_df['blockid']
            self.all_inner_df.drop(['blockid','hill','urban_pop'], axis=1, inplace=True)
        else:
            # Alternate receptors
#TODO Make sure alt recs are using lat/lon and not utm
            self.all_inner_df.drop(['hill','utmzone','location_type'], inplace=True)
        
        # Add some required columns
        self.all_inner_df['source_id'] = 'sourceID'
        self.all_inner_df['emis_type'] = 'C'
        self.all_inner_df['overlap'] = 'N'
        self.all_inner_df['rec_type'] = 'C'
        self.all_inner_df['drydep'] = ''
        self.all_inner_df['wetdep'] = ''
        self.all_inner_df['conc'] = self.all_inner_df['cconc']
        self.all_inner_df.drop('cconc', axis=1, inplace=True)
        
        # Set the column order
        if self.acuteyn == 'N':
            cols = ['fips', 'block', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                    'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
        else:
            cols = ['fips', 'block', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                    'aconc', 'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
        self.all_inner_df = self.all_inner_df[cols]
        
        self.model.all_inner_receptors_df = self.all_inner_df
    
    
    def createOutputs(self):

        success = True

        # Initialize some dataframes needed for output processing
        self.model.outerblks_df = pd.DataFrame()
        self.model.innerblks_df = self.census_filt
        self.model.runstream_hapemis = pd.DataFrame({'pollutant':self.polls})

        # Compute utm coordinates in innerblks_df
        self.model.innerblks_df[['utmn', 'utme', 'uzone', 'hemi', 'epsg']] = \
            (self.model.innerblks_df.apply(lambda row: UTM.ll2utm(row[lat],row[lon]), 
                                       result_type="expand", axis=1))
 
        # Assign a receptor type of C if census, P if census user receptor, S if school, and M if monitor
        if self.altrec == False:
            self.model.innerblks_df['rec_type']=np.where(self.model.innerblks_df['blockid'].str.contains('M'),'M',
                                  np.where(self.model.innerblks_df['blockid'].str.contains('S'),'S',
                                  np.where(self.model.innerblks_df['blockid'].str.contains('U'),'P','C')))
             
        # Write the All_Inner_Receptors file
        allinner = AllInnerReceptorsNonCensus(self.fac_folder, self.facilityId, self.model, None, self.acuteyn) if self.altrec \
                        else AllInnerReceptors(self.fac_folder, self.facilityId, self.model, None, self.acuteyn)
        allinner.write(False, self.model.all_inner_receptors_df)
        Logger.logMessage('Finished creating the All Inner Receptors output file')
        
        # Create and write Block Summary Chronic file
        Logger.logMessage('Creating the Block Summary Chronic output file...')
        block_summary_chronic = BlockSummaryChronicNonCensus(targetDir=self.fac_folder, facilityId=self.facilityId,
                 model=self.model, plot_df=None, outerAgg=None) if self.altrec else \
            BlockSummaryChronic(self.fac_folder, self.facilityId, self.model, None, None)
        block_summary_chronic.write()
        Logger.logMessage('Finished creating the Block Summary Chronic output file')
        
        # Create risk_by_latlon DF because it is need by Maximum Individual Risk
        self.model.risk_by_latlon = block_summary_chronic.dataframe
        
        
        # Create and write Maximum Individual Risk file
        max_indiv_risk = MaximumIndividualRisksUserconcs(self.fac_folder, self.facilityId, self.model) 
        max_indiv_risk.write()
        

        # Did user abort?
        if self.abort.is_set():
            success = False
            return success
        
        return success


