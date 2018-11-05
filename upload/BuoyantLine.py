#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 20:34:16 2018

@author: d
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class BuoyantLine(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        
    def createDataframe(self):
        
        emisloc_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = ["avgbld_len","avgbld_hgt","avgbld_wid","avglin_wid","avgbld_sep","avgbuoy"]
        self.strColumns = ["fac_id"]

        multibuoy_df = self.readFromPath(
            ("fac_id", "avgbld_len", "avgbld_hgt", "avgbld_wid", "avglin_wid", "avgbld_sep", "avgbuoy"))
                                         
        #check for unassigned buoyant line  
        check_buoyant_assignment = set(multibuoy_df['fac_id'])
        
        #get buoyant line facility list
        find_b = emisloc_df[emisloc_df['source_type'] == 'B']
        buoyant_fac = set(find_b["fac_id"])
        
        if check_buoyant_assignment != buoyant_fac:
            buoyant_unassigned = (check_buoyant_assignment - buoyant_fac).tolist()
            
            messagebox.showinfo("Unassigned buoyant Line parameters", "buoyant" + 
                                " Line parameters for " + 
                                ", ".join(buoyant_unassigned) + " have not been" + 
                                " assigned. Please edit the 'source_type' column" + 
                                " in the Emissions Locations file.")
            
        else:
            
            self.log.append("Uploaded buoyant line parameters for " + 
                            " ".join(check_buoyant_assignment))
            
            self.dataframe = multibuoy_df