#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 20:34:16 2018

@author: d
"""
from com.sca.hem4.log import Logger
from com.sca.hem4.model.Model import fac_id
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

from com.sca.hem4.upload.EmissionsLocations import source_type
import pandas as pd

avgbld_len = 'avgbld_len';
avgbld_hgt = 'avgbld_hgt';
avgbld_wid = 'avgbld_wid';
avglin_wid = 'avglin_wid';
avgbld_sep = 'avgbld_sep';
avgbuoy = 'avgbuoy';
blpgrp_id = 'blpgrp_id';
source_id = 'source_id';

class BuoyantLine(DependentInputFile):

    def __init__(self, path, dependency):
        self.emisloc_df = dependency
        DependentInputFile.__init__(self, path, dependency)
        
    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [avgbld_len,avgbld_hgt,avgbld_wid,avglin_wid,avgbld_sep,avgbuoy]
        self.strColumns = [fac_id, blpgrp_id, source_id]

        multibuoy_df = self.readFromPath(
            (fac_id, blpgrp_id, source_id, avgbld_len, avgbld_hgt, avgbld_wid, avglin_wid, avgbld_sep, avgbuoy))
            
        self.dataframe = multibuoy_df

    def clean(self, df):
        cleaned = df.fillna({avgbld_len:0, avgbld_hgt:0, avgbld_wid:0, avglin_wid:0, avgbld_sep:0, avgbuoy:0})        
        cleaned.replace(to_replace={fac_id:{"nan":""}, blpgrp_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = cleaned.reset_index(drop = True)

        return cleaned

    def validate(self, df):
        
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Buoyant Line Parameter file.")
            messagebox.showinfo("Missing facility IDs", "One or more facility IDs are missing in the Buoyant Line Parameter file.")
            return None

        # The group ID cannot be empty
        blank_grpids = df[df[blpgrp_id]==""]
        if len(blank_grpids) > 0:
            Logger.logMessage("At least one buoyant line group id in the Buoyant Line Parameter file is blank. Please add an ID.")
            messagebox.showinfo("Buoyant Line Group ID is blank", "At least one buoyant line group id in the Buoyant Line Parameter file is blank. Please add an ID.")            
            return None
        
        # Buoyant line group id's can be no longer than 8 characaters
        blpgrpid_len = df[blpgrp_id].str.len().max()
        if blpgrpid_len > 8:
            Logger.logMessage("At least one buoyant line group id in the Buoyant Line Parameter file is longer than 8 characters. Please correct.")
            messagebox.showinfo("Buoyant Line Group ID too long", "At least one buoyant line group id in the Buoyant Line Parameter file is longer than 8 characters. Please correct.")
            return None
        
        # Make sure all parameters for each line (source id) in a group per facility are the same
        df['facblpgrp'] = df[fac_id] + df[blpgrp_id]
        v = df['facblpgrp'].value_counts()
        # buoyant line groups with more than one line
        grp_srcs = df[df['facblpgrp'].isin(v.index[v.gt(1)])]
        dup_chk = grp_srcs[grp_srcs.duplicated(subset=[avgbld_len,avgbld_hgt,avgbld_wid,avglin_wid,avgbld_sep,avgbuoy],keep=False)]
        if grp_srcs.shape[0] != dup_chk.shape[0]:
            Logger.logMessage("There is at least one buoyant line group for a given facility in the Buoyant Line Parameter file with source IDs that do not have the same parameters. Please correct.")
            messagebox.showinfo("Parameters differ in buoyant line group", "There is at least one buoyant line group for a given facility in the Buoyant Line Parameter file with source IDs that do not have the same parameters. Please correct.")
            return None
            
        
        # Make sure all source id's are unique for each facility. 
        unique_ids = df.groupby([fac_id])[source_id].nunique()
        num_rows = df.groupby([fac_id]).size()
        qa_df = pd.DataFrame({'num_unique':unique_ids, 'num_rows':num_rows})
        compare_counts = qa_df['num_unique'] == qa_df['num_rows']
        if compare_counts.all() == False:
            Logger.logMessage("The Buoyant Line Parameter file contains one or more facilities with non-unique source IDs. Please correct.")
            messagebox.showinfo("Non-unique Source IDs", "The Buoyant Line Parameter file contains one or more facilities with non-unique source IDs. Please correct.")
            return None
            
        
        # Make sure all source IDs in the buoyant parameter file are listed as buoyant line
        # sources in the Emission Location file.
        el_srcs = self.emisloc_df[self.emisloc_df['source_type']=='B'][[fac_id, source_id]]
        blp_srcs = df[[fac_id, source_id]].copy()
        if len(blp_srcs) > 0:
            el_srcs['facsrc'] = el_srcs[fac_id] + el_srcs[source_id]
            blp_srcs['facsrc'] = blp_srcs[fac_id] + blp_srcs[source_id]
            elfacsrc = set(el_srcs['facsrc'])
            blpfacsrc = set(blp_srcs['facsrc'])
            if elfacsrc != blpfacsrc:
                Logger.logMessage("For at least one facility, there are missmatched buoyant line Source IDs in the Emission Location file and the Buoyant Line Parameter file.")
                messagebox.showinfo("Missmatched buoyant line Source IDs", "For at least one facility, there are missmatched buoyant line Source IDs in the Emission Location file and the Buoyant Line Parameter file.")
                return None
                
        
        for index, row in df.iterrows():
            facility = row[fac_id]

            if row[avgbld_len] <= 0:
                Logger.logMessage("Facility " + facility + ": avg building length " + str(row[avgbld_len]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg building length " + str(row[avgbld_len]) +
                                  " out of range.")
                return None
            if row[avgbld_hgt] <= 0:
                Logger.logMessage("Facility " + facility + ": avg building height " + str(row[avgbld_hgt]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg building height " + str(row[avgbld_hgt]) +
                                  " out of range.")
                return None
            if row[avgbld_wid] <= 0:
                Logger.logMessage("Facility " + facility + ": avg building width " + str(row[avgbld_wid]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg building width " + str(row[avgbld_wid]) +
                                  " out of range.")
                return None
            if row[avglin_wid] <= 0:
                Logger.logMessage("Facility " + facility + ": avg line width " + str(row[avglin_wid]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg line width " + str(row[avglin_wid]) +
                                  " out of range.")
                return None
            if row[avgbld_sep] < 0:
                Logger.logMessage("Facility " + facility + ": avg building separation " + str(row[avgbld_sep]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg building separation " + str(row[avgbld_sep]) +
                                  " out of range.")
                return None
            if row[avgbuoy] <= 0:
                Logger.logMessage("Facility " + facility + ": avg buoyancy " + str(row[avgbuoy]) +
                                  " out of range.")
                messagebox.showinfo("Out of Range", "Facility " + facility + ": avg buoyancy " + str(row[avgbuoy]) +
                                  " out of range.")
                return None

        # check for unassigned buoyant line
        check_buoyant_assignment = set(df[fac_id])
        
        # get buoyant line facility list
        find_b = self.emisloc_df[self.emisloc_df[source_type] == 'B']
        buoyant_fac = set(find_b[fac_id])

        if check_buoyant_assignment != buoyant_fac:
            buoyant_unassigned = check_buoyant_assignment.symmetric_difference(buoyant_fac)

            Logger.logMessage("Buoyant Line parameters for " +
                                ", ".join(buoyant_unassigned) + " have not been" +
                                " assigned. Please edit the 'source_type' column" +
                                " in the Emissions Locations file.")
            messagebox.showinfo("Unassigned buoyant Line parameters", "Buoyant" +
                                " Line parameters for " +
                                ", ".join(buoyant_unassigned) + " have not been" +
                                " assigned. Please edit the 'source_type' column" +
                                " in the Emissions Locations file.")
            return None

        else:
            Logger.logMessage("Uploaded buoyant line parameters for [" + ",".join(check_buoyant_assignment) + "]\n")

        return df
