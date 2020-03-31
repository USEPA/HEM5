#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 20:13:09 2018
@author: d
"""
from com.sca.hem4.model.Model import fac_id
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class LandUse(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency

    def createDataframe(self):


        faclist_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = ["D01", "D02","D03", "D04", "D05","D06", "D07","D08","D09","D10","D11","D12","D13","D14",
                               "D15", "D16", "D17","D18", "D19", "D20","D21", "D22", "D23","D24", "D25", "D26",
                               "D27", "D28", "D29","D30", "D31", "D32","D33", "D34", "D35","D36"]
        self.strColumns = [fac_id]

        landuse_df = self.readFromPath((fac_id, "D01", "D02",
                                        "D03", "D04", "D05",
                                        "D06", "D07", "D08",
                                        "D09", "D10", "D11",
                                        "D12", "D13", "D14",
                                        "D15", "D16", "D17",
                                        "D18", "D19", "D20",
                                        "D21", "D22", "D23",
                                        "D24", "D25", "D26",
                                        "D27", "D28", "D29",
                                        "D30", "D31", "D32",
                                        "D33", "D34", "D35",
                                        "D36"))

        #check for unassigned landuse
        check_landuse_assignment = set(landuse_df[fac_id])

        ## figure out how to get fac ids that have landuse based on flag or index

        self.dataframe = landuse_df
