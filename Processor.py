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

            try:
                runner = FacilityRunner(facid, self.model, self.abort)
                runner.run()

                # increment facility count
                num += 1
            except Exception as ex:

                fullStackInfo=''.join(traceback.format_exception(
                    etype=type(ex), value=ex, tb=ex.__traceback__))

                Logger.logMessage("An error occurred while running a facility:\n" + fullStackInfo)

        Logger.logMessage("HEM4 Modeling Completed. Finished modeling all" +
                          " facilities. Check the log tab for error messages."+
                          " Modeling results are located in the Output"+
                          " subfolder of the HEM4 folder.")
