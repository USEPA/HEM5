#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018

@author: d
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox



class Particle(DependentInputFile):

    def __init__(self, path, dependency, facilities):
        DependentInputFile.__init__(self, path, dependency, facilities)
        self.dependency = dependency
        self.facilities = facilities

    def createDataframe(self):
        
        faclist_df = self.dependency
        particle_df = self.readFromPath(("fac_id", "source_id", "part_diam",
                                        "mass_frac", "part_dens"), {0:str, 1:str})
        
        
        #check for unassigned particle
        check_particle_assignment = set(particle_df['fac_id'])
        
        
        if check_particle_assignment != set(self.facilities):
            particle_unassigned = (check_particle_assignment - set(self.facilities)).tolist()
            
            messagebox.showinfo("Unassigned particle size parameters", "" + 
                                " Line parameters for " + 
                                ", ".join(particle_unassigned) + " have not been" + 
                                " assigned. Please edit the 'FacilityID' column" + 
                                " in the Facilities List Options file.")
        
        self.dataframe = particle_df