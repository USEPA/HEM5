#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018
@author: d
"""

from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *
from decimal import Decimal

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
        facid_list = faclist_df[fac_id].tolist()
        
        # Specify dtypes for all fields
        self.numericColumns = [part_diam,mass_frac,part_dens]
        self.strColumns = [fac_id,source_id]

        # Read the particle file
        particle_allfacs = self.readFromPath((fac_id, source_id, part_diam,mass_frac, part_dens))
        
        
        # Subset the particle data to the facilities being modeled
        particle_df = particle_allfacs.loc[particle_allfacs[fac_id].isin(facid_list)]

        # Default NaN to 0 and convert float64 values to decimal with 3 decimal places
        particle_df.fillna({part_diam:0, mass_frac:0, part_dens:0})
        particle_df[part_diam] = particle_df[part_diam].apply(lambda x: round(Decimal(x), 3))
        particle_df[mass_frac] = particle_df[mass_frac].apply(lambda x: round(Decimal(x), 3))
        particle_df[part_dens] = particle_df[part_dens].apply(lambda x: round(Decimal(x), 3))

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
                    incomplete.append(str(fac) + ': ' + str(s))


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
                                       set(self.facilities))


                messagebox.showinfo("Unassigned particle size parameters", "" +
                                    " Line parameters for " +
                                    ", ".join(particle_unassigned) + " have not been" +
                                    " assigned. Please edit the 'FacilityID' column" +
                                    " in the Facilities List Options file.")

            else:
                self.dataframe = particle_df

    def validate(self, df):
        pass