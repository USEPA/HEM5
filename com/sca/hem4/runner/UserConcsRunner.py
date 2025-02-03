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
from com.sca.hem4.writer.excel.CancerRiskExposure import CancerRiskExposure
from com.sca.hem4.writer.excel.NoncancerRiskExposure import NoncancerRiskExposure
from com.sca.hem4.writer.excel.Incidence import Incidence
from com.sca.hem4.writer.excel.AcuteChemicalPopulated import AcuteChemicalPopulated
from com.sca.hem4.writer.excel.AcuteChemicalPopulatedNonCensus import AcuteChemicalPopulatedNonCensus
from com.sca.hem4.writer.excel.AcuteChemicalMax import AcuteChemicalMax
from com.sca.hem4.writer.excel.AcuteChemicalMaxNonCensus import AcuteChemicalMaxNonCensus
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
        
        # Set the rec_type of the user concs as C
        self.userconcs_df['rec_type'] = 'C'
        
        
        # Either census or alternate receptors are used. Both are stored as lazyframes.
        # Note that whether census or alternate receptors are used to interpolate to, the
        # dataframe is called "census".
        if not self.altrec:
            # U.S. Census
            self.census_df = model.census.dataframe.collect()
        else:
            # Alternate Receptors
            self.census_df = model.altreceptr.dataframe.collect()
                        
            # If any alternate receptors are in UTM coordinates, convert to lat/lon.
            # Also prefix the receptor ID with ALT
            altrec_df = self.census_df.to_pandas()
            altrec_df[[lat, lon]] = altrec_df.apply(lambda row: UTM.utm2ll(row[lat],row[lon],row[utmzone]) 
                                       if row['location_type']=='U' else [row[lat],row[lon]], result_type="expand", axis=1)
            altrec_df['rec_id'] = 'ALT' + altrec_df['rec_id'].astype(str)
            self.census_df = pl.from_pandas(altrec_df)
         
        
        # Prepare the output folder
        self.fac_folder =  "output/" + self.model.group_name + "/" + self.facilityId + "/"

        if os.path.exists(self.fac_folder):
            pass
        else:
            os.makedirs(self.fac_folder)        
        
    
    def interpolate(self):
        
        ''' 
        Filter user data by pollutant, get block/alternate receptors within extents of user input data,
        interpolate the input data to the block/alternate receptors for each pollutant.
        
        Note that the user supplied receptors with their concentrations are included in the
        resulting dataframe. This allows risk to be computed at those receptors.          
        '''
        
        Logger.logMessage('\nInterpolating user supplied concentrations...')

        # If interpolating to census, then rename user conc column "rec_id" to "blockid"
        # and set a FIPS column. If interpolating to Alt Receptors, prefix the user conc
        # receptor ID with "UCONC" for easier identification.
        if not self.altrec:
            self.userconcs_df.rename(columns={'rec_id': 'blockid'}, inplace=True)
            self.userconcs_df['fips'] = 'UCONC'
        else:
            self.userconcs_df['rec_id'] = 'UCONC' + self.userconcs_df['rec_id'].astype(str)

        
        self.polls = list(self.userconcs_df['pollutant'].unique())
        
        #----------------------------------------------------------------
        # If the user concs and census have any duplicate lat/lons, then
        # do not include user concs in the all_inner.
        #----------------------------------------------------------------
        
        census_pandas_df = self.census_df.collect()
        duplicates = pd.merge(census_pandas_df, self.userconcs_df, on=['lat', 'lon'], how="inner")
        if len(duplicates) == 0:
            # no dups
            pollframes = [self.userconcs_df]
        else:
            # there are dups
            pollframes = []
            
        for poll in self.polls:
            tempuser_df = self.userconcs_df.loc[self.userconcs_df['pollutant'] == poll]
            minlat = tempuser_df['lat'].min()
            maxlat = tempuser_df['lat'].max()
            minlon = tempuser_df['lon'].min()
            maxlon = tempuser_df['lon'].max()
                
            census_filt = self.census_df.filter(
                (pl.col('lat') <= maxlat) & (pl.col('lat') >= minlat) 
                & (pl.col('lon') <= maxlon) & (pl.col('lon') >= minlon)).to_pandas()
            
            x = tempuser_df['lon'].values
            y = tempuser_df['lat'].values
            zc = tempuser_df['cconc'].values
            za = tempuser_df['aconc'].values

            xi = census_filt['lon'].values
            yi = census_filt['lat'].values
            
            zic = griddata((x, y), zc, (xi, yi), method='linear')
            zia = griddata((x, y), za, (xi, yi), method='linear') 
                        
            census_filt['pollutant'] = poll
            census_filt['cconc'] = zic
            census_filt['aconc'] = zia
            poll_df = census_filt.dropna(subset=['cconc','aconc']) # drop blocks with nan conc because outside hull
            
            # If census used, assign a receptor type of C if census, P if census user receptor, S if school, and M if monitor.
            # If alternate receptors used, assign receptor type as C.
            if self.altrec == False:
                poll_df['rec_type']=np.where(poll_df['blockid'].str.contains('M'),'M',
                                      np.where(poll_df['blockid'].str.contains('S'),'S',
                                      np.where(poll_df['blockid'].str.contains('U'),'P','C')))
            else:
                poll_df['rec_type'] = 'C'
            
            pollframes.append(poll_df)            

        self.all_inner_df = pd.concat(pollframes, ignore_index=True)
        
        # Use one of the filtered census DF's to represent the census data
        self.census_filt = census_filt
                        
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
            self.all_inner_df.drop(['hill','utmzone','location_type'], axis=1, inplace=True)
        
        # Add some required columns
        self.all_inner_df['source_id'] = 'sourceID'
        self.all_inner_df['emis_type'] = 'C'
        self.all_inner_df['overlap'] = 'N'
        self.all_inner_df['drydep'] = ''
        self.all_inner_df['wetdep'] = ''
        self.all_inner_df['conc'] = self.all_inner_df['cconc']
        self.all_inner_df.drop('cconc', axis=1, inplace=True)
        
        # Replace NaN with 0 in certain columns
        self.all_inner_df[['population', 'elev']] = \
                                self.all_inner_df[['population', 'elev']].fillna(0)
        
        # Set the column order
        if self.altrec == False:
            if self.acuteyn == 'N':
                cols = ['fips', 'block', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                        'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
            else:
                cols = ['fips', 'block', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                        'aconc', 'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
        else:
            if self.acuteyn == 'N':
                cols = ['rec_id', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                        'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
            else:
                cols = ['rec_id', 'lat', 'lon', 'source_id', 'emis_type', 'pollutant', 'conc',
                        'aconc', 'elev', 'drydep', 'wetdep', 'population', 'overlap', 'rec_type']
                      
        self.all_inner_df = self.all_inner_df[cols]
        self.model.all_inner_receptors_df = self.all_inner_df
    
    
    def createOutputs(self):

        success = True

        # Initialize some dataframes needed for output processing
        self.model.outerblks_df = pd.DataFrame()
        self.model.runstream_hapemis = pd.DataFrame({'pollutant':self.polls})
        self.model.all_polar_receptors_df = pd.DataFrame({'pollutant':self.polls,
                                                          'lat':0.0, 'lon':0.0, 'aconc':0.0}) 
        
        # Create a unique list of lat/lons/hill from the user receptors and interpolated to receptors.
        # This DF is needed in the Block Summary Chronic module.
        self.model.innerblks_df = pd.concat([self.census_filt, self.userconcs_df], ignore_index=True)
        self.model.innerblks_df = self.model.innerblks_df.drop_duplicates(subset=['lat', 'lon'])        
        self.model.innerblks_df['distance'] = ''
        self.model.innerblks_df['angle'] = ''
        self.model.innerblks_df[['population', 'elev', 'hill']] = \
                    self.model.innerblks_df[['population', 'elev', 'hill']].fillna(0)
        
        # Compute utm coordinates in innerblks_df
        self.model.innerblks_df[['utmn', 'utme', 'uzone', 'hemi', 'epsg']] = \
            (self.model.innerblks_df.apply(lambda row: UTM.ll2utm(row[lat],row[lon]), 
                                       result_type="expand", axis=1))
 
        # Assign a receptor type of C if census, P if census user receptor, S if school, and M if monitor
        if self.altrec == False:
            self.model.innerblks_df['rec_type']=np.where(self.model.innerblks_df['blockid'].str.contains('M'),'M',
                                  np.where(self.model.innerblks_df['blockid'].str.contains('S'),'S',
                                  np.where(self.model.innerblks_df['blockid'].str.contains('U'),'P','C')))
             
        #---------- All_Inner_Receptors file --------------------------------
        Logger.logMessage('\nCreating the All Inner Receptors output file...')
        allinner = AllInnerReceptorsNonCensus(self.fac_folder, self.facilityId, self.model, None, self.acuteyn) if self.altrec \
                        else AllInnerReceptors(self.fac_folder, self.facilityId, self.model, None, self.acuteyn)
        allinner.write(False, self.model.all_inner_receptors_df)
        Logger.logMessage('Finished creating the All Inner Receptors output file')
        
        #---------- Block Summary Chronic file ------------------------------
        Logger.logMessage('\nCreating the Block Summary Chronic output file...')
        block_summary_chronic = BlockSummaryChronicNonCensus(targetDir=self.fac_folder, facilityId=self.facilityId,
                 model=self.model, plot_df=None, outerAgg=None) if self.altrec else \
            BlockSummaryChronic(self.fac_folder, self.facilityId, self.model, None, None)
        block_summary_chronic.write()
        self.model.block_summary_chronic_df = block_summary_chronic.dataframe
        Logger.logMessage('Finished creating the Block Summary Chronic output file')

        
        # Create risk_by_latlon DF because it is need by Maximum Individual Risk
        self.model.risk_by_latlon = block_summary_chronic.dataframe
                
        #------------ Maximum Individual Risk file ---------------------------
        Logger.logMessage('\nCreating the Maximum Individual Risk output file...')
        max_indiv_risk = MaximumIndividualRisksUserconcs(self.fac_folder, self.facilityId, 
                                                         self.model, self.altrec) 
        max_indiv_risk.write()
        Logger.logMessage('Finished creating the Maximum Individual Risk output file')
        

        #------------ Cancer Risk Exposure file ---------------------------
        Logger.logMessage('\nCreating the Cancer Risk Exposure output file...')
        cancer_risk_exposure = CancerRiskExposure(self.fac_folder, self.facilityId, 
                                                  self.model, None, self.model.block_summary_chronic_df)
        cancer_risk_exposure.write()
        Logger.logMessage('Finished creating the Cancer Risk Exposure output file')
        

        #------------ Noncancer Risk Exposure file ---------------------------
        Logger.logMessage('\nCreating the Noncancer Risk Exposure output file...')
        noncancer_risk_exposure = NoncancerRiskExposure(self.fac_folder, self.facilityId, 
                                                        self.model, None, self.model.block_summary_chronic_df)
        noncancer_risk_exposure.write()
        Logger.logMessage('Finished creating the Noncancer Risk Exposure output file')


        #------------ Incidence file ---------------------------
        Logger.logMessage('\nCreating the Incidence output file...')
        incidence= Incidence(self.fac_folder, self.facilityId, self.model, None, None)        
        incidence.write()
        Logger.logMessage('Finished creating the Incidence output file')


        #------------ Acute Chem Pop file ---------------------------
        if self.acuteyn == 'Y':
            
            Logger.logMessage('\nCreating the Acute Chemical Populated output file...')
            acutechempop = AcuteChemicalPopulatedNonCensus(self.fac_folder, self.facilityId, self.model) if self.altrec \
                 else AcuteChemicalPopulated(self.fac_folder, self.facilityId, self.model)
            acutechempop.write()
            Logger.logMessage('Finished creating the Acute Chemical Populated output file')

            Logger.logMessage('\nCreating the Acute Chemical Max output file...')
            acutechemmax = AcuteChemicalMaxNonCensus(self.fac_folder, self.facilityId, self.model) if self.altrec \
                 else AcuteChemicalMax(self.fac_folder, self.facilityId, self.model)
            acutechemmax.write()
            Logger.logMessage('Finished creating the Acute Chemical Max output file')


        # Did user abort?
        if self.abort.is_set():
            success = False
            return success
        
        return success


