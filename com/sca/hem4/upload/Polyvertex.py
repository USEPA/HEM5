
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 00:34:57 2018
@author: d
"""

from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

from com.sca.hem4.upload.EmissionsLocations import *

numvert = 'numvert';
area = 'area';
fipstct = 'fipstct';

class Polyvertex(DependentInputFile):

    def __init__(self, path, dependency):
        self.emisloc_df = dependency
        DependentInputFile.__init__(self, path, dependency)

    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [lon,lat,numvert,area,fipstct]
        self.strColumns = [fac_id,source_id,location_type,utmzone]

        # POLYVERTEX excel to dataframe
        multipoly_df = self.readFromPath((fac_id,source_id,location_type, lon,lat,utmzone,numvert,area,fipstct))

        self.dataframe = multipoly_df

    def clean(self, df):
        cleaned = df
        cleaned.replace(to_replace={fac_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = cleaned.reset_index(drop = True)

        # upper case of selected fields
        cleaned[location_type] = cleaned[location_type].str.upper()

        return cleaned

    def validate(self, df):

        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Polyvertex List.")
            return None

        if len(df.loc[(df[source_id] == '')]) > 0:
            Logger.logMessage("One or more source IDs are missing in the Polyvertex List.")
            return None

        if len(df.loc[(df[location_type] != 'L') & (df[location_type] != 'U')]) > 0:
            Logger.logMessage("One or more locations have a missing/invalid coordinate system in the Polyvertex List.")
            return None

        for index, row in df.iterrows():

            facility = row[fac_id]
            type = row[location_type]

            maxlon = 180 if type == 'L' else 850000
            minlon = -180 if type == 'L' else 160000
            maxlat = 85 if type == 'L' else 10000000
            minlat = -80 if type == 'L' else 0

            if row[lon] > maxlon or row[lon] < minlon:
                Logger.logMessage("Facility " + fac_id + ": lon value " + str(row[lon]) + " out of range " +
                                  "in the Polyvertex List.")
                return None
            if row[lat] > maxlat or row[lat] < minlat:
                Logger.logMessage("Facility " + fac_id + ": lat value " + str(row[lat]) + " out of range " +
                                  "in the Polyvertex List.")
                return None

            if type == 'U':
                zone = row[utmzone]
                if zone.endswith('N') or zone.endswith('S'):
                    zone = zone[:-1]

                try:
                    zonenum = int(zone)
                except ValueError as v:
                    Logger.logMessage("Facility " + facility + ": UTM zone value " + str(row[utmzone]) + " malformed " +
                                      "in the Polyvertex List.")
                    return None

                if zonenum < 1 or zonenum > 60:
                    Logger.logMessage("Facility " + facility + ": UTM zone value " + str(row[utmzone]) + " invalid " +
                                      "in the Polyvertex List.")
                    return None

            if row[numvert] <= 3 or row[numvert] > 20:
                Logger.logMessage("Facility " + facility + ": Number of vertices " + str(row[numvert]) + " invalid " +
                                  "in the Polyvertex List.")
                return None

            if row[area] <= 0:
                Logger.logMessage("Facility " + facility + ": Area value " + str(row[area]) + " invalid " +
                                  "in the Polyvertex List.")
                return None

        # check for unassigned polyvertex
        check_poly_assignment = set(df[fac_id])

        # get polyvertex facility list for check
        find_p = self.emisloc_df[self.emisloc_df[source_type] == "I"]
        poly_fac = set(find_p[fac_id])

        if check_poly_assignment != poly_fac:
            poly_unassigned = (check_poly_assignment - poly_fac).tolist()

            messagebox.showinfo("Unassigned polyvertex sources", "Polyvertex" +
                                "sources for " + ", ".join(poly_unassigned) +
                                " have not been assigned. Please edit the" +
                                " 'source_type' column in the Emissions Locations" +
                                " file.")
            return None
        else:
            Logger.logMessage("Uploaded polyvertex sources for " + " ".join(check_poly_assignment) + "\n")
            return df
