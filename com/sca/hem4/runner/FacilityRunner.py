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
from com.sca.hem4.support.NormalRounding import *
import com.sca.hem4.FindMet as fm


class FacilityRunner():

    def __init__(self, id, model, abort):
        self.facilityId = id
        self.model = model
        self.abort = abort
        self.start = time.time()
        self.phase = None
        
        self.phaseNames = {'P': 'Particle', 'V': 'Vapor'}
        self.facops = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == self.facilityId]


    def setupLead(self):
                                
        #create fac folder
        fac_folder =  "output/" + self.model.group_name + "/" + self.facilityId + "/"

        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)        
        
        #do prep
        try:    
            self.prep_fac = self.prep()
            
        except BaseException as e:
                
                Logger.logMessage(str(e))

        
        # phases dictionary
        phases = {'phase': None, 'settings': None}

              
        # create Aermod runstream for the lead run
        self.runstream = self.prep_fac.createRunstream(self.facilityId, phases, aermodleadYN='Y')

        if self.runstream is None:
            # In this case, no lead emissions were found for this facility. Do not run LEADPOST.
            # Instead return to Processor and run setup for mormal Aermod run.
            return
            
        # Set the runtype variable which indicates how Aermod is run (with or without deposition)
        # and what columns will be in the Aermod postfile
        depoYN = 'N'
        depotype = 'NO'
        runtype = self.set_runtype(depoYN, depotype)
        self.model.model_optns['runtype'] = runtype
                    
        #run aermod
        Logger.logMessage("Aermod will be run for lead sources only and produce outputs for LEADPOST.")
        self.run(fac_folder)

        #check lead aermod run and if successful then run LEADPOST
        check = False
        try:
            check = self.check_AermodLead_run(fac_folder)
        
        except BaseException as e:
            
            Logger.logMessage(str(e))
        
        
        if check == True:
            
            # The post files represent unit emissions. Adjust them using the real
            # lead emissions.
            self.adjustPostfiles(fac_folder)
            
            # run LEADPOST
            self.runLeadPost(fac_folder)

            #check LEADPOST run
            checkpost = False
            try:
                checkpost = self.check_LeadPost_run(fac_folder)
            
            except BaseException as e:
                
                Logger.logMessage(str(e))
            


            
    
    def setup(self):

        #Debug
        self.model.faclist.dataframe['leadYN'] = 'N'
            
        #put phase in model_optns
        self.acute_yn = self.facops[acute].tolist()[0]
        
        if self.facops['phase'].iloc[0] == "":
            self.model.model_optns['phase'] = None

        else:
            self.model.model_optns['phase'] = self.facops['phase'].tolist()[0]

                    
        #create faility folder
        fac_folder =  "output/" + self.model.group_name + "/" + self.facilityId + "/"

        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)        
        
        #do prep
        try:    
            self.prep_fac = self.prep()
            
        except BaseException as e:
                
                Logger.logMessage(str(e))

        
        # phases dictionary
        if self.model.model_optns['phase'] in ('P', 'V', 'B'):
            phases = sort(self.facops)
            
        elif self.model.model_optns['phase'] == 'Z':
            phases = {'phase': 'Z', 'settings': None}

        else:
            phases = {'phase': None, 'settings': None}

              
        # Single run model options
        if self.model.model_optns['phase'] != 'B':

            self.runstream = self.prep_fac.createRunstream(self.facilityId, phases, aermodleadYN='N')

            # Set the runtype variable which indicates how Aermod is run (with or without deposition)
            # and what columns will be in the Aermod plotfile
            depoYN = self.model.facops['dep'].iloc[0]
            
            if phases['phase'] == 'P':
                depotype = self.model.facops['pdep'].iloc[0]
                self.phase = 'P'
                
            elif phases['phase'] == 'V':
                depotype = self.model.facops['vdep'].iloc[0]
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
            
            except BaseException as e:
                
                Logger.logMessage(str(e))
                

            if check == True:
                
                if phases['phase'] == 'P':
                    
                    # Open the Aermod plotfile
                    ppfile = open(fac_folder + 'plotfile_p.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(ppfile, self.model.model_optns['runtype'])
 
                    # If acute run, put the maxhour plot file into a dataframe
                    if self.acute_yn == 'Y':
                        apfile = open(fac_folder + 'maxhour_p.plt', "r")
                        aplot_df = self.readmaxf(apfile, runtype)
                   
                elif phases['phase'] == 'V':
                    
                    
                    # Open the Aermod plotfile
                    vpfile = open(fac_folder + 'plotfile_v.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(vpfile, self.model.model_optns['runtype'])

                    # If acute run, put the maxhour plot file into a dataframe
                    if self.acute_yn == 'Y':
                        apfile = open(fac_folder + 'maxhour_v.plt', "r")
                        aplot_df = self.readmaxf(apfile, runtype)

                    
                else:
                
                    # phase is None (C) or Z
                    
                    # Open the Aermod plotfile
                    pfile = open(fac_folder + 'plotfile.plt', "r")
                    
                    # Now put the plotfile into a dataframe
                    plot_df = self.readplotf(pfile, self.model.model_optns['runtype'])

                    # If acute run, put the maxhour plot file into a dataframe
                    if self.acute_yn == 'Y':
                        apfile = open(fac_folder + 'maxhour.plt', "r")
                        aplot_df = self.readmaxf(apfile, runtype)
                

                # Set the emis_type column in plot_df
                if phases['phase'] == None:
                    
                    plot_df['emis_type'] = 'C'
                    
                elif phases['phase'] == 'Z':
                    
                    # Special case where concs by particle and vapor are desired but no deposition/depletion
                    plot_df['emis_type'] = 'P'
                    V_df = plot_df.copy()
                    V_df['emis_type'] = 'V'
                    plot_df = pd.concat([plot_df, V_df], ignore_index=True)
                    
                else:
                    plot_df['emis_type'] = phases['phase']

                
                # If acute run, set the emis_type column in aplot_df
                if self.acute_yn == 'Y':
 
                    if phases['phase'] == None:
                    
                        aplot_df['emis_type'] = 'C'
                        
                    elif phases['phase'] == 'Z':
                        
                        # Special case where concs by particle and vapor are desired but no deposition/depletion
                        aplot_df['emis_type'] = 'P'
                        V_df = aplot_df.copy()
                        V_df['emis_type'] = 'V'
                        aplot_df = pd.concat([aplot_df, V_df], ignore_index=True)
                        
                    else:
                        aplot_df['emis_type'] = phases['phase']
    
                    # Put the acute plot file into the Model class
                    self.model.acuteplot_df = aplot_df
                
                # Process outputs for single facility
                self.process_outputs(fac_folder, plot_df)
                

        else:
            #double run for particle and vapor

            #let the sort get both phases then loop through each
            phases = sort(self.facops)
                        
            runstreams = []
            plot_df = pd.DataFrame()
            
            if self.acute_yn == 'Y':
                aplot_df = pd.DataFrame()
            
            # Initialize array to hold runtype of each phase run
            bothruntype = []
            
            for r in phases:

                Logger.logMessage(self.phaseNames[r['phase']] + " run:")
                
                # create runstream for individual phase
                try:
                    self.runstream = self.prep_fac.createRunstream(self.facilityId, r, aermodleadYN='N')
                    
                except BaseException as e:
                
                    Logger.logMessage(str(e))
                
 
                # Set the runtype variable which indicates how Aermod is run (with or without deposition)
                # and what columns will be in the Aermod plotfile
                depoYN = self.model.facops['dep'].iloc[0]
                
                # depotype can be WD (wet/dry), WO (wet only), DO (dry only), or NO (none)
                if r['phase'] == 'P':
                    depotype = self.model.facops['pdep'].iloc[0]
                    self.phase = 'P'
                elif r['phase'] == 'V':
                    depotype = self.model.facops['vdep'].iloc[0]
                    self.phase = 'V'
                else:
                    depotype = 'NO'
                runtype = self.set_runtype(depoYN, depotype)
                bothruntype.append(runtype)
               
                #store runstream objects for later use
                runstreams.append(self.runstream)
                                
                #run individual phase
                self.run(fac_folder)
                
                #check aermod run, move aermod.out file to facility folder and rename
                check = False
                try:
                    check = self.check_run(fac_folder, r['phase'])
                    
                except BaseException as e:
                
                    Logger.logMessage(str(e))
                
                
                if check == True:
    
                    # Open the Aermod plotfile
                    if self.phase == 'P':
                        pfile = open(fac_folder + 'plotfile_p.plt', "r")
                    elif self.phase == 'V':
                        pfile = open(fac_folder + 'plotfile_v.plt', "r")
                    else:
                        pfile = open(fac_folder + 'plotfile.plt', "r")                    
                    
                    # Put the plotfile into a dataframe and assign emis_type
                    temp_df = self.readplotf(pfile, runtype)
                    temp_df['emis_type'] = r['phase']

                    # Append temp_df to plot_df
                    plot_df = pd.concat([plot_df, temp_df], ignore_index=True)

                    
                    # If acute run, put the maxhour plot file into a dataframe
                    if self.acute_yn == 'Y':
                        if self.phase == 'P':
                            apfile = open(fac_folder + 'maxhour_p.plt', "r")
                        elif self.phase == 'V':
                            apfile = open(fac_folder + 'maxhour_v.plt', "r")
                        else:
                            apfile = open(fac_folder + 'maxhour.plt', "r")
                        tempmax_df = self.readmaxf(apfile, runtype)
                        tempmax_df['emis_type'] = r['phase']
                        aplot_df = pd.concat([aplot_df, tempmax_df], ignore_index=True)
                    
            
            # Determine the runtype for a double run
            if (1 in bothruntype) or ((2 in bothruntype) and (3 in bothruntype)):
                alltype = 1
            if (bothruntype == [2,2] or bothruntype == [2,0] or bothruntype == [0,2]):
                alltype = 2
            if (bothruntype == [3,3] or bothruntype == [3,0] or bothruntype == [0,3]):
                alltype = 3
            if bothruntype == [0,0]:
                alltype = 0
                
            self.model.model_optns['runtype'] = alltype

            # Put the acute plot file into the Model class (if run)
            if self.acute_yn == 'Y':
                self.model.acuteplot_df = aplot_df
                
                
            # Process outputs for this facility
            self.process_outputs(fac_folder, plot_df)
            
    
    def prep(self):
        
        Logger.logMessage("Building runstream for " + self.facilityId)
        
        try:
            
            prep = FacilityPrep(self.model)
                
        except BaseException as e:
            
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
                        

    def runLeadPost(self, fac_folder):

        #run LEADPOST
        now = datetime.now().time()
        current_time = now.strftime("%H:%M:%S")
        Logger.logMessage("Running LEADPOST for " + self.facilityId + ". Started at time " + current_time)


        # Need the modeling time period as an input to LEADPOST.
        
        if self.facops['annual'].iloc[0] != 'Y' and self.facops['period_start'].iloc[0] != '' and self.facops['period_end'].iloc[0] != '':
            # User provided modeling time period
            period_start_spec = self.facops['period_start'].iloc[0]
            starts = period_start_spec.split(" ")
            start_year = starts[0]
            start_month = starts[1].zfill(2)
            period_end_spec = self.facops['period_end'].iloc[0]
            ends = period_end_spec.split(" ")
            end_year = ends[0]
            end_month = ends[1]
        else:
            # Model is run for one year. Get the meteorology year.
            surf_file, upper_file, surfdata_str, uairdata_str, prof_base, distance, year = \
                   fm.find_met(self.model.computedValues['cenlat'], self.model.computedValues['cenlon'], self.model.metlib.dataframe)
            start_year = str(year)
            start_month = '01'
            end_year = str(year)
            end_month = '12'

        # Construct the names of the LEADPOST outputs. They are named after the modeling
        # time period and will be needed later.
        self.monthconc_output = (start_month + '_' + start_year + '_' + end_month + '_' 
                            + end_year + '_3_month_concs.txt')
        self.monthmaxconc_output = (start_month + '_' + start_year + '_' + end_month + '_' 
                            + end_year + '_3_month_max_concs_rec.txt')
        

        # Start LEADPOST asynchronously and then monitor it, with the possibility
        # of terminating it midstream (i.e. if the thread is asked to die...)

        leadpost_inputs = [start_month+' '+start_year+' '+end_month+' '+end_year, '', 'Y', 'A', '1']
        executable = os.path.join("leadpost", "leadpost.exe")
        p = subprocess.Popen([executable], stdin=subprocess.PIPE, text=True, cwd="leadpost")
        for data_input in leadpost_inputs:
            p.stdin.write(data_input + '\n')
        p.stdin.flush()
        p.stdin.close()
        subRunning = True
        while subRunning:
            if self.abort.is_set():
                Logger.logMessage("Terminating LEADPOST process...")
                p.terminate()
                return
            else:
                time.sleep(0.5)
                subRunning = (p.poll() is None)

                
    def check_run(self, fac_folder, phasetype):

        # Did user abort?
        if self.abort.is_set():
            success = False
            self.model.aermod = False
            return success
        
        ## Check for successful aermod run:
        output = os.path.join("aermod", "aermod.out")
        if os.path.exists(output):
            check = open(output, 'r')
            message = check.read()
            now = datetime.now().time()
            current_time = now.strftime("%H:%M:%S")
            if 'AERMOD Finishes UN-successfully' in message:
                success = False
                self.model.aermod = False
    
                
                Logger.logMessage("Aermod ran unsuccessfully. Please check the "+
                                  "error section of the aermod.out file in the "  + str(self.facilityId) + 
                                  " output folder. Ended at time "+ current_time)
            else:
                success = True
                self.model.aermod = True
                Logger.logMessage("Aermod ran successfully. Ended at time " + current_time)
            check.close()
        else:
            # aermod.out does not exist
            success = False
            self.model.aermod = False
            
            Logger.logMessage("Aermod finished but the aermod.out file does not exist. Please check the "+
                              "aermod folder for any *.TMP or *.ERR files that may indicate the problem.")
            

        if success == True:
             
            #determine which plotfile and maxhour we are using based on phases
            if self.phase == 'P' or phasetype =='P':
                                
                #rename plotfile for particle
                if os.path.exists('aermod/plotfile_p.plt'):
                    os.remove('aermod/plotfile_p.plt')
                os.rename('aermod/plotfile.plt','aermod/plotfile_p.plt')
                plt_version = 'plotfile_p.plt'

                #rename maxhour for particle
                if self.acute_yn == 'Y':
                    if os.path.exists('aermod/maxhour_p.plt'):
                        os.remove('aermod/maxhour_p.plt')
                    os.rename('aermod/maxhour.plt','aermod/maxhour_p.plt')
                max_version = 'maxhour_p.plt'
                 
            elif self.phase == 'V' or phasetype == 'V':
                
                #rename plotfile for vapor
                if os.path.exists('aermod/plotfile_v.plt'):
                    os.remove('aermod/plotfile_v.plt')
                os.rename('aermod/plotfile.plt','aermod/plotfile_v.plt')
                plt_version = 'plotfile_v.plt'

                #rename maxhour for vapor
                if self.acute_yn == 'Y':
                    if os.path.exists('aermod/maxhour_v.plt'):
                        os.remove('aermod/maxhour_v.plt')
                    os.rename('aermod/maxhour.plt','aermod/maxhour_v.plt')
                max_version = 'maxhour_v.plt'
                
            else:
                plt_version = 'plotfile.plt'
                max_version = 'maxhour.plt'

            # Move aermod.inp, aermod.out, and plotfile.plt to the fac output folder
            # If phasetype is not empty, rename aermod.out, aermod.inp, plotfile.plt, and maxhour.plt using phasetype
            # Replace if one is already in there othewrwise will throw error
            if os.path.isfile(fac_folder + 'aermod.out'):
                os.remove(fac_folder + 'aermod.out')

            if os.path.isfile(fac_folder + 'aermod.inp'):
                os.remove(fac_folder + 'aermod.inp')

            if os.path.isfile(fac_folder + plt_version):
                os.remove(fac_folder + plt_version)

            if os.path.isfile(fac_folder + max_version):
                os.remove(fac_folder + max_version)

            for item in os.listdir(fac_folder):
                if item.endswith(".tmp"):
                    file_path = os.path.join(fac_folder, item)
                    os.remove(file_path)

            # move aermod.out file
            shutil.move(output, fac_folder)
            
            # move aermod.inp file
            inpfile = os.path.join("aermod", "aermod.inp")
            shutil.move(inpfile, fac_folder)

            # move plotfile.plt file
            pltfile = os.path.join("aermod", plt_version)
            shutil.move(pltfile, fac_folder)
            
            # If acute was run, move the maxhour plot file
            if self.acute_yn == 'Y':
                apltfile = os.path.join("aermod", max_version)
                shutil.move(apltfile, fac_folder)
                
            
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

            # Move any Aermod tmp files. These contain error or warning messages.
            for item in os.listdir("aermod"):
                if item.endswith(".tmp"):
                    old_name = os.path.join("aermod", item)
                    new_name = os.path.join(fac_folder, item)
                    os.rename(old_name, new_name)
        
        else:
            # Aermod failed. Move aermod.inp and aermod.out and rename if appropriate.

            # move aermod.out file
            shutil.move(output, fac_folder)
            
            # move aermod.inp file
            inpfile = os.path.join("aermod", "aermod.inp")
            shutil.move(inpfile, fac_folder)

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


    def check_AermodLead_run(self, fac_folder):

        # Did user abort?
        if self.abort.is_set():
            success = False
            self.model.aermod = False
            return success
        
        ## Check for successful aermod run:
        output = os.path.join("aermod", "aermod.out")
        if os.path.exists(output):
            check = open(output, 'r')
            message = check.read()
            now = datetime.now().time()
            current_time = now.strftime("%H:%M:%S")
            if 'AERMOD for lead finishes UN-successfully' in message:
                success = False
                self.model.aermod = False
    
                
                Logger.logMessage("Aermod for Lead ran unsuccessfully. Please check the "+
                                  "error section of the aermod.out file in the "  + str(self.facilityId) + 
                                  " output folder. Ended at time "+ current_time)
            else:
                success = True
                self.model.aermod = True
                Logger.logMessage("Aermod for Lead ran successfully. Ended at time " + current_time)
            check.close()
        else:
            # aermod.out does not exist
            success = False
            self.model.aermod = False
            
            Logger.logMessage("Aermod for Lead finished but the aermod.out file does not exist. Please check the "+
                              "aermod folder for any *.TMP or *.ERR files that may indicate the problem.")
            

        if success == True:
             
            # Move aermod.inp, aermod.out, and all post files to the facility folder.
            
            # First see if these files are alrezdy in the output folder. If so, delete them.
            if os.path.isfile(fac_folder + 'aermod_lead.out'):
                os.remove(fac_folder + 'aermod_lead.out')

            if os.path.isfile(fac_folder + 'aermod_lead.inp'):
                os.remove(fac_folder + 'aermod_lead.inp')

            extension = 'pst'
            for item in os.listdir(fac_folder):
                item_path = os.path.join(fac_folder, item)
    
                # Check if the item is a file and has the desired extension
                if os.path.isfile(item_path) and item.endswith(extension):
                    os.remove(item_path)

            # Now move files

            # move aermod.out file
            new_name = os.path.join(fac_folder, 'aermod_lead.out')
            shutil.move(output, new_name)
            
            # move aermod.inp file
            inpfile = os.path.join("aermod", "aermod.inp")
            new_name = os.path.join(fac_folder, 'aermod_lead.inp')
            shutil.move(inpfile, new_name)

            # move all post files and create the inputfiles.txt file needed by LEADPOST
            post_input_name = os.path.join('leadpost', 'inputfiles.txt')
            with open(post_input_name, "w") as postfile:
                extension = 'pst'
                for item in os.listdir('aermod'):
                    item_path = os.path.join('aermod', item)
        
                    # Check if the item is a file and has the desired extension
                    if os.path.isfile(item_path) and item.endswith(extension):
                        new_name = os.path.join(fac_folder, item)
                        shutil.move(item_path, new_name)
                        postfile.write('"../'+new_name+'"\n') 
                
        else:
            # Aermod failed. Move aermod.inp and aermod.out and rename.

            # move aermod.out file
            new_name = os.path.join(fac_folder, 'aermod_lead.out')
            shutil.move(output, new_name)
            
            # move aermod.inp file
            inpfile = os.path.join("aermod", "aermod.inp")
            new_name = os.path.join(fac_folder, 'aermod_lead.inp')
            shutil.move(inpfile, new_name)
            
        return success


    def check_LeadPost_run(self, fac_folder):

        # Did user abort?
        if self.abort.is_set():
            success = False
            self.model.leadpost = False
            return success
        
        ## Check for successful LEADPOST run:
        outlog = os.path.join("leadpost", "lead.log")
        if os.path.exists(outlog):
            check = open(outlog, 'r')
            message = check.read()
            now = datetime.now().time()
            current_time = now.strftime("%H:%M:%S")
            if 'Calculating maximum concentrations' in message:
                success = True
                self.model.leadpost = True          
                Logger.logMessage("LEADPOST ran successfully. Ended at time " + current_time)
            else:
                success = False
                self.model.leadpost = False
                Logger.logMessage("LEADPOST ran unsuccessfully. Please check the "+
                                  "lead.log file in the "  + str(self.facilityId) + 
                                  " output folder. Ended at time "+ current_time)
            check.close()
        else:
            # lead.log does not exist
            success = False
            self.model.leadpost = False         
            Logger.logMessage("LEADPOST finished but the lead.log file does not exist. Please check the "+
                              "leadpost folder for any *.TMP or *.ERR files that may indicate the problem.")
            

        if success == True:
             
            # Move all LEADPOST output files to the facility folder.
            # Replace if one is already in there othewrwise will throw error

            # Move log file
            if os.path.isfile(os.path.join(fac_folder, 'lead.log')):
                os.remove(os.path.join(fac_folder, 'lead.log'))
            new_name = os.path.join(fac_folder, 'lead.log')
            shutil.move(outlog, new_name)
                
            # Move lead.out file
            leadout = os.path.join("leadpost", "lead.out")
            if os.path.isfile(os.path.join(fac_folder, 'lead.out')):
                os.remove(os.path.join(fac_folder, 'lead.out'))
            new_name = os.path.join(fac_folder, 'lead.out')
            shutil.move(leadout, new_name)

            # Move inputfiles.txt file
            old_name = os.path.join("leadpost", "inputfiles.txt")
            if os.path.isfile(os.path.join(fac_folder, 'inputfiles.txt')):
                os.remove(os.path.join(fac_folder, 'inputfiles.txt'))
            new_name = os.path.join(fac_folder, 'inputfiles.txt')
            shutil.move(old_name, new_name)

            # Move output files
            leadconc = os.path.join("leadpost", self.monthconc_output)
            if os.path.isfile(os.path.join(fac_folder, self.monthconc_output)):
                os.remove(os.path.join(fac_folder, self.monthconc_output))
            new_name = os.path.join(fac_folder, self.monthconc_output)
            shutil.move(leadconc, new_name)

            leadmaxconc = os.path.join("leadpost", self.monthmaxconc_output)
            if os.path.isfile(os.path.join(fac_folder, self.monthmaxconc_output)):
                os.remove(os.path.join(fac_folder, self.monthmaxconc_output))
            new_name = os.path.join(fac_folder, self.monthmaxconc_output)
            shutil.move(leadmaxconc, new_name)
            
            
        else:
            # LEADPOST failed.

            # move lead.log file
            new_name = os.path.join(fac_folder, 'lead.log')
            shutil.move(outlog, new_name)
            
            
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

        # Round utm coordinates to integers
        if len(plotf_df) > 0:
            plotf_df.utme = plotf_df.apply(lambda row: normal_round(row[utme]), axis=1)
            plotf_df.utmn = plotf_df.apply(lambda row: normal_round(row[utmn]), axis=1)

        return plotf_df



    def readmaxf(self, apfile, runtype):
        
        if runtype == 0:
            # No deposition
            aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,aresult,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9], 
                converters={utme:np.float64,utmn:np.float64,aresult:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str
                       ,concdate:np.str},
                comment='*')             
        elif runtype == 1:
            # Wet and Dry deposition
            aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,aresult,adry,awet,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10,11], 
                converters={utme:np.float64,utmn:np.float64,aresult:np.float64,adry:np.float64,
                            awet:np.float64,elev:np.float64,hill:np.float64,flag:np.float64,
                            avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str,concdate:np.str},
                comment='*')                       
        elif runtype == 2:
            # Dry only deposition
            aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,aresult,adry,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10], 
                converters={utme:np.float64,utmn:np.float64,aresult:np.float64,adry:np.float64,
                            elev:np.float64,hill:np.float64,flag:np.float64,
                            avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str,concdate:np.str},
                comment='*')                       
        elif runtype == 3:
            # Wet only deposition
            aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,aresult,awet,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9,10], 
                converters={utme:np.float64,utmn:np.float64,aresult:np.float64,awet:np.float64,
                            elev:np.float64,hill:np.float64,flag:np.float64,
                            avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str,concdate:np.str},
                comment='*')
 
        # Round utm coordinates to integers
        aplot_df.utme = aplot_df.apply(lambda row: normal_round(row[utme]), axis=1)
        aplot_df.utmn = aplot_df.apply(lambda row: normal_round(row[utmn]), axis=1)

        return aplot_df
               

    def process_outputs(self, fac_folder, plot_df):
           
            # check length of fac_folder
            
            
            #process outputs
            Logger.logMessage("Processing Outputs for " + self.facilityId)
            outputProcess = Process_outputs(fac_folder, self.facilityId, 
                                            self.model, self.prep_fac,
                                            self.runstream, plot_df, self.abort)
            outputProcess.process()
                        
            #if successful save state
#            self.model.save.save_model(self.facilityId)
            
            pace =  str(round((time.time()- self.start)/60, 2)) + ' minutes'
            Logger.logMessage("Finished calculations for " + self.facilityId + 
                              ' after ' + pace + "\n")
            
            
    def adjustPostfiles(self, fac_folder):
        
        # Conversion factor for tons/year to ug/m3
        cf = 2000*0.4536/3600/8760
        
        # Get list of all post files in the facility folder
        post_list = []
        for filename in os.listdir(fac_folder):
            if filename.endswith('pst') and os.path.isfile(os.path.join(fac_folder, filename)):
                post_list.append(filename)
                        
        #--- Load each post file into a dataframe and multiply by the lead compounds emissions

        # The ALL Aermod source category will need a sum of all lead emissions
        allemis = self.model.leademis_df['emis_tpy'].sum()

        for pfile in post_list:
            pfile_path = os.path.join(fac_folder, pfile)
            
            # save the header of the post file
            header_rows = []
            with open(pfile_path, 'r') as file:
                for line in file:
                    if line.strip().startswith('*'):
                        header_rows.append(line)
            
            # load into dataframe
            postf_df = pd.read_table(pfile_path, delim_whitespace=True, header=None, 
                names=['x','y','avgconc','elev','hill','flag','avg_time','source_id','date','net_id'],
                usecols=[0,1,2,3,4,5,6,7,8,9], 
                dtype={'x':np.float64,'y':np.float64,'avgconc':np.float64,'elev':np.float64,'hill':np.float64
                       ,'flag':np.float64,'avg_time':np.str,'source_id':np.str,'date':np.int64,'net_id':np.str},
                comment='*')
                        
            # multiply by lead emissions (tpy)
            srcid = postf_df.iloc[0,7]
            if srcid == 'ALL':
                leademis_tpy = allemis
            else:
                leademis_tpy = (self.model.leademis_df[self.model.leademis_df['source_id']
                                                   ==srcid]['emis_tpy'].iloc[0])
            postf_df['avgconc'] = postf_df['avgconc'] * leademis_tpy * cf
            
            # write back to post file
            with open(pfile_path, 'w') as outfile:
                for row in header_rows:
                    outfile.write(row)
                    
                for index, row in postf_df.iterrows():
                    formatted_line = []
                    formatted_line.append(f"{row['x']:>14.5f}")
                    formatted_line.append(f"{row['y']:>14.5f}")
                    formatted_line.append(f"{row['avgconc']:>14.5f}")
                    formatted_line.append(f"{row['elev']:>9.2f}")
                    formatted_line.append(f"{row['hill']:>9.2f}")
                    formatted_line.append(f"{row['flag']:>9.2f}")
                    formatted_line.append(f"{row['avg_time']:>8}")
                    formatted_line.append(f"{row['source_id']:>10}")
                    formatted_line.append(f"{row['date']:>10}")
                    formatted_line.append(f"{row['net_id']:>10}")
                    outfile.write("".join(formatted_line) + '\n')
                    
        Logger.logMessage("Ready to run LEADPOST for facility " + self.facilityId + "\n")
                    
                    
                    
                    
                    
            
            

                
