import os
import shutil
import threading
from datetime import datetime

import pandas as pd

from com.sca.hem4.SaveState import SaveState
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.runner.FacilityRunner import FacilityRunner
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.writer.excel.FacilityCancerRiskExp import FacilityCancerRiskExp
from com.sca.hem4.writer.excel.FacilityTOSHIExp import FacilityTOSHIExp
from com.sca.hem4.writer.kml.KMLWriter import KMLWriter
from com.sca.hem4.inputsfolder.InputsPackager import InputsPackager
from com.sca.hem4.upload.FileUploader import FileUploader

import traceback
from collections import defaultdict
import uuid

from tkinter import messagebox


threadLocal = threading.local()

class Processor():

    abort = None
    def __init__ (self, nav, model, abort):
        self.nav = nav
        self.model = model
        self.abort = abort
        self.exception = None
        print("processor starting")

    def abortProcessing(self):
        self.abort.set()

    def process(self):

        try:
            # create Inputs folder
            inputspkgr = InputsPackager(self.model.rootoutput, self.model)
            inputspkgr.createInputs()
          
        except BaseException as ex:
            print(ex)

        # If using Census data, Load the national census data into a polars lazyframe for future querying
        if 'altrec' not in self.model.dependencies:
            self.uploader = FileUploader(self.model)
            success = self.uploader.uploadLibrary("census")
            if success:
                Logger.logMessage('Uploaded the Census file')
            else:
                messagebox.showinfo('Error', "Invalid Census file. Check log for details.")
                return success

       
        Logger.logMessage("RUN GROUP: " + self.model.group_name)
        

        threadLocal.abort = False

        
        #create a Google Earth KML of all sources to be modeled
        try:
            kmlWriter = KMLWriter()
            if kmlWriter is not None:
                kmlWriter.write_kml_emis_loc(self.model)
                Logger.logMessage("KMZ for all sources completed")

        except BaseException as ex:
                self.exception = ex
                fullStackInfo=traceback.format_exc()
                message = "An error occurred while trying to create the KML file of all facilities:\n" + fullStackInfo
                Logger.logMessage(message)
           
        else:
          
            print(str(self.model.facids.count()))
            
            Logger.logMessage("Preparing Inputs for " + str(self.model.facids.count()) + " facilities\n")
            
           
            fac_list = []
            for index, row in self.model.faclist.dataframe.iterrows():
                
                facid = row[0]
                #print(facid)
                fac_list.append(facid)
                num = 1
    
    #        Logger.logMessage("The facility ids being modeled: , False)
            Logger.logMessage("The facility ids being modeled: " + ", ".join(fac_list))
               
            success = False
    
            # Create output files with headers for any source-category outputs that will be appended
            # to facility by facility. These won't have any data for now.
            self.createSourceCategoryOutputs()
            
            self.completed = []
            self.skipped = []
            for facid in fac_list:
                print(facid)
                if self.abort.is_set():
                    Logger.logMessage('HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
                    messagebox.showinfo('Run Canceled', 'HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
                    self.nav.abortLabel.destroy()
#                    Logger.logMessage("Aborting processing...")
                    success = False
                    return success
                
                
                
                #save version of this gui as is? constantly overwrite it once each facility is done?
                Logger.logMessage("Running facility " + str(num) + " of " + str(len(fac_list)))
                
                success = False
                
                
                try:
                    runner = FacilityRunner(facid, self.model, self.abort)
                    runner.setup()

                except BaseException as ex:

                    # Check for bad Internet connection which aborts the HEM run
                    if 'There is no Internet connection' in str(ex):
                        messagebox.showinfo("No Internet connection", "Your computer is not connected to the Internet and this run needs elevation data from the USGS server." \
                                            " This HEM run will stop." \
                                            " One option is to re-run this Run Group with elevation turned off." \
                                            " More detail about this error is available in the log.")
                        fullStackInfo = traceback.format_exc()
                        Logger.logMessage("No Internet connection.\n" \
                                          " Aborting this HEM run.\n" \
                                          " Detailed error message: \n\n" + fullStackInfo)                

                        self.abortProcessing()
                        break
                        
                                        
                    # Check for USGS elevation server error which aborts the HEM run
                    if str(ex) == "USGS elevation server unavailable":
                        messagebox.showinfo("Cannot obtain elevation data", "Your computer was unable to obtain elevation data for this model run." \
                                            " This HEM run will stop. This problem may be due to your internet connection or the elevation data not being available from the USGS." \
                                            " Your options are to run this run group with no elevation or to use the off-line elevation method." \
                                            " More detail about this error is available in the log.")
                        fullStackInfo = traceback.format_exc()
                        Logger.logMessage("Cannot obtain elevation data.\n" \
                                          " Aborting this HEM run.\n" \
                                          " Detailed error message: \n\n" + fullStackInfo)                

                        self.abortProcessing()
                        break
                        
                    self.exception = ex
                    fullStackInfo=traceback.format_exc()   
                    message = "An error occurred while running a facility and facility was skipped:\n" + fullStackInfo
                    Logger.logMessage(message)
                    
                    self.skipped.append(facid)
                    num += 1
                    continue

                    ## if the try is successful this is where we would update the 
                    # dataframes or cache the last processed facility so that when 
                    # restart we know which faciltiy we want to start on
                    # increment facility count
                
                  
                try:
                    self.model.aermod
                    
                except:
                    
                    pass
                
                else:
                    if self.model.aermod == False:
                        
                        fac_folder = self.model.rootoutput + str(facid)
                           
                        # move plotfile.plt file
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
                        try:
                            output = os.path.join("aermod", "aermod.out")
                            shutil.move(output, fac_folder)
                        except:
                            pass
                        
                        # move aermod.inp file
                        try:
                            inpfile = os.path.join("aermod", "aermod.inp")
                            shutil.move(inpfile, fac_folder)
                        except:
                            pass
                        
                        try:
                            pltfile = os.path.join("aermod", plt_version)
                            shutil.move(pltfile, fac_folder)
                        except:
                            pass
                        
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
                                    
                        self.skipped.append(facid)
                        self.model.aermod = None
                        
                    else:
                        self.completed.append(facid)
                    
                num += 1
                success = True
                

                #reset model options aftr facility
                self.model.model_optns = defaultdict()
                
#                try:  
#                    self.model.save.remove_folder()
#                except:
#                    pass
                
                
         # move the log file to the run dir and re-initialize
        Logger.archiveLog(self.model.rootoutput)
        Logger.initializeLog()
        
        if self.abort.is_set():
            
            
            Logger.logMessage('HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            messagebox.showinfo('Run Canceled', 'HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            self.nav.abortLabel.destroy()
                    
        elif len(self.skipped) == 0:
            
#            self.model.save.remove_folder()
            
            Logger.logMessage("HEM Modeling Completed. Finished modeling all" +
                          " facilities. Check the log tab for error messages."+
                          " Modeling results are located in the Output"+
                          " subfolder of the HEM folder.")
            
            messagebox.showinfo('Modeling Completed', "HEM Modeling Completed. Finished modeling all" +
                          " facilities. Check the log tab for error messages."+
                          " Modeling results are located in the Output"+
                          " subfolder of the HEM folder.")

        else:

#            self.model.save.remove_folder()
            
            Logger.logMessage("HEM completed " + str(len(self.completed)) + 
                              " facilities and skipped " + str(len(self.skipped))+ 
                              " facilities. Modeling not completed for: " + "\n ".join(self.skipped))
            messagebox.showinfo('Modeling Completed', "HEM completed " + str(len(self.completed)) + 
                              " facilities and skipped " + str(len(self.skipped))+ 
                              " facilities. Modeling not completed for: " + "\n ".join(self.skipped))

            
            # output skipped facilities to csv
            skipped_path = self.model.rootoutput + 'Skipped_Facilities.xlsx'
            skipped_df = pd.DataFrame(self.skipped, columns=['Facility'])
            print(skipped_df)
            
            skipped_df.to_excel(skipped_path, index=False)

       
        # Clean up any cache file created by the elevation functions
        if os.path.exists('cache'):
            for file in os.scandir('cache'):
                os.remove(file.path)
        
        self.nav.reset_gui()

        
        return success

    def createSourceCategoryOutputs(self):
        
        # Create Facility Max Risk and HI file
        fac_max_risk = FacilityMaxRiskandHI(self.model.rootoutput, None, self.model, None, None)
        fac_max_risk.write()

        
        # Create Facility Cancer Risk Exposure file
        fac_canexp = FacilityCancerRiskExp(self.model.rootoutput, None, self.model, None)
        fac_canexp.write()
                
        # Create Facility TOSHI Exposure file
        fac_hiexp = FacilityTOSHIExp(self.model.rootoutput, None, self.model, None)
        fac_hiexp.write()
