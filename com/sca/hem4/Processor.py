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
from com.sca.hem4.support.ElevHill import ElevHill

import traceback
from collections import defaultdict
import uuid
import time

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

        # ----------------------------------------------------------------------------------
        # The acute benchmark column names will be used in acute outputs.
        # The user can change them in the dose reponse file, so record them and 
        # compare to the default names to let the user know if they have been changed.
        # ----------------------------------------------------------------------------------
        haplib_acute_names_default = ["AEGL-1  (1-hr)\n(mg/m3)",
                                           "AEGL-2  (1-hr)\n(mg/m3)",
                                           "ERPG-1\n(mg/m3)",
                                           "ERPG-2\n(mg/m3)",
                                           "Acute REL\n(mg/m3)"]
        
        haplib_header = pd.read_excel("resources/Dose_Response_Library.xlsx", nrows=1)
        haplib_acute_names_real = haplib_header.columns.tolist()[-5:]

        # Let the user know if the acute benchmark column names have been changed in the
        # dose reponse file        
        if not haplib_acute_names_default == haplib_acute_names_real:
            messagebox.showinfo('Warning',"You have changed acute benchmark column header(s) in the 'Dose_Response_Library.xlsx' file. These benchmark names will be used to label the acute outputs for every facility in your run group, for which you chose to model acute impacts. HEM uses a one-hour acute averaging period by default. If your acute benchmark of interest for this run is based on a different averaging period, you should change the modeling options to that acute averaging period (in the 'hours' field of the 'Facility_List_Options.xlsx' file). Note that the averaging period you choose will be used to compute acute concentrations that will be compared to every acute benchmark for that facility, so you may wish to perform multiple HEM runs with different averaging periods.")
            
            Logger.logMessage('\nWarning: You have changed acute benchmark column header(s) in the "Dose_Response_Library.xlsx" file. These benchmark names will be used to label the acute outputs for every facility in your run group, for which you chose to model acute impacts. HEM uses a one-hour acute averaging period by default. If your acute benchmark of interest for this run is based on a different averaging period, you should change the modeling options to that acute averaging period (in the “hours” field of the “Facility_List_Options.xlsx” file). Note that the averaging period you choose will be used to compute acute concentrations that will be compared to every acute benchmark for that facility, so you may wish to perform multiple HEM runs with different averaging periods.\n')
        
        # Store the acute names in the model class
        self.model.acute_names = haplib_acute_names_real

        
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
                        
            Logger.logMessage("There are " + str(self.model.facids.count()) + " facilities to model\n")
            
           
            fac_list = []
            for index, row in self.model.faclist.dataframe.iterrows():
                
                facid = row.iloc[0]
                fac_list.append(facid)
    
            Logger.logMessage("The facility ids to model are: " + ", ".join(fac_list))
               
            success = False
    
            # Create output files with headers for any source-category outputs that will be appended
            # to facility by facility. These won't have any data for now.
            self.createSourceCategoryOutputs()
            
            self.completed = []
            self.skipped = []
            
            #-------------Iterrate over all facilities-------------------------
            num = 0
            for index, row in self.model.faclist.dataframe.iterrows():
                
                num+=1
                facid = row['fac_id']
                
                if self.abort.is_set():
                    Logger.logMessage('HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
                    messagebox.showinfo('Run Canceled', 'HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
                    self.nav.abortLabel.destroy()
                    success = False
                    return success
                
                #save version of this gui as is? constantly overwrite it once each facility is done?
                Logger.logMessage("Preparing to model facility " + str(num) + " of " + str(len(fac_list)))
                
                if row['elev'] == 'Y':
                    # This facility will use elevations.
                    # Confirm that an Internet connection is available. If there is not, then keep
                    # checking every minute indefinitely. Report progress to the log.
                    gotInternet = ElevHill.isInternet()
                    if gotInternet == False:
                        # No Internet. Keep checking until there is.
                        while not gotInternet:
                            gotInternet = ElevHill.isInternet()
                            if gotInternet == False:
                                currtime = datetime.now().strftime("%H:%M:%S")
                                message = "No Internet connection to retrieve elevations. Will try again in 1 minute. \n" \
                                          + "Click Exit to stop this loop. \n" \
                                          + "Current time is: " + currtime + "\n"
                                Logger.logMessage(message)
                                time.sleep(60)
                        # Internet has returned. Start over.
                        Logger.logMessage("Internet connection has returned. Will retrieve elevations.\n")
                
                success = False
                                
                try:
                                        
                    runner = FacilityRunner(facid, self.model, self.abort)
                    if self.model.faclist.dataframe.loc[self.model.faclist.dataframe['fac_id']
                                                        ==facid]['leadYN'].iloc[0].upper() == 'N':
                        # no special lead modeling
                        runner.setup()
                    else:
                        # Run Aermod twice - once for lead and once for all pollutants
                        runner.setupLead()
                        runner.setup()

                except BaseException as ex:                        
                                                                
                    self.exception = ex
                    fullStackInfo=traceback.format_exc()   
                    message = "An error occurred while running a facility and facility was skipped:\n" + fullStackInfo
                    Logger.logMessage(message)
                    
                    self.skipped.append(facid)
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
                    
                success = True
                

                #reset model options and runstreasm values after facility
                self.model.model_optns = defaultdict()
                self.model.runstream_reset()
                
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
