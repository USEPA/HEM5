import math
import re
import operator

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
rec_type = 'rec_type';


class AllOuterReceptorsNonCensus(CsvWriter, InputFile):
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


        # No need to go further if we are instantiating this class to read in a CSV file...
        if self.model is None:
            return


        self.outerblocks = self.model.outerblks_df[[lat, lon, utme, utmn, hill, rec_type]]
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
        self.srcpols = self.model.all_polar_receptors_df[[source_id, pollutant, 'emis_type']].drop_duplicates().values.tolist()
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
        
        # Compute a recipricol of the rfc for easier computation of HIs
        self.haplib_df = self.model.haplib.dataframe
        self.haplib_df['invrfc'] = self.haplib_df.apply(lambda x: 1/x['rfc'] if x['rfc']>0 else 0.0, axis=1)

        # Local copy of target organs and combine target organ columns into one list column
        self.organs_df = self.model.organs.dataframe
        self.organs_df['organ_list'] = (self.organs_df[['resp','liver','neuro','dev','reprod','kidney',
                        'ocular','endoc','hemato','immune','skeletal','spleen','thyroid','wholebod']]
                        .values.tolist())

        # List of HI target organ endpoints
        self.hi_list = [hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                        hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
        
    def getHeader(self):
        if self.acute_yn == 'N':
            return ['Receptor ID', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                    'Conc (µg/m3)', 'Elevation (m)',
                    'Population', 'Overlap', 'Receptor Type']
        else:
            return ['Receptor ID', 'Latitude', 'Longitude', 'Source ID', 'Emission type', 'Pollutant',
                    'Conc (µg/m3)', 'Acute Conc (µg/m3)', 'Elevation (m)',
                    'Population', 'Overlap', 'Receptor Type']
            

    def getColumns(self):
        if self.acute_yn == 'N':
            return [rec_id, lat, lon, source_id, 'emis_type', pollutant, conc, elev, population
                    , overlap, rec_type]
        else:
            return [rec_id, lat, lon, source_id, 'emis_type', pollutant, conc, aconc
                    , elev, population, overlap, rec_type]
            
    def generateOutputs(self):
        """
        Interpolate polar pollutant concs to outer receptors.
        """
        
        if not self.outerblocks.empty:
            
            # Units conversion factor
            self.cf = 2000*0.4536/3600/8760
    
            # Runtype (with or without deposition) determines what columns are in the aermod plotfile.
            self.rtype = self.model.model_optns['runtype']
                        
            # Was acute run? If not, this is chronic only.
            if self.acute_yn == 'N':
                            
                #-------- Chronic only ------------------------------------
    
                #extract Chronic polar concs from the Chronic plotfile and round the utm coordinates
                polarplot_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
                polarplot_df.utme = polarplot_df.utme.round()
                polarplot_df.utmn = polarplot_df.utmn.round()
    
                # Assign sector and ring to polar concs from polarplot_df and set an index
                # of source_id + sector + ring
                self.polarconcs = pd.merge(polarplot_df, self.model.polargrid[['utme', 'utmn', 'sector', 'ring']], 
                                     how='inner', on=['utme', 'utmn'])
                # self.polarconcs['newindex'] = self.polarconcs['source_id'] \
                #                                 + 's' + self.polarconcs['sector'].apply(str) \
                #                                 + 'r' + self.polarconcs['ring'].apply(str)
                # self.polarconcs.set_index(['newindex'], inplace=True)
                
                # QA - make sure merge retained all rows
                if self.polarconcs.shape[0] != polarplot_df.shape[0]:
                    raise ValueError(""""Error! self.polarconcs has wrong number 
                                     of rows in AllOuterReceptors""")
                   
                #subset outer blocks DF to needed columns and sort by increasing distance
                outerblks_subset = self.model.outerblks_df[[rec_id, lat, lon, elev,
                                                            'distance', 'angle', population, overlap,
                                                            's', 'ring_loc', 'rec_type']].copy()
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
                cs1r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result','emis_type']],
                                 how='left', left_on=['s1','r1','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs1r1.rename(columns={"result":"result_s1r1"}, inplace=True)
                cs1r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result']],
                                 how='left', left_on=['s1','r2','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs1r2.rename(columns={"result":"result_s1r2"}, inplace=True)
                cs2r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result']],
                                 how='left', left_on=['s2','r1','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs2r1.rename(columns={"result":"result_s2r1"}, inplace=True)
                cs2r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result']],
                                 how='left', left_on=['s2','r2','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs2r2.rename(columns={"result":"result_s2r2"}, inplace=True)
        
                outer4interp = cs1r1.copy()
                outer4interp['result_s1r2'] = cs1r2['result_s1r2']
                outer4interp['result_s2r1'] = cs2r1['result_s2r1']
                outer4interp['result_s2r2'] = cs2r2['result_s2r2']
                 
                # Interpolate polar Aermod concs to each outer receptor; store results in arrays
                toInterp_df = outer4interp[[rec_id,'source_id','emis_type','result_s1r1'
                                            ,'result_s1r2','result_s2r1','result_s2r2'
                                            ,'s','ring_loc']].copy()
                toInterp_df.rename({'result_s1r1':'conc_s1r1','result_s1r2':'conc_s1r2'
                                    ,'result_s2r1':'conc_s2r1','result_s2r2':'conc_s2r2'}
                                   ,axis=1, inplace=True)
                interpolated_df = self.interpolate(toInterp_df)
                outerconcs = outer4interp[[rec_id, 'lat', 'lon', 'elev', 'population', 'overlap',
                                        'emis_type', 'source_id', 'rec_type']].copy()
                outerconcs = pd.merge(outerconcs, interpolated_df[[rec_id,'source_id','emis_type','intconc']]
                                      , on=[rec_id,'source_id','emis_type'], how='inner')

                # QA - make sure merge retained all rows
                if outerconcs.shape[0] != interpolated_df.shape[0]:
                    raise ValueError(""""Error! outerconcs has wrong number of 
                                     rows in AllOuterReceptors""")
                
    
                #   Apply emissions to interpolated outer concs and write
                num_rows_outer_recs = outerblks_subset.shape[0]
                num_polls_in_hapemis = self.model.runstream_hapemis[pollutant].nunique()
                num_rows_hapemis = self.model.runstream_hapemis.shape[0]
                num_rows_output = num_rows_outer_recs * num_rows_hapemis
                num_srcids = len(srcids)
         
                col_list = self.getColumns()
         
               
                #  Write no more than 10,000,000 rows to a given CSV output file
                
                if num_rows_output <= self.batchSize:
                    
                    # One output file
                                    
                    outer_polconcs = pd.merge(outerconcs, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                        on=[source_id])
                    
                    if 'C' in outer_polconcs['emis_type'].values:
                        outer_polconcs['conc'] = outer_polconcs['intconc'] * outer_polconcs['emis_tpy'] * self.cf
    
                    else:
                        outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P'].copy()
                        outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V'].copy()
                        outer_polconcs_p['conc'] = outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_v['conc'] = outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
         
                    self.dataframe = outer_polconcs[col_list]
                    self.data = self.dataframe.values
                    yield self.dataframe
                    
                else:
         
                    # Multiple output files
                    
                    # compute the number of CSV files (batches) to output and number of rows from outerconcs to use in 
                    # each batch.
                    num_batches = math.ceil(num_rows_output/self.batchSize)
                    num_outerconc_rows_per_batch = int(round(self.batchSize / num_rows_hapemis)) * num_srcids
                                    
                    for k in range(num_batches-1):
                        start = k * num_outerconc_rows_per_batch
                        end = start + num_outerconc_rows_per_batch
                        outerconcs_batch = outerconcs[start:end]
                        outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                            on=[source_id])
    
                        if 'C' in outer_polconcs['emis_type'].values:
                            outer_polconcs['conc'] = outer_polconcs['intconc'] * outer_polconcs['emis_tpy'] * self.cf
        
                        else:
                            outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                            outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']
                            outer_polconcs_p['conc'] = outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                                           * outer_polconcs_p['part_frac'] * self.cf
                            outer_polconcs_v['conc'] = outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                                           * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                            outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
                            
    
                        self.dataframe = outer_polconcs[col_list]
                        self.data = self.dataframe.values
                        yield self.dataframe
                    
                    # Last batch
                    outerconcs_batch = outerconcs[end:]
                    outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                        on=[source_id])
    
                    if 'C' in outer_polconcs['emis_type'].values:
                        outer_polconcs['conc'] = outer_polconcs['intconc'] * outer_polconcs['emis_tpy'] * self.cf
    
                    else:
                        outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                        outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']
                        outer_polconcs_p['conc'] = outer_polconcs_p['intconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_v['conc'] = outer_polconcs_v['intconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
    
                    self.dataframe = outer_polconcs[col_list]
                    self.data = self.dataframe.values
                    yield self.dataframe
                
                
            else:
                
                # Acute
                                
                #extract Chronic polar concs from the Chronic plotfile and round the utm coordinates
                polarcplot_df = self.plot_df.query("net_id == 'POLGRID1'").copy()
                polarcplot_df.utme = polarcplot_df.utme.round()
                polarcplot_df.utmn = polarcplot_df.utmn.round()
    
                # extract polar concs from Acute plotfile and join to chronic polar concs
                polaraplot_df = self.model.acuteplot_df.query("net_id == 'POLGRID1'").copy()
                polaraplot_df.utme = polaraplot_df.utme.round()
                polaraplot_df.utmn = polaraplot_df.utmn.round()
                polarplot_df = pd.merge(polarcplot_df, polaraplot_df[['emis_type', source_id, utme, utmn, aresult]], 
                                        how='inner', on = ['emis_type', source_id, utme, utmn])
    
                # Assign sector and ring to polar concs from polarplot_df and set an index
                # of source_id + sector + ring
                self.polarconcs = pd.merge(polarplot_df, self.model.polargrid[['utme', 'utmn', 'sector', 'ring']], 
                                     how='inner', on=['utme', 'utmn'])
                # self.polarconcs['newindex'] = self.polarconcs['source_id'] \
                #                                 + 's' + self.polarconcs['sector'].apply(str) \
                #                                 + 'r' + self.polarconcs['ring'].apply(str)
                # self.polarconcs.set_index(['newindex'], inplace=True)
                
                # QA - make sure merge retained all rows
                if self.polarconcs.shape[0] != polarplot_df.shape[0]:
                    raise ValueError(""""Error! self.polarconcs has wrong number 
                                     of rows in AllOuterReceptors""")
        
                #subset outer blocks DF to needed columns and sort by increasing distance
                outerblks_subset = self.model.outerblks_df[[rec_id, lat, lon, elev,
                                                            'distance', 'angle', population, overlap,
                                                            's', 'ring_loc', 'rec_type']].copy()
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
                cs1r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result','aresult','emis_type']],
                                 how='left', left_on=['s1','r1','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs1r1.rename(columns={"result":"result_s1r1", "aresult":"aresult_s1r1"}, inplace=True)
                cs1r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result','aresult']],
                                 how='left', left_on=['s1','r2','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs1r2.rename(columns={"result":"result_s1r2", "aresult":"aresult_s1r2"}, inplace=True)
                cs2r1 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result','aresult']],
                                 how='left', left_on=['s2','r1','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs2r1.rename(columns={"result":"result_s2r1", "aresult":"aresult_s2r1"}, inplace=True)
                cs2r2 = pd.merge(outerblks_subset2, self.polarconcs[['sector','ring','source_id','result','aresult']],
                                 how='left', left_on=['s2','r2','source_id'],
                                 right_on=['sector','ring','source_id'])
                cs2r2.rename(columns={"result":"result_s2r2", "aresult":"aresult_s2r2"}, inplace=True)
    
                outer4interp = cs1r1.copy()
                outer4interp['result_s1r2'] = cs1r2['result_s1r2']
                outer4interp['result_s2r1'] = cs2r1['result_s2r1']
                outer4interp['result_s2r2'] = cs2r2['result_s2r2']
                outer4interp['aresult_s1r2'] = cs1r2['aresult_s1r2']
                outer4interp['aresult_s2r1'] = cs2r1['aresult_s2r1']
                outer4interp['aresult_s2r2'] = cs2r2['aresult_s2r2']
            
                #.... Interpolate polar Aermod concs to each outer receptor ......
                                
                # first do chronic conc
                toInterp_df = outer4interp[[rec_id,'source_id','result_s1r1','result_s1r2'
                                    ,'result_s2r1','result_s2r2','s','ring_loc']].copy()
                toInterp_df.rename({'result_s1r1':'conc_s1r1','result_s1r2':'conc_s1r2'
                                    ,'result_s2r1':'conc_s2r1','result_s2r2':'conc_s2r2'}
                                   ,axis=1, inplace=True)
                interpolated_df = self.interpolate(toInterp_df)
                outerconcs = outer4interp[[rec_id, 'lat', 'lon', 'elev', 'population', 'overlap',
                                        'emis_type', 'source_id', 'rec_type']].copy()
                outerconcs = pd.merge(outerconcs, interpolated_df[[rec_id,'source_id','intconc']]
                                      , on=[rec_id,'source_id'], how='inner')
                outerconcs.rename({'intconc':'intcconc'}, axis=1, inplace=True)
                # QA - make sure merge retained all rows
                if outerconcs.shape[0] != interpolated_df.shape[0]:
                    raise ValueError("""Error! Chronic outerconcs has wrong number 
                                     of rows for Acute in AllOuterReceptors""")
                    #TODO stop this facility

               
                # next do acute conc
                
                toInterp_df = outer4interp[[rec_id,'source_id','aresult_s1r1','aresult_s1r2'
                                    ,'aresult_s2r1','aresult_s2r2','s','ring_loc']].copy()
                toInterp_df.rename({'aresult_s1r1':'conc_s1r1','aresult_s1r2':'conc_s1r2'
                                    ,'aresult_s2r1':'conc_s2r1','aresult_s2r2':'conc_s2r2'}
                                   ,axis=1, inplace=True)
                interpolated_df = self.interpolate(toInterp_df)
                outerconcs = pd.merge(outerconcs, interpolated_df[[rec_id,'source_id','intconc']]
                                      , on=[rec_id,'source_id'], how='inner')
                outerconcs.rename({'intconc':'intaconc'}, axis=1, inplace=True)
                # QA - make sure merge retained all rows
                if outerconcs.shape[0] != toInterp_df.shape[0]:
                    raise ValueError("""Error! Acute outerconcs has wrong number 
                                     of rows for Acute in AllOuterReceptors""")
                
                
                #   Apply emissions to interpolated outer concs and write
                                
                num_rows_outer_recs = outerblks_subset.shape[0]
                num_polls_in_hapemis = self.model.runstream_hapemis[pollutant].nunique()
                num_rows_hapemis = self.model.runstream_hapemis.shape[0]
                num_rows_output = num_rows_outer_recs * num_rows_hapemis
                num_srcids = len(srcids)
         
                col_list = self.getColumns()
              
                # Write no more than 10,000,000 rows to a given CSV output file
                                
                if num_rows_output <= self.batchSize:
                    
                    # One output file
                    
                    outer_polconcs = pd.merge(outerconcs, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                        on=[source_id])
                
                    if 'C' in outer_polconcs['emis_type'].values:
                        outer_polconcs['conc'] = outer_polconcs['intcconc'] * outer_polconcs['emis_tpy'] * self.cf
                        outer_polconcs['aconc'] = outer_polconcs['intaconc'] * outer_polconcs['emis_tpy'] \
                                                  * self.cf * self.model.facops.iloc[0][multiplier]
     
                    else:
                        outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                        outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']
                        outer_polconcs_p['conc'] = outer_polconcs_p['intcconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_p['aconc'] = outer_polconcs_p['intaconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_v['conc'] = outer_polconcs_v['intcconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs_v['aconc'] = outer_polconcs_v['intaconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
    
                    self.dataframe = outer_polconcs[col_list]
                    self.data = self.dataframe.values
                    yield self.dataframe
                
                else:
                    
                    # Multiple output files
     
                    # compute the number of CSV files (batches) to output and number of rows from outerconcs to use in 
                    # each batch.
                    num_batches = math.ceil(num_rows_output/self.batchSize)
                    num_outerconc_rows_per_batch = int(round(self.batchSize / num_rows_hapemis)) * num_srcids
                                    
                    for k in range(num_batches-1):
                        start = k * num_outerconc_rows_per_batch
                        end = start + num_outerconc_rows_per_batch
                        outerconcs_batch = outerconcs[start:end]
                        outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                            on=[source_id])
                        if 'C' in outer_polconcs['emis_type'].values:
                            outer_polconcs['conc'] = outer_polconcs['intcconc'] * outer_polconcs['emis_tpy'] * self.cf
                            outer_polconcs['aconc'] = outer_polconcs['intaconc'] * outer_polconcs['emis_tpy'] \
                                                      * self.cf * self.model.facops.iloc[0][multiplier]
         
                        else:
                            outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                            outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']
                            outer_polconcs_p['conc'] = outer_polconcs_p['intcconc'] * outer_polconcs_p['emis_tpy'] \
                                                           * outer_polconcs_p['part_frac'] * self.cf
                            outer_polconcs_p['aconc'] = outer_polconcs_p['intaconc'] * outer_polconcs_p['emis_tpy'] \
                                                           * outer_polconcs_p['part_frac'] * self.cf
                            outer_polconcs_v['conc'] = outer_polconcs_v['intcconc'] * outer_polconcs_v['emis_tpy'] \
                                                           * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                            outer_polconcs_v['aconc'] = outer_polconcs_v['intaconc'] * outer_polconcs_v['emis_tpy'] \
                                                           * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                            outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
    
                        self.dataframe = outer_polconcs[col_list]
                        self.data = self.dataframe.values
                        yield self.dataframe
                    
                    # Last batch
                    outerconcs_batch = outerconcs[end:]
                    outer_polconcs = pd.merge(outerconcs_batch, self.model.runstream_hapemis[[source_id,pollutant,emis_tpy,part_frac]],
                                        on=[source_id])
    
                    if 'C' in outer_polconcs['emis_type'].values:
                        outer_polconcs['conc'] = outer_polconcs['intcconc'] * outer_polconcs['emis_tpy'] * self.cf
                        outer_polconcs['aconc'] = outer_polconcs['intaconc'] * outer_polconcs['emis_tpy'] \
                                                  * self.cf * self.model.facops.iloc[0][multiplier]
     
                    else:
                        outer_polconcs_p = outer_polconcs[outer_polconcs['emis_type']=='P']
                        outer_polconcs_v = outer_polconcs[outer_polconcs['emis_type']=='V']
                        outer_polconcs_p['conc'] = outer_polconcs_p['intcconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_p['aconc'] = outer_polconcs_p['intaconc'] * outer_polconcs_p['emis_tpy'] \
                                                       * outer_polconcs_p['part_frac'] * self.cf
                        outer_polconcs_v['conc'] = outer_polconcs_v['intcconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs_v['aconc'] = outer_polconcs_v['intaconc'] * outer_polconcs_v['emis_tpy'] \
                                                       * ( 1 - outer_polconcs_v['part_frac']) * self.cf
                        outer_polconcs = pd.concat([outer_polconcs_p, outer_polconcs_v], ignore_index=True)
    
                    self.dataframe = outer_polconcs[col_list]
                    self.data = self.dataframe.values
                    yield self.dataframe

        else:
            
            # No outer blocks to process. Return empty dataframes

            blksumm_cols = [lat, lon, overlap, elev, rec_id, utme, utmn, hill, population,
                            mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                            hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
            self.outerAgg = pd.DataFrame(columns=blksumm_cols)
            
            col_list = self.getColumns()
            self.dataframe = pd.DataFrame(columns=col_list)
               


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
    


    def interpolate(self, interpDF):
        # Interpolate 4 concentrations to the point defined by (s, ring_loc)
         
        nozeros_df = interpDF[(interpDF['conc_s1r1'] > 0) & (interpDF['conc_s1r2'] > 0)
                              & (interpDF['conc_s2r1'] > 0) & (interpDF['conc_s2r2'] > 0)].copy()

        # Identify rows in interpDF where at least one polar conc is 0, but not all 4
        somezeros_df = interpDF[ ~interpDF.index.isin(nozeros_df.index) ].copy()
         
        # Ensure that nozeros and somezeros sum to interpDF
        if interpDF.shape[0] != nozeros_df.shape[0] + somezeros_df.shape[0]:
            raise ValueError("""Error! nozeros and somezeros dataframes do not 
                             sum to interpDF dataframe in AllOuterReceptors""")

         
        #--- Interpolate outer blocks where all 4 polars are non-zero ---      
        conc_s1r1 = nozeros_df['conc_s1r1'].to_numpy()
        conc_s1r2 = nozeros_df['conc_s1r2'].to_numpy()
        conc_s2r1 = nozeros_df['conc_s2r1'].to_numpy()
        conc_s2r2 = nozeros_df['conc_s2r2'].to_numpy()
        ring_loc = nozeros_df['ring_loc'].to_numpy()
        s = nozeros_df['s'].to_numpy()
        
        R_s12 = np.exp((np.log(conc_s1r1) * (ring_loc.astype(int)+1-ring_loc)) +
                       (np.log(conc_s1r2) * (ring_loc-ring_loc.astype(int))))
        
        R_s34 = np.exp((np.log(conc_s2r1) * (ring_loc.astype(int)+1-ring_loc)) +
                       (np.log(conc_s2r2) * (ring_loc-ring_loc.astype(int))))
        
        ic_array = R_s12*(s.astype(int)+1-s) + R_s34*(s-s.astype(int))
        
        nozeros_df['intconc'] = ic_array


        if somezeros_df.shape[0] == 0:
            
            conc_df = nozeros_df.copy()
            
        else:
            
            #---Interpolate outer blocks where at least one of the 4 polars is zero ---
            
            # Find max of s1r1,s1r2 and s2r1,s2r2. These are used for 0 cases.
            somezeros_df['R_s12'] = somezeros_df[['conc_s1r1','conc_s1r2']].max(axis=1)
            somezeros_df['R_s34'] = somezeros_df[['conc_s2r1','conc_s2r2']].max(axis=1)
            
            
            # In order to vectorize operations, split somezeros_df into three DFs
            # zeroS1 => s1r1=0 or s1r2=0 so R_s12 is max of s1r1, s1r2
            # zeroS2 => s2r1=0 or s2r2=0 so R_s34 is max of s2r1, s2r2
            # zeroS12 => s1r1=0 or s1r2=0 AND s2r1=0 or s2r2=0, R_s12=max(s1r1,s1r2) R_s34=max(s2r1,s2r2)
            zeroS1 = somezeros_df[((somezeros_df['conc_s1r1']==0) | (somezeros_df['conc_s1r2']==0))
                                    & ((somezeros_df['conc_s2r1']>0) & (somezeros_df['conc_s2r2']>0))].copy()
            zeroS2 = somezeros_df[((somezeros_df['conc_s1r1']>0) & (somezeros_df['conc_s1r2']>0))
                                    & ((somezeros_df['conc_s2r1']==0) | (somezeros_df['conc_s2r2']==0))].copy()
            zeroS12 = somezeros_df[(somezeros_df[['conc_s1r1','conc_s1r2']].min(axis=1) == 0) & 
                                   (somezeros_df[['conc_s2r1','conc_s2r2']].min(axis=1)==0)]
            
    
            zeroS1['R_s34'] = np.exp((np.log(zeroS1['conc_s2r1']) * 
                                (np.int64(zeroS1['ring_loc'])+1-zeroS1['ring_loc'])) +
                                (np.log(zeroS1['conc_s2r2']) * 
                                (zeroS1['ring_loc']-np.int64(zeroS1['ring_loc']))))
    
            zeroS2['R_s12'] = np.exp((np.log(zeroS2['conc_s1r1']) * 
                                (np.int64(zeroS2['ring_loc'])+1-zeroS2['ring_loc'])) +
                                (np.log(zeroS2['conc_s1r2']) * 
                                (zeroS2['ring_loc']-np.int64(zeroS2['ring_loc']))))
            
            somezeros2_df = pd.concat([zeroS1, zeroS2, zeroS12])
            somezeros2_df['intconc'] = (somezeros2_df['R_s12']*(np.int64(somezeros2_df['s'])+1-somezeros2_df['s']) 
                                      + somezeros2_df['R_s34']*(somezeros2_df['s']-np.int64(somezeros2_df['s'])))
            somezeros2_df.drop(['R_s12','R_s34'], axis=1, inplace=True)
                    
            conc_df = pd.concat([nozeros_df, somezeros2_df], ignore_index=True)
        
        return conc_df


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

        # Analyze a batch of outer receptor risk
        
        # Skip if no data in this batch
        if data.size > 0:
                        
            # DF of outer receptor concs
            outer_concs = pd.DataFrame(data, columns=self.columns)
            
            # Get utme, utmn, and hill columns
            outer_concs1 = pd.merge(outer_concs, self.model.outerblks_df[[lat, lon, 'utme', 'utmn', 'hill']],
                                    how='left', on=[lat, lon])

            # Confirm the merge did not grow or shrink the number of rows
            if len(outer_concs.index) != len(outer_concs1.index):
                emessage = "Error! Incorrect merging of outer blocks with outer_concs in AllOuterReceptors."
                Logger.logMessage(emessage)
                raise ValueError(emessage)
                        
            # Merge ure and inverted rfc
            outer_concs2 = pd.merge(outer_concs1, self.haplib_df[['pollutant', 'ure', 'invrfc']],
                                    how='left', on='pollutant')
            
            # Confirm the merge did not grow or shrink the number of rows
            if len(outer_concs.index) != len(outer_concs2.index):
                emessage = "Error! Incorrect merging of haplib with outer_concs1 in AllOuterReceptors."
                Logger.logMessage(emessage)
                raise ValueError(emessage)
                
            # Merge target organ list
            outer_concs3 = pd.merge(outer_concs2, self.organs_df[['pollutant', 'organ_list']],
                                    how='left', on='pollutant')

            # Confirm the merge did not grow or shrink the number of rows
            if len(outer_concs.index) != len(outer_concs3.index):
                emessage = "Error! Incorrect merging of target organs with outer_concs2 in AllOuterReceptors."
                Logger.logMessage(emessage)
                raise ValueError(emessage)

            
            chk4null = outer_concs3[outer_concs3['organ_list'].isnull()]
            if not chk4null.empty:
                # Replace NaN with list of 0's
                outer_concs3['organ_list'] = outer_concs3['organ_list'].apply(
                        lambda x: x if isinstance(x, list) else [0,0,0,0,0,0,0,0,0,0,0,0,0,0])


            # Compute risk
            outer_concs3[mir] = outer_concs3['conc'] * outer_concs3['ure']
            
            # Compute all 14 HI's
            for i in range(14):
                hiname = self.hi_list[i]
                organval = np.array(list(zip(*outer_concs3['organ_list']))[i])
                outer_concs3[hiname] = self.calculateHI(outer_concs3['conc'].values, 
                                        outer_concs3['invrfc'].values, organval)

            # Sum risk and HI to blocks
            blksumm_cols = [lat, lon, overlap, elev, rec_id, utme, utmn, hill, population,
                            mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                            hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', rec_id:'first',
                    utme:'first', utmn:'first', hill:'first',population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}
            
            self.outerAgg = outer_concs3.groupby([lat, lon]).agg(aggs)[blksumm_cols]



            #--------------- Keep track of incidence -----------------------------------------
            
            # Compute incidence for each Outer rececptor and then sum incidence by source_id/pollutant/emis_type
            outer_concs3['inc'] = outer_concs3[mir] * outer_concs3[population]/70
            inc_cols = [source_id, pollutant, 'emis_type', 'inc']
            aggs = {source_id:'first', pollutant:'first','emis_type':'first','inc':'sum'}
            incsumm = outer_concs3.groupby([source_id, pollutant, 'emis_type']).agg(aggs)[inc_cols]
            
            # Update the outerInc incidence dictionary
            for index, row in incsumm.iterrows():
                self.outerInc[(row[source_id], row[pollutant], row['emis_type'])] = \
                    self.outerInc[(row[source_id], row[pollutant], row['emis_type'])] + row['inc']


    def calculateMir(self, conc, ure):
        cancer_risk = conc * ure
        return cancer_risk
    
    def calculateHI(self, conc, invrfc, organ):
        aHI = conc * (invrfc/1000) * organ
        return aHI
        
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
        if self.acute_yn == 'N':
            self.numericColumns = [lat, lon, conc, elev, population]
        else:
           self.numericColumns = [lat, lon, conc, aconc, elev, population]
            
        self.strColumns = [rec_id, source_id, 'emis_type', pollutant, overlap]

        df = self.readFromPathCsv(self.getColumns())
        return df.fillna("")
    

    def createBigDataframe(self):
        # Type setting for CSV reading
        if self.acute_yn == 'N':
            self.numericColumns = [lat, lon, conc, elev, population]
        else:
           self.numericColumns = [lat, lon, conc, aconc, elev, population]
            
        self.strColumns = [rec_id, source_id, 'emis_type', pollutant, overlap, rec_type]

        colnames = self.getColumns()
        self.skiprows = 1
        reader = pd.read_csv(f, skiprows=self.skiprows, names=colnames, dtype=str, 
                             na_values=[''], keep_default_na=False, chunksize=100000)

        return reader
    