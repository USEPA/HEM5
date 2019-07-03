import os
import time
import subprocess
import shutil
import pandas as pd
from com.sca.hem4.OutputProcessing import *
from com.sca.hem4.FacilityPrep import FacilityPrep
from com.sca.hem4.log import Logger
from com.sca.hem4.DepositionDepletion import sort
from com.sca.hem4.model.Model import *
from datetime import datetime


class FacilityRunner():

    def __init__(self, id, model, abort):
        self.facilityId = id
        self.model = model
        self.abort = abort
        self.start = time.time()
        
    
    def setup(self):
        
        #put phase in model_optns
        fac = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == self.facilityId]

        if 'nan' in fac['phase'].tolist()[0]:
            self.model.model_optns['phase'] = None

        else:
            self.model.model_optns['phase'] = fac['phase'].tolist()[0]

        
        #create fac folder
        fac_folder = "output/"+ self.facilityId + "/"
        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)

        #do prep
        self.prep_fac = self.prep()

        # phases dictionary
        if self.model.model_optns['phase'] != None:
            phases = sort(fac)

        else:
            phases = {'phase': None, 'settings': None}

        
        #Single run model options
        if self.model.model_optns['phase'] != 'B':
            
            #create runstream
            self.runstream = self.prep_fac.createRunstream(self.facilityId, phases)

            # Set the runtype variable which indicates how Aermod is run (with or without deposition)
            # and what columns will be in the Aermod plotfile
            depoYN = self.model.facops['dep'][0]
            if phases['phase'] == 'P':
                depotype = self.model.facops['pdep'][0]
            elif phases['phase'] == 'V':
                depotype = self.model.facops['vdep'][0]
            else:
                depotype = 'NO'
            runtype = self.set_runtype(depoYN, depotype)
            self.model.model_optns['runtype'] = runtype
            
            
            #run aermod
            self.run(fac_folder)

            #check aermod run and move aermod.out file to facility folder
            check = self.check_run(fac_folder, None)

            if check == True:

                # Open the Aermod plotfile
                pfile = open("aermod/plotfile.plt", "r")
                
                # Now put the plotfile into a dataframe
                plot_df = self.readplotf(pfile, self.model.model_optns['runtype'])
                
                # Set the emis_type column in plot_df
                if phases['phase'] == None:
                    plot_df['emis_type'] = 'C'
                else:
                    plot_df['emis_type'] = phases['phase']
                                
                # Process outputs for single facility
                self.process_outputs(fac_folder, plot_df)

        else:
            #double run for particle and vapor

            #let the sort get both phases then loop through each
            phases = sort(fac)
                        
            runstreams = []
            plot_df = pd.DataFrame()
            
            for r in phases:

                Logger.logMessage(r['phase'] + " run:")
                
                # create runstream for individual phase
                self.runstream = self.prep_fac.createRunstream(self.facilityId, r)
 
                # Set the runtype variable which indicates how Aermod is run (with or without deposition)
                # and what columns will be in the Aermod plotfile
                depoYN = self.model.facops['dep'][0]
                
                # depotype can be WD (wet/dry), WO (wet only), DO (dry only), or NO (none)
                if r['phase'] == 'P':
                    depotype = self.model.facops['pdep'][0]
                elif r['phase'] == 'V':
                    depotype = self.model.facops['vdep'][0]
                else:
                    depotype = 'NO'
                runtype = self.set_runtype(depoYN, depotype)
                self.model.model_optns['runtype'] = runtype
               
                #store runstream objects for later use
                runstreams.append(self.runstream)
                                
                #run individual phase
                self.run(fac_folder)
                
                #check aermod run, move aermod.out file to facility folder and rename
                check = self.check_run(fac_folder, r['phase'])
                
                if check == True:
    
                    # Open the Aermod plotfile
                    pfile = open("aermod/plotfile.plt", "r")
                    
                    # Put the plotfile into a dataframe
                    temp_df = self.readplotf(pfile, self.model.model_optns['runtype'])
                    
                    # Set the emis_type column in temp_df
                    temp_df['emis_type'] = r['phase']
                    
                    # Append temp_df to plot_df
                    plot_df = plot_df.append(temp_df, ignore_index=True)
 
            # For QA purposes, export plot_df to an Excel file in the Working directory
            plotdf_path = "working/plot_df.xlsx"
            plotdf_con = pd.ExcelWriter(plotdf_path)
            plot_df.to_excel(plotdf_con,'Sheet1')
            plotdf_con.save()
    
            # Process outputs for this facility
            self.process_outputs(fac_folder, plot_df)
               
    
    def prep(self):
        
        prep = FacilityPrep(self.model)
        
        Logger.logMessage("Building runstream for facility " + self.facilityId)
        
        return prep
            

    def run(self, fac_folder):

        #run aermod
        now = datetime.now().time()
        current_time = now.strftime("%H:%M:%S")
        Logger.logMessage("Running Aermod for " + self.facilityId + " starting at time " + current_time)

        # Start aermod asynchronously and then monitor it, with the possibility
        # of terminating it midstream (i.e. if the thread is asked to die...)

        executable = os.path.join("aermod", "aermod.exe")
        aermodInput = "aermod.inp"
        p = subprocess.Popen([executable, aermodInput], cwd="aermod")
        subRunning = True
        while subRunning:
            if self.abort.is_set():
                Logger.logMessage("Terminating aermod process...")
                p.terminate()
                return
            else:
                time.sleep(0.5)
                subRunning = (p.poll() is None)
                
                
                
    def check_run(self, fac_folder, phasetype):

        ## Check for successful aermod run:
        output = os.path.join("aermod", "aermod.out")
        check = open(output, 'r')
        message = check.read()
        now = datetime.now().time()
        current_time = now.strftime("%H:%M:%S")
        if 'AERMOD Finishes UN-successfully' in message:
            success = False
            Logger.logMessage("Aermod ran unsuccessfully. Please check the "+
                              "error section of the aermod.out file. Ended at time "+
                              current_time)
        else:
            success = True
            Logger.logMessage("Aermod ran successfully. Ended at time " + current_time)
        check.close()

        if success == True:

            #move aermod.out to the fac output folder and rename using phasetype
            #replace if one is already in there othewrwise will throw error

            if os.path.isfile(fac_folder + 'aermod.out'):
                os.remove(fac_folder + 'aermod.out')

            shutil.move(output, fac_folder)
            
            if phasetype != None:
                oldname = os.path.join(fac_folder, 'aermod.out')
                newname = os.path.join(fac_folder, 'aermod_' + phasetype + '.out')
                if os.path.isfile(newname):
                    os.remove(newname)
                os.rename(oldname, newname)    
                
            #if successful save state
            self.model.save.save_model(self.facilityId)
                
            return success


    def set_runtype(self, depYN, deptype):
        
        if depYN == 'N':
            # No deposition
            runtype = 0
        else:
            if deptype == 'WD':
                # Wet and dry deposition
                runtype = 1
            elif deptype == 'DO':
                # Dry only deposition
                runtype = 2
            elif deptype == 'WO':
                # Wet only deposition
                runtype = 3
            else:
                # No deposition
                runtype = 0
                        
        return runtype
        
        
        
    def readplotf(self, pfile, runtype):

        if runtype == 0:
            plotf_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,result,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9], 
                converters={utme:np.float64,utmn:np.float64,result:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
                comment='*')
        elif runtype == 1:
            plotf_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,result,ddp,wdp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10,11], 
                converters={utme:np.float64,utmn:np.float64,result:np.float64,ddp:np.float64,wdp:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
                comment='*')
        elif runtype == 2:
            plotf_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,result,ddp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10], 
                converters={utme:np.float64,utmn:np.float64,result:np.float64,ddp:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
                comment='*')
        elif runtype == 3:
            plotf_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,result,wdp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10], 
                converters={utme:np.float64,utmn:np.float64,result:np.float64,wdp:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
                comment='*')
        
        return plotf_df
    

    def process_outputs(self, fac_folder, plot_df):
           
            # check length of fac_folder
            
            
            #process outputs
            Logger.logMessage("Processing Outputs for " + self.facilityId)
            outputProcess = Process_outputs(fac_folder, self.facilityId, 
                                            self.model, self.prep_fac,
                                            self.runstream, plot_df, self.abort)
            outputProcess.process()
                        

            pace =  str(time.time()- self.start) + 'seconds'
            Logger.logMessage("Finished calculations for " + self.facilityId + 
                              ' after' + pace + "\n")