# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 11:21:13 2018

@author: dlindsey
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from model.Model import *
from upload.FacilityList import bldg_dw

section = 'section';
keyword = 'keyword';

class Downwash(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency

    def createDataframe(self):
        
        faclist_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = ["value_1","value_2","value_3","value_4","value_5","value_6","value_7","value_8",
                               "value_9","value_10","value_11","value_12","value_13","value_14","value_15","value_16",
                               "value_17","value_18","value_19","value_20","value_21","value_22","value_23","value_24",
                               "value_25", "value_26","value_27","value_28","value_29","value_30","value_31","value_32",
                               "value_33","value_34","value_35","value_36"]
        self.strColumns = [fac_id, section, keyword, source_id]

        downwash_df = self.readFromPath((fac_id, section, keyword,
                                      source_id, "value_1", "value_2",
                                      "value_3", "value_4", "value_5",
                                      "value_6", "value_7", "value_8",
                                      "value_9", "value_10", "value_11",
                                      "value_12", "value_13", "value_14",
                                      "value_15", "value_16", "value_17",
                                      "value_18", "value_19", "value_20",
                                      "value_21", "value_22", "value_23",
                                      "value_24", "value_25", "value_26",
                                      "value_27", "value_28", "value_29",
                                      "value_30", "value_31", "value_32",
                                      "value_33", "value_34", "value_35",
                                      "value_36"))
         
        #check for unassigned downwash
        check_downwash_assignment = set(downwash_df[fac_id])

        find_d = faclist_df[faclist_df[bldg_dw] == "Y"]
        d_fac = set(find_d[fac_id])
         
        if check_downwash_assignment != d_fac:
         downwash_unassigned = (check_downwash_assignment - d_fac).tolist()

         messagebox.showinfo("Unassigned building downwash", "Building" +
                            "downwash parameters for " +
                            ", ".join(downwash_unassigned) + " have not" +
                            " been assigned. Please edit the" +
                            " 'bldgdw' column in the Facilities List Option" +
                            " file.")

        else:

            self.log.append("Uploaded building downwash parameters for " +
                            " ".join(check_downwash_assignment))

        self.dataframe = downwash_df
             
         
        
         
         

