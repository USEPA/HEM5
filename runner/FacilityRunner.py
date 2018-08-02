import Hem4_Output_Processing as po
import os
import time
import subprocess
import shutil

from FacilityPrep import FacilityPrep
from writer.kml.KMLWriter import KMLWriter


class FacilityRunner():

    def __init__(self, id, messageQueue, model):
        self.facilityId = id
        self.messageQueue = messageQueue
        self.model = model
        
    def run(self):

        # Start the clock for benchmarking
        start = time.time()

        prep = FacilityPrep(self.model)
        runstream = prep.createRunstream(self.facilityId)

        self.messageQueue.put("Building Runstream File for " + self.facilityId)
        runstream.build()

        #create fac folder
        fac_folder = "output/"+ self.facilityId + "/"
        if os.path.exists(fac_folder):
            pass
        else:
            os.makedirs(fac_folder)

        #run aermod
        self.messageQueue.put("Running Aermod for " + self.facilityId)
        args = "aermod.exe aermod.inp"
        subprocess.call(args, shell=False)

        ## Check for successful aermod run:
        check = open('aermod.out','r')
        message = check.read()
        if 'AERMOD Finishes UN-successfully' in message:
            success = False
            self.messageQueue.put("Aermod ran unsuccessfully. Please check the error section of the aermod.out file.")
        else:
            success = True
            self.messageQueue.put("Aermod ran successfully.")
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
            self.messageQueue.put("Processing Outputs for " + self.facilityId)
            outputProcess = po.Process_outputs(fac_folder, self.facilityId, self.model, prep, runstream)
            outputProcess.process()

            #create facility kml
            self.messageQueue.put("Writing KML file for " + self.facilityId)
            kmlWriter = KMLWriter()
            kmlWriter.write_facility_kml(self.facilityId, runstream.cenlat, runstream.cenlon, fac_folder)

            pace =  str(time.time()-start) + 'seconds'
            self.messageQueue.put("Finished calculations for " + self.facilityId + ' after' + pace + "\n")