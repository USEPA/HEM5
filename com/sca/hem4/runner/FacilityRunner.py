import os
import time
import subprocess
import shutil
import pandas as pd
from com.sca.hem4.OutputProcessing import *
from com.sca.hem4.FacilityPrep import FacilityPrep
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.DepositionDepletion import sort
from com.sca.hem4.model.Model import *
from datetime import datetime


class FacilityRunner():

    def __init__(self, id, model, abort):
        self.facilityId = id
        self.model = model
        self.abort = abort
        self.start = time.time()
        self.phase = None
        
    
    def setup(self):
                
        #put phase in model_optns
        fac = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == self.facilityId]
        
        if fac['phase'].iloc[0] == "":
            self.model.model_optns['phase'] = None

        else:
            self.model.model_optns['phase'] = fac['phase'].tolist()[0]

        
#        if self.model.group_name != None:
#            
#            Logger.logMessage("RUN GROUP: " + self.model.group_name)
#            
#            output = "output/"+self.model.group_name+"/"
#            fac_folder =  output + self.facilityId + "/"
#            
#        else:
#            
#            self.model.group_name = "rungroup_" + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
#            Logger.logMessage("RUN GROUP: " + self.model.group_name)
            
        #create fac folder
        fac_folder =  "output/" + self.model.group_name + "/" + self.facilityId + "/"

        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)        
        
        #do prep
        try:    
            self.prep_fac = self.prep()
            
        except Exception as e:
                
                Logger.logMessage(str(e))


        # phases dictionary
        if self.model.model_optns['phase'] != None:
            phases = sort(fac)

        else:
            phases = {'phase': None, 'settings': None}

                
        #Single run model options
        if self.model.model_optns['phase'] != 'B':

            self.runstream = self.prep_fac.createRunstream(self.facilityId, phases)

#            #create runstream
#            try:
#                self.runstream = self.prep_fac.createRunstream(self.facilityId, phases)
#                
#            except Exception as e:
#                
#                Logger.logMessage(str(e))
#                raise Exception("An error occurred while running a facility")
                

            # Set the runtype variable which indicates how Aermod is run (with or without deposition)
            # and what columns will be in the Aermod plotfile
            depoYN = self.model.facops['dep'][0]
            
            if phases['phase'] == 'P':
                depotype = self.model.facops['pdep'][0]
                self.phase = 'P'
                
            elif phases['phase'] == 'V':
                depotype = self.model.facops['vdep'][0]
                self.phase = 'V'
                
            else:
                depotype = 'NO'
                
            runtype = self.set_runtype(depoYN, depotype)
            self.model.model_optns['runtype'] = runtype
            
            
            #run aermod
            self.run(fac_folder)

            #check aermod run and move aermod.inp, aermod.out, and plot.plt files to facility folder
            check = False
            try:
                check = self.check_run(fac_folder, self.phase)
            
            except Exception as e:
                
                Logger.logMessage(str(e))
                

            if check == True:
                
                if phases['phase'] == 'P':
                    
                    # Open the Aermod plotfile
                    ppfile = open(fac_folder + 'plotfile_p.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(ppfile, self.model.model_optns['runtype'])
                    
                elif phases['phase'] == 'V':
                    
                    
                    # Open the Aermod plotfile
                    vpfile = open(fac_folder + 'plotfile_v.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(vpfile, self.model.model_optns['runtype'])


                else:
                
                    # Open the Aermod plotfile
                    pfile = open(fac_folder + 'plotfile.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(pfile, self.model.model_optns['runtype'])
                

                # Set the emis_type column in plot_df
                if phases['phase'] == None:
                    plot_df['emis_type'] = 'C'
                else:
                    plot_df['emis_type'] = phases['phase']
                                
                # Process outputs for single facility
                try:
                    
                    self.process_outputs(fac_folder, plot_df)
                    
                except Exception as e:
                
                    Logger.logMessage(str(e))
                

        else:
            #double run for particle and vapor

            #let the sort get both phases then loop through each
            phases = sort(fac)
                        
            runstreams = []
            plot_df = pd.DataFrame()
                        
            for r in phases:

                Logger.logMessage(r['phase'] + " run:")
                
                # create runstream for individual phase
                
                try:
                    self.runstream = self.prep_fac.createRunstream(self.facilityId, r)
                    
                except BaseException as e:
                
                    Logger.logMessage(str(e))
                
 
                # Set the runtype variable which indicates how Aermod is run (with or without deposition)
                # and what columns will be in the Aermod plotfile
                depoYN = self.model.facops['dep'][0]
                print('deposition type', depoYN)                
                
                # depotype can be WD (wet/dry), WO (wet only), DO (dry only), or NO (none)
                if r['phase'] == 'P':
                    depotype = self.model.facops['pdep'][0]
                    self.phase = 'P'
                    print('depotype', depotype)
                elif r['phase'] == 'V':
                    depotype = self.model.facops['vdep'][0]
                    self.phase = 'V'
                else:
                    depotype = 'NO'
                runtype = self.set_runtype(depoYN, depotype)
                self.model.model_optns['runtype'] = runtype
               
                #store runstream objects for later use
                runstreams.append(self.runstream)
                                
                #run individual phase
                self.run(fac_folder)
                
                #check aermod run, move aermod.out file to facility folder and rename
                check = False
                try:
                    check = self.check_run(fac_folder, r['phase'])
                    
                except Exception as e:
                
                    Logger.logMessage(str(e))
                
                
                if check == True:
    
                    # Open the Aermod plotfile
                    if self.phase == 'P':
                        pfile = open(fac_folder + 'plotfile_p.plt', "r")
                    elif self.phase == 'V':
                        pfile = open(fac_folder + 'plotfile_v.plt', "r")
                    else:
                        pfile = open(fac_folder + 'plotfile.plt', "r")

                    
                    # Put the plotfile into a dataframe
                    temp_df = self.readplotf(pfile, self.model.model_optns['runtype'])
                    
                    # Set the emis_type column in temp_df
                    temp_df['emis_type'] = r['phase']
                    
                    # Append temp_df to plot_df
                    plot_df = plot_df.append(temp_df, ignore_index=True)
                    
 
                    #TODO: Remove the below 4 lines for production version. For QA only.
                    plotdf_path = "working/plot_df.xlsx"
                    plotdf_con = pd.ExcelWriter(plotdf_path)
                    plot_df.to_excel(plotdf_con,'Sheet1')
                    plotdf_con.save()
            
                    # Process outputs for this facility
                    try:
                    
                        self.process_outputs(fac_folder, plot_df)
                        
                    except Exception as e:
                        
                        Logger.logMessage(str(e))
                
           
               
    
    def prep(self):
        
        Logger.logMessage("Building runstream for " + self.facilityId)
        
        try:
            
            prep = FacilityPrep(self.model)
        
#        print("building runstream")
        
        except Exception as e:
                
            Logger.logMessage(str(e))
                
        
        
        return prep
            

    def run(self, fac_folder):

        #run aermod
        now = datetime.now().time()
        current_time = now.strftime("%H:%M:%S")
        Logger.logMessage("Running Aermod for " + self.facilityId + ". Started at time " + current_time)

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
            self.model.aermod = False
            Logger.logMessage("Aermod ran unsuccessfully. Please check the "+
                              "error section of the aermod.out file. Ended at time "+
                              current_time)
        else:
            success = True
            self.aermod = True
            Logger.logMessage("Aermod ran successfully. Ended at time " + current_time)
        check.close()

        if success == True:
             
            #determine which plotfile we are using based on phases
            if self.phase == 'P' or phasetype =='P':
                
                # listing directories
                print ("The dir is: %s"%os.listdir('aermod'))
                
                #rename for particle
                os.rename('aermod/plotfile.plt','aermod/plotfile_p.plt')
                plt_version = 'plotfile_p.plt'
                  # listing directories
                print ("The dir is: %s"%os.listdir('aermod'))
                 
            elif self.phase == 'V' or phasetype == 'V':
                
                  # listing directories
                print ("The dir is: %s"%os.listdir('aermod'))
                #rename for vapor
                os.rename('aermod/plotfile.plt','aermod/plotfile_v.plt')
                plt_version = 'plotfile_v.plt'
                
                  # listing directories
                print ("The dir is: %s"%os.listdir('aermod'))
            else:
                plt_version = 'plotfile.plt'

            # Move aermod.inp, aermod.out, and plotfile.plt to the fac output folder
            # If phasetype is not empty, rename aermod.out, aermod.inp and plotfile.plt using phasetype
            # Replace if one is already in there othewrwise will throw error
            if os.path.isfile(fac_folder + 'aermod.out'):
                os.remove(fac_folder + 'aermod.out')

            if os.path.isfile(fac_folder + 'aermod.inp'):
                os.remove(fac_folder + 'aermod.inp')

            if os.path.isfile(fac_folder + plt_version):
                os.remove(fac_folder + plt_version)

            # move aermod.out file
            shutil.move(output, fac_folder)
            
            # move aermod.inp file
            inpfile = os.path.join("aermod", "aermod.inp")
            shutil.move(inpfile, fac_folder)

            # move plotfile.plt file
            pltfile = os.path.join("aermod", plt_version)
            shutil.move(pltfile, fac_folder)
            
            # if an acute maxhour.plt plotfile was output by Aermod, move it too
            maxfile = os.path.join("aermod", "maxhour.plt")
            if os.path.isfile(maxfile):
                if os.path.isfile(fac_folder + "maxhour.plt"):
                    os.remove(fac_folder + "maxhour.plt")
                shutil.move(maxfile, fac_folder)

            # if a temporal seasonhr.plt plotfile was output by Aermod, move it too
            seasonhrfile = os.path.join("aermod", "seasonhr.plt")
            if os.path.isfile(seasonhrfile):
                if os.path.isfile(fac_folder + "seasonhr.plt"):
                    os.remove(fac_folder + "seasonhr.plt")
                shutil.move(seasonhrfile, fac_folder)

            # for deposition runs, change the names of aermod.out and aermod.inp
            if phasetype != None:
                
                oldname = os.path.join(fac_folder, 'aermod.out')
                newname = os.path.join(fac_folder, 'aermod_' + phasetype + '.out')
                if os.path.isfile(newname):
                    os.remove(newname)
                os.rename(oldname, newname)    

                oldname = os.path.join(fac_folder, 'aermod.inp')
                newname = os.path.join(fac_folder, 'aermod_' + phasetype + '.inp')
                if os.path.isfile(newname):
                    os.remove(newname)
                os.rename(oldname, newname)    

                
            
            
            
            
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
        
        print('runtype', runtype)                
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

        plotf_df.utme = plotf_df.utme.round()
        plotf_df.utmn = plotf_df.utmn.round()

        return plotf_df
    

    def process_outputs(self, fac_folder, plot_df):
           
            # check length of fac_folder
            
            
            #process outputs
            Logger.logMessage("Processing Outputs for " + self.facilityId)
            outputProcess = Process_outputs(fac_folder, self.facilityId, 
                                            self.model, self.prep_fac,
                                            self.runstream, plot_df, self.abort)
            outputProcess.process()
                        
            #if successful save state
            self.model.save.save_model(self.facilityId)
            
            pace =  str(round((time.time()- self.start)/60, 2)) + ' minutes'
            Logger.logMessage("Finished calculations for " + self.facilityId + 
                              ' after ' + pace + "\n")
