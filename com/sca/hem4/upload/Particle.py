#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018
@author: d
"""
from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *
from decimal import Decimal

part_diam = 'part_diam';
mass_frac = 'mass_frac';
part_dens = 'part_dens';

class Particle(DependentInputFile):

    def __init__(self, path, dependency, facilities):
        self.faclist_df = dependency
        # Facilities that need particle size data:
        self.particleFacilities = set(facilities)
        DependentInputFile.__init__(self, path, dependency, facilities)

    def createDataframe(self):

        facid_list = self.faclist_df[fac_id].tolist()
        
        # Specify dtypes for all fields
        self.numericColumns = [part_diam,mass_frac,part_dens]
        self.strColumns = [fac_id,source_id]

        # Read the particle file
        particle_allfacs = self.readFromPath((fac_id, source_id, part_diam,mass_frac, part_dens))
        
        self.dataframe = particle_allfacs

    def clean(self, df):

        # Default NaN to 0 and convert float64 values to decimal with 3 decimal places
        cleaned = df.fillna({part_diam:0, mass_frac:0, part_dens:0})
        cleaned.replace(to_replace={fac_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = cleaned.reset_index(drop = True)

        cleaned[part_diam] = cleaned[part_diam].apply(lambda x: round(Decimal(x), 3))
        cleaned[mass_frac] = cleaned[mass_frac].apply(lambda x: round(Decimal(x), 3))
        cleaned[part_dens] = cleaned[part_dens].apply(lambda x: round(Decimal(x), 3))
        cleaned[mass_frac] = cleaned[mass_frac] / 100

        # Upper case source id
        cleaned[source_id] = cleaned[source_id].str.upper()

        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Particle List.")
            messagebox.showinfo("Missing facility IDs", "One or more facility IDs are missing in the Particle List.")
            return None

        if len(df.loc[(df[source_id] == '')]) > 0:
            Logger.logMessage("One or more source IDs are missing in the Particle List.")
            messagebox.showinfo("Missing source IDs", "One or more source IDs are missing in the Particle List.")
            return None

        duplicates = self.duplicates(df, [fac_id, source_id, part_diam])
        if len(duplicates) > 0:
            Logger.logMessage("One or more records are duplicated in the Particle List (key=fac_id, source_id, part_diam):")
            messagebox.showinfo("Duplicate records", "One or more records are duplicated in the Particle List (key=fac_id, source_id, part_diam)")
            for d in duplicates:
                Logger.logMessage(d)
            return None

        for index, row in df.iterrows():

            facility = row[fac_id]

            if row[part_diam] <= 0:
                Logger.logMessage("Facility " + facility + ": particle diameter value " + str(row[part_diam]) +
                                  " out of range.")
                messagebox.showinfo("Value out of range", "Facility " + facility + ": particle diameter value " + str(row[part_diam]) +
                                  " out of range.")
                return None
            if row[mass_frac] < 0 or row[mass_frac] > 100:
                Logger.logMessage("Facility " + facility + ": mass fraction value " + str(row[mass_frac]) +
                                  " out of range.")
                messagebox.showinfo("Value out of range", "Facility " + facility + ": mass fraction value " + str(row[mass_frac]) +
                                  " out of range.")
                return None
            if row[part_dens] < 0:
                Logger.logMessage("Facility " + facility + ": particle density value " + str(row[part_dens]) +
                                  " out of range.")
                messagebox.showinfo("Value out of range", "Facility " + facility + ": particle density value " + str(row[part_dens]) +
                                  " out of range.")
                return None

        # check for mass frac sum to 1
        fac_ids = df[fac_id].tolist()
        incomplete = []
        for fac in set(fac_ids):
            fac_search = df[df[fac_id] == fac]
            sources = df[df[fac_id] == fac][source_id].tolist()

            for s in set(sources):
                mass_fracs = fac_search[fac_search[source_id] == s][mass_frac].tolist()

                if sum(mass_fracs) != 1:
                    incomplete.append(str(fac) + ': ' + str(s))

        if len(incomplete) > 0:
            Logger.logMessage("The mass fraction for " + ", ".join(incomplete)+
                                " does not sum to 100%. Please correct them in your "+
                                "particle size file.")
            messagebox.showinfo("Mass fraction error", "The mass fraction for " + ", ".join(incomplete)+
                                " does not sum to 100%. Please correct them in your "+
                                "particle size file.")
            return None
        else:
            # check for unassigned particle
            check_particle_assignment = set(df[fac_id])

            # Particle size file can have extra facilities
            if self.particleFacilities.issubset(check_particle_assignment) == False:
                particle_unassigned = (set(self.particleFacilities) - check_particle_assignment)
                
                Logger.logMessage("Particle size data for facilities: " +
                                  ", ".join(particle_unassigned) + " have not been assigned. " +
                                  "Please edit the particle size file.")
                messagebox.showinfo("Particle size data", "Particle size data for facilities, " +
                                  ", ".join(particle_unassigned) + " have not been assigned. " +
                                  "Please edit the particle size file.")
                return None
            else:
                Logger.logMessage("Uploaded particle data for [" + ",".join(check_particle_assignment) + "]\n")
                return df
