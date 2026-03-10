import os
import shutil
import threading
from datetime import datetime

import pandas as pd

from com.sca.hem4.SaveState import SaveState
from com.sca.hem4.log.Logger import Logger
from com.sca.hem4.runner.UserConcsRunner import UserConcsRunner
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.writer.excel.FacilityCancerRiskExp import FacilityCancerRiskExp
from com.sca.hem4.writer.excel.FacilityTOSHIExp import FacilityTOSHIExp
from com.sca.hem4.inputsfolder.InputsPackager import InputsPackager
from com.sca.hem4.upload.FileUploader import FileUploader

import traceback
from collections import defaultdict
from tkinter import messagebox


threadLocal = threading.local()

class userconcsProcessor():

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

        success = False

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
            messagebox.showinfo('Warning', 'The acute benchmark column names have been'
                              + ' changed in the "Dose_Response_Library.xlsx" file. These names'
                              + ' will be used in the acute outputs.')
            
            Logger.logMessage('\nWarning: The acute benchmark column names have been'
                              + ' changed in the "Dose_Response_Library.xlsx" file. These names'
                              + ' will be used in the acute outputs.\n')
        
        # Store the acute names in the model class
        self.model.acute_names = haplib_acute_names_real

        
        Logger.logMessage("RUN GROUP: " + self.model.group_name)
        
        threadLocal.abort = False
            
        if self.abort.is_set():
            Logger.logMessage('HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            messagebox.showinfo('Run Canceled', 'HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            self.nav.abortLabel.destroy()
            success = False
            return success
                                      
        try:
            runner = UserConcsRunner(self.model, self.abort)
            runner.interpolate()
            runner.formatDF()
            runner.createOutputs()

        except BaseException as ex:
                
            self.exception = ex
            fullStackInfo=traceback.format_exc()   
            message = "An error occurred while running HEM. Error message says:\n" + fullStackInfo
            Logger.logMessage(message)
            return success
            
        success = True
                        
                
         # move the log file to the run dir and re-initialize
        Logger.archiveLog(self.model.rootoutput)
        Logger.initializeLog()
        
        if self.abort.is_set():
            
            Logger.logMessage('HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            messagebox.showinfo('Run Canceled', 'HEM RUN GROUP: ' + str(self.model.group_name) + ' canceled')
            self.nav.abortLabel.destroy()
                    
        else:
            
            Logger.logMessage("HEM completed")
            messagebox.showinfo('Modeling Completed', "HEM completed")

        
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
