#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018
@author: d
"""

from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *

part_diam = 'part_diam';
mass_frac = 'mass_frac';
part_dens = 'part_dens';

class Particle(DependentInputFile):

    def __init__(self, path, dependency, facilities):
        DependentInputFile.__init__(self, path, dependency, facilities)
        self.dependency = dependency
        self.facilities = facilities

    def createDataframe(self):

        faclist_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = [part_diam,mass_frac,part_dens]
        self.strColumns = [fac_id,source_id]

        particle_df = self.readFromPath((fac_id, source_id, part_diam,mass_frac, part_dens))

        particle_df[mass_frac] = particle_df[mass_frac] / 100


        #check for mass frac sum to 1
        fac_ids = particle_df[fac_id].tolist()
        incomplete = []
        for fac in set(fac_ids):
            fac_search = particle_df[particle_df[fac_id] == fac]
            sources = particle_df[particle_df[fac_id] == fac][source_id].tolist()

            for s in set(sources):
                mass_fracs = fac_search[fac_search[source_id] == s][mass_frac].tolist()

                if sum(mass_fracs) != 1:
                    incomplete.append[str(fac) + ': ' + str(s)]


        if len(incomplete) > 0:
            messagebox.showinfo("Mass Fraction Error",
                                "The mass fractions for " + ", ".join(incomplete)+
                                " do not sum to 1. Please correct them in your "+
                                "particle size file.")


        else:
            #check for unassigned particle
            check_particle_assignment = set(particle_df[fac_id])


            if check_particle_assignment != set(self.facilities):
                particle_unassigned = (check_particle_assignment -
                                       set(self.facilities)).tolist()

                messagebox.showinfo("Unassigned particle size parameters", "" +
                                    " Line parameters for " +
                                    ", ".join(particle_unassigned) + " have not been" +
                                    " assigned. Please edit the 'FacilityID' column" +
                                    " in the Facilities List Options file.")

            else:
                self.dataframe = particle_df