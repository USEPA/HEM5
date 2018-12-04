#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018

@author: d
"""
from model.Model import fac_id
from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class Vegetation(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency

    def createDataframe(self):
        
        faclist_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = ["M01", "M02", "M03", "M04","M05", "M06", "M07", "M08", "M09","M10","M11", "M12"]
        self.strColumns = [fac_id]

        vegetation_df = self.readFromPath((fac_id, "M01", "M02", "M03", "M04",
                                      "M05", "M06", "M07", "M08", "M09","M10",
                                      "M11", "M12"))
        
        
        #check for unassigned veg
        
        check_veg_assignment = set(vegetation_df[fac_id])
        
        
        ## figure out how to get fac ids that have particle based on flag or index
        
        self.dataframe = vegetation_df