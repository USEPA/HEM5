# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 11:21:13 2018

@author: dlindsey
"""
from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *
from com.sca.hem4.upload.FacilityList import bldg_dw

section = 'section';
keyword = 'keyword';

class Downwash(DependentInputFile):

    def __init__(self, path, dependency):
        self.faclist_df = dependency
        DependentInputFile.__init__(self, path, dependency)

    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = ["value_1","value_2","value_3","value_4","value_5","value_6","value_7","value_8",
                               "value_9","value_10","value_11","value_12","value_13","value_14","value_15","value_16",
                               "value_17","value_18","value_19","value_20","value_21","value_22","value_23","value_24",
                               "value_25", "value_26","value_27","value_28","value_29","value_30","value_31","value_32",
                               "value_33","value_34","value_35","value_36"]
        self.strColumns = [fac_id, section, keyword, source_id]

        downwash_df = self.readFromPath((fac_id, section, keyword,
                                      source_id, "value_1", "value_2",
                                      "value_3", "value_4", "value_5",
                                      "value_6", "value_7", "value_8",
                                      "value_9", "value_10", "value_11",
                                      "value_12", "value_13", "value_14",
                                      "value_15", "value_16", "value_17",
                                      "value_18", "value_19", "value_20",
                                      "value_21", "value_22", "value_23",
                                      "value_24", "value_25", "value_26",
                                      "value_27", "value_28", "value_29",
                                      "value_30", "value_31", "value_32",
                                      "value_33", "value_34", "value_35",
                                      "value_36"))

        self.dataframe = downwash_df

    def clean(self, df):

        df.replace(to_replace={fac_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = df.reset_index(drop = True)

        # upper case of selected fields
        cleaned[section] = cleaned[section].str.upper()
        cleaned[keyword] = cleaned[keyword].str.upper()

        return cleaned

    def validate(self, df):

        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Downwash List.")
            return None

        if len(df.loc[(df[source_id] == '')]) > 0:
            Logger.logMessage("One or more source IDs are missing in the Downwash List.")
            return None

        duplicates = self.duplicates(df, [fac_id, source_id, keyword])
        if len(duplicates) > 0:
            Logger.logMessage("One or more records are duplicated in the Downwash List (key=fac_id, source_id, keyword):")
            for d in duplicates:
                Logger.logMessage(d)
            return None

        for index, row in df.iterrows():

            if row[section] != 'SO':
                Logger.logMessage("Invalid section " + str(row[section]) + ".")
                return None

            valid = ['BUILDHGT', 'BUILDWID', 'BUILDLEN', 'XBADJ', 'YBADJ']
            if row[keyword] not in valid:
                Logger.logMessage("Invalid keyword " + str(row[keyword]) + ".")
                return None

            constrained = ['BUILDHGT', 'BUILDWID', 'BUILDLEN']
            for num in range(1, 37):
                field = "value_" + str(num)

                if row[keyword] in constrained and row[field] <= 0:
                    Logger.logMessage("Invalid down wash value " + str(row[field]) + ".")
                    return None

        # check for unassigned downwash
        check_downwash_assignment = set(df[fac_id])

        find_d = self.faclist_df[self.faclist_df[bldg_dw] == "Y"]
        d_fac = set(find_d[fac_id])

        if check_downwash_assignment != d_fac:
            downwash_unassigned = (check_downwash_assignment - d_fac).tolist()

            messagebox.showinfo("Unassigned building downwash", "Building" +
                                "downwash parameters for " +
                                ", ".join(downwash_unassigned) + " have not" +
                                " been assigned. Please edit the" +
                                " 'bldgdw' column in the Facilities List Option" +
                                " file.")
            return None

        else:
            Logger.logMessage("Uploaded building downwash parameters for [" + ",".join(check_downwash_assignment) + "]\n")
            return df


             
         
        
         
         

