#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018

@author: d
"""

from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class Particle(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency

    def createDataframe(self):
        
        faclist_df = self.dependency
        particle_df = self.readFromPath(("fac_id", "source_id", "part_diam",
                                        "mass_frac", "part_dens"), {0:str, 1:str})
        
        
        #check for unassigned particle
        check_particle_assignment = set(particle_df['fac_id'])
        
        ## figure out how to get fac ids that have particle based on flag or index
        
        self.dataframe = particle_df