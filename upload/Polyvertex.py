#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 00:34:57 2018

@author: d
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class Polyvertex(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)

   def createDataframe(self): 
       
       emisloc_df = dependency;
        
       
       
        #POLYVERTEX excel to dataframe
        multipoly_df = self.readFromPath("fac_id","source_id","location_type",
                                         "lon","lat","utmzone","numvert","area",
                                         "fipstct"),{0:str, 1:str, 2:str, 5:str}
        
        #check for unassigned polyvertex
        check_poly_assignment = set(multipoly_df["fac_id"])
        
        #get polyvertex facility list for check
        find_p = emisloc_df[emisloc_df['source_type'] == "I"]
        poly_fac = find_p['fac_id']
        
        
         if check_poly_assignment != poly_fac:
            poly_unassigned = (check_poly_assignment - poly_fac).tolist()
            
            messagebox.showinfo("Unassigned polyvertex sources", "Polyvertex" + 
                                "sources for " + ", ".join(poly_unassigned) + 
                                " have not been assigned. Please edit the" +
                                " 'source_type' column in the Emissions Locations" +
                                " file.")
            
        else:
            
            self.log.append("Uploaded polyvertex sources for " + 
                            " ".join(check_poly_assignment))
            
            self.dataframe = multipoly_df
        
        