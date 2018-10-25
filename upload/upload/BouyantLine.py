#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 20:34:16 2018

@author: d
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class BouyantLine(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        
    def createDataframe(self):
        
        emisloc_df = self.dependency
        
        multibouy_df = self.readFromPath("fac_id", "avgbld_len", "avgbld_hgt", 
                                         "avgbld_wid", "avglin_wid", "avgbld_sep"
                                         , "avgbuoy"),{0:str}
                                         
        #check for unassigned bouyant line  
        check_bouyant_assignment = set(multibuoy_df['fac_id'])
        
        #get buoyant line facility list
        find_b = emisloc_df[emisloc_df['source_type'].upper() == 'B']
        bouyant_fac = find_b["fac_id"]
        
        if check_bouyant_assignment != bouyant_fac:
            bouyant_unassigned = (check_bouyant_assignment - bouyant_fac).tolist()
            
            messagebox.showinfo("Unassigned Bouyant Line parameters", "Bouyant" + 
                                " Line parameters for " + 
                                ", ".join(bouyant_unassigned) + " have not been" + 
                                " assigned. Please edit the 'source_type' column" + 
                                " in the Emissions Locations file.")
            
        else:
            
            self.log.append("Uploaded bouyant line parameters for " + 
                            " ".join(check_bouyant_assignment))
            
            self.dataframe = multibouy_df