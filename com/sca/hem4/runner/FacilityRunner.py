import os
import time
import subprocess
import shutil
from com.sca.hem4 import OutputProcessing as po
from com.sca.hem4.FacilityPrep import FacilityPrep
from com.sca.hem4.log import Logger
from com.sca.hem4.DepositionDepletion import sort
from com.sca.hem4.model.Model import fac_id


class FacilityRunner():

    def __init__(self, id, model, abort):
        self.facilityId = id
        self.model = model
        self.abort = abort
        self.start = time.time()
        
    
    def setup(self):
        
        #put phase in run_optns
        ## need to fix this not pulling phase out correctly
        fac = self.model.faclist.dataframe.loc[self.model.faclist.dataframe[fac_id] == self.facilityId]
        print('fac list:', fac['phase'].tolist()[0])

        if 'nan' in fac['phase'].tolist()[0]:
            self.model.model_optns['phase'] = None
            print(self.model.model_optns['phase'])

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

        #Single run model options
        if self.model.model_optns['phase'] != 'B':

            if self.model.model_optns['phase'] != None:
                phase = sort(fac)

            else:
                phase = {'phase': None, 'settings': None}

            #create runstream
            self.runstream = self.prep_fac.createRunstream(self.facilityId, phase)

            #run aermod
            self.run(fac_folder)

            #check aermod run and move aer.out file to facility folder
            check = self.check_run(fac_folder)

            if check == True:

                #process outputs for single facility -- turn off for particle
                self.process_outputs(fac_folder)

        else:
            #double run needs to create subfolder for particle and vapor
            #also store the runstream objects for later use in processing

            #let the sort get both phases then loop through each
            phases = sort(fac)
            runstreams = []


            for r in phases:

                #log label for particle and vapor so easy to track

                #Logger.logMessage(r + " run:")
                print(phases)

                #store run in subfolder
                sub_folder = fac_folder + r['phase'] +"/"
                if os.path.exists(sub_folder):
                    pass
                else:
                    os.makedirs(sub_folder)
                
                #run individual phase
                self.runstream = self.prep_fac.createRunstream(self.facilityId, r)
                
                #store runstream objects for later use
                runstreams.append(self.runstream)
                
                self.run(sub_folder)
             
                check = self.check_run(sub_folder)
                
                #currently process outputs has not been made for a double run
    
    def prep(self):
        
        prep = FacilityPrep(self.model)
        
        Logger.logMessage("Building runstream for facility " + self.facilityId)
        
        return prep
            

    def run(self, fac_folder):

        #run aermod
        Logger.logMessage("Running Aermod for " + self.facilityId)

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
                
                
                
    def check_run(self, fac_folder):

        ## Check for successful aermod run:
        output = os.path.join("aermod", "aermod.out")
        check = open(output, 'r')
        message = check.read()
        if 'AERMOD Finishes UN-successfully' in message:
            success = False
            Logger.logMessage("Aermod ran unsuccessfully. Please check the "+
                              "error section of the aermod.out file.")
        else:
            success = True
            Logger.logMessage("Aermod ran successfully.")
        check.close()

        if success == True:

            #move aermod.out to the fac output folder
            #replace if one is already in there othewrwise will throw error

            if os.path.isfile(fac_folder + 'aermod.out'):
                os.remove(fac_folder + 'aermod.out')
                shutil.move(output, fac_folder)

            else:
                shutil.move(output, fac_folder)
                self.model.save.save_model(self.facilityId)
                
            return success


    def process_outputs(self, fac_folder):
           
            # check length of fac_folder
            
            
            #process outputs
            Logger.logMessage("Processing Outputs for " + self.facilityId)
            outputProcess = po.Process_outputs(fac_folder, self.facilityId, 
                                               self.model, self.prep_fac,
                                               self.runstream, self.abort)
            outputProcess.process()
            
            

            pace =  str(time.time()- self.start) + 'seconds'
            Logger.logMessage("Finished calculations for " + self.facilityId + 
                              ' after' + pace + "\n")