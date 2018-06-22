import Hem4_Output_Processing as po
import create_facililty_kml as fkml
import os

class FacilityRunner():

    def __init__(self, id, messageQueue):
        self.facilityId = id
        self.messageQueue = messageQueue
        
    def run(self):

        self.messageQueue.put("\nRunning facility " + str(num) + " of " + str(len(fac_list)))

        result = pass_ob.prep_facility(self.facilityId)

        self.messageQueue.put("Building Runstream File for " + self.facilityId)

        result.build()

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

        #self.loc["textvariable"] = "Aermod complete for " + facid

        ## Check for successful aermod run:
        check = open('aermod.out','r')
        message = check.read()
        if 'AERMOD Finishes UN-successfully' in message:
            success = False
            self.messageQueue.put("Aermod ran unsuccessfully. Please check the error section of the aermod.out file.")

            #increment facility count
            num += 1
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
            process = po.Process_outputs(self.facilityId, pass_ob.haplib_df, result.hapemis, fac_folder, pass_ob.innerblks, pass_ob.outerblks, result.polar_df)
            process.process()

            #create facility kml
            self.messageQueue.put("Writing KML file for " + self.facilityId)
            facility_kml = fkml.facility_kml(self.facilityId, result.cenlat, result.cenlon, fac_folder)

            pace =  str(time.time()-start) + 'seconds'

            self.messageQueue.put("Finished calculations for " + self.facilityId + ' after' + pace + "\n")


            #increment facility count
            num += 1