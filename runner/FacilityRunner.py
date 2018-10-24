import Hem4_Output_Processing as po
import os
import time
import subprocess
import shutil

from FacilityPrep import FacilityPrep
from log.Logger import Logger

class FacilityRunner():

    def __init__(self, id, model, abort):
        self.facilityId = id
        self.model = model
        self.abort = abort
        
    def run(self):

        # Start the clock for benchmarking
        start = time.time()

        prep = FacilityPrep(self.model)
        Logger.logMessage("Building runstream for facility " + self.facilityId)
        runstream = prep.createRunstream(self.facilityId)

        Logger.logMessage("Building Runstream File for " + self.facilityId)
        runstream.build()

        #create fac folder
        fac_folder = "output/"+ self.facilityId + "/"
        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)

        #run aermod
        Logger.logMessage("Running Aermod for " + self.facilityId)

        # Start aermod asynchronously and then monitor it, with the possibility
        # of terminating it midstream (i.e. if the thread is asked to die...)

        p = subprocess.Popen(['aermod.exe', 'aermod.inp'])
        subRunning = True
        while subRunning:
            if self.abort.is_set():
                Logger.logMessage("Terminating aermod process...")
                p.terminate()
                return
            else:
                time.sleep(0.5)
                subRunning = (p.poll() is None)

        ## Check for successful aermod run:
        check = open('aermod.out','r')
        message = check.read()
        if 'AERMOD Finishes UN-successfully' in message:
            success = False
            Logger.logMessage("Aermod ran unsuccessfully. Please check the error section of the aermod.out file.")
        else:
            success = True
            Logger.logMessage("Aermod ran successfully.")
        check.close()

        if success == True:


            #move aermod.out to the fac output folder
            #replace if one is already in there othewrwise will throw error

            if os.path.isfile(fac_folder + 'aermod.out'):
                os.remove(fac_folder + 'aermod.out')
                shutil.move('aermod.out', fac_folder)

            else:
                shutil.move('aermod.out', fac_folder)

            #process outputs
            Logger.logMessage("Processing Outputs for " + self.facilityId)
            outputProcess = po.Process_outputs(fac_folder, self.facilityId, self.model, prep, runstream, self.abort)
            outputProcess.process()

            pace =  str(time.time()-start) + 'seconds'
            Logger.logMessage("Finished calculations for " + self.facilityId + ' after' + pace + "\n")