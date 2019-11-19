
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
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency

    def createDataframe(self):

        emisloc_df = self.dependency;

        # Specify dtypes for all fields
        self.numericColumns = [lon,lat,numvert,area,fipstct]
        self.strColumns = [fac_id,source_id,location_type,utmzone]

        #POLYVERTEX excel to dataframe
        multipoly_df = self.readFromPath((fac_id,source_id,location_type,
                                          lon,lat,utmzone,numvert,area,fipstct))

        #check for unassigned polyvertex
        check_poly_assignment = set(multipoly_df[fac_id])

        #get polyvertex facility list for check
        find_p = emisloc_df[emisloc_df[source_type] == "I"]
        poly_fac = set(find_p[fac_id])

        #        print("poly assignment", check_poly_assignment)
        #        print("poly:", poly_fac)
        #


        if check_poly_assignment != poly_fac:
            poly_unassigned = (check_poly_assignment - poly_fac).tolist()

            messagebox.showinfo("Unassigned polyvertex sources", "Polyvertex" +
                                "sources for " + ", ".join(poly_unassigned) +
                                " have not been assigned. Please edit the" +
                                " 'source_type' column in the Emissions Locations" +
                                " file.")

        else:

            self.log.append("Uploaded polyvertex sources for " +
                            " ".join(check_poly_assignment) + "\n")

            self.dataframe = multipoly_df