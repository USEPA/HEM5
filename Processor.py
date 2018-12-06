import threading

from log import Logger
from runner.FacilityRunner import FacilityRunner
from writer.kml.KMLWriter import KMLWriter
import traceback

threadLocal = threading.local()

class Processor():

    abort = None
    def __init__ (self, model, abort):
        self.model = model
        self.abort = abort
        self.exception = None

    def abortProcessing(self):
        self.abort.set()

    def process(self):

        threadLocal.abort = False

        #create a Google Earth KML of all sources to be modeled
        kmlWriter = KMLWriter()
        if kmlWriter is not None:
            #kmlWriter.write_kml_emis_loc(self.model)
            pass

        Logger.logMessage("Preparing Inputs for " + str(
            self.model.facids.count()) + " facilities")

        fac_list = []
        for index, row in self.model.faclist.dataframe.iterrows():

            facid = row[0]
            fac_list.append(facid)
            num = 1

        Logger.log("The facilities ids being modeled:", fac_list, False)

        for facid in fac_list:

            if self.abort.is_set():
                Logger.logMessage("Aborting processing...")
                return

            #save version of this gui as is? constantly overwrite it once each facility is done?
            Logger.logMessage("Running facility " + str(num) + " of " +
                              str(len(fac_list)))

            success = False
            try:
                runner = FacilityRunner(facid, self.model, self.abort)
                runner.setup()

                
            except Exception as ex:

                self.exception = ex
                fullStackInfo=''.join(traceback.format_exception(
                    etype=type(ex), value=ex, tb=ex.__traceback__))

                message = "An error occurred while running a facility:\n" + fullStackInfo
                print(message)
                Logger.logMessage(message)
                
                
            else:
                ## if the try is successful this is where we would update the 
                # dataframes or cache the last processed facility so that when 
                # restart we know which faciltiy we want to start on
                # increment facility count
                num += 1
                success = True
                
                

        Logger.logMessage("HEM4 Modeling Completed. Finished modeling all" +
                          " facilities. Check the log tab for error messages."+
                          " Modeling results are located in the Output"+
                          " subfolder of the HEM4 folder.")

        return success
