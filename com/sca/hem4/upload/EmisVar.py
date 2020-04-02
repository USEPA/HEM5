# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 12:35:08 2018
@author: 
"""
import pandas as pd

from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *

class EmisVar(DependentInputFile):

    def __init__(self, path, dependency):
        self.emisloc_df = dependency
        self.path = path
        DependentInputFile.__init__(self, path, dependency)

    def createDataframe(self):
        
        #not calling standard read_file because length of columns is variable
        #depending on varation type
        
        #checking to see if variaiton file is excel or txt.
        #NEED TO MAKE SURE THE LINKED FILE HAS A .txt in it or append
        
        if self.path[-3:] == 'txt': 
            
            self.dataframe = self.path #save linked file path in place of dataframe
        
        else: #excel file used
        
            emisvar_df = pd.read_excel(self.path, skiprows=0, dtype=str)
            
            emisvar_df.columns = map(str.lower, emisvar_df.columns)
            
            # rename first three columns
            emisvar_df.rename(columns={"facility id": fac_id,
                                       "source id": source_id,
                                       emisvar_df.columns[2]: "variation"}, inplace=True)
            
            # convert all columns to float64 except first three
            float_cols=[i for i in emisvar_df.columns if i not in ["fac_id","source_id","variation"]]
            for col in float_cols:
                emisvar_df[col]=pd.to_numeric(emisvar_df[col], errors="coerce")

            self.dataframe = emisvar_df

    def clean(self, df):
        cleaned = df
        cleaned.replace(to_replace={fac_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = cleaned.reset_index(drop = True)

        # upper case of selected fields
        cleaned['variation'] = cleaned['variation'].str.upper()

        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Emissions Variations List.")
            return None

        if len(df.loc[(df[source_id] == '')]) > 0:
            Logger.logMessage("One or more source IDs are missing in the Emissions Variations List.")
            return None

        for index, row in df.iterrows():
            facility = row[fac_id]

            valid = ['SEASON', 'MONTH', 'HROFDY', 'WSPEED', 'SEASHR', 'HRDOW',
                     'HRDOW7', 'SHRDOW', 'SHRDOW7', 'MHRDOW', 'MHRDOW7']
            if row['variation'] not in valid:
                Logger.logMessage("Facility " + facility + ": variation value invalid.")
                return None

        # facility/source ids from emission variation file
        var_ids = set(df[[fac_id, source_id]].apply(lambda x: ''.join(x), axis=1).tolist())

        # facility/source ids from emission location file
        model_ids = set(self.emisloc_df[[fac_id, source_id]].apply(lambda x: ''.join(x), axis=1).tolist())

        # Make sure all facility/source ids from emission variation file are also in
        # the emission location file
        if len(set(var_ids).difference(set(model_ids))) > 0:
            missing = set(var_ids).difference(set(model_ids))

            messagebox.showinfo("Missing Emission Location", "The emission " +
                                "variation file indicates variation for facility/source ids " +
                                ", ".join(missing) + " which are not in the " +
                                "emissions location file. Please edit " +
                                "the emissions variation or emissions location "+
                                " file.")
            return None

        vtype = df['variation'].str.tolist()

        if 'SEASON' in vtype:

            # check that seasonal variaton only has 4 values
            seasons = df[df['variation'].str.lower() == 'SEASON']
            print(seasons)
            s_wrong = []
            for row in seasons.iterrows():
                if len(row[1].values[3:]) != 4:
                    s_wrong.append(seasons[source_id].values[0])

            if len(s_wrong) > 0:
                messagebox.showinfo("Seasonal Emissions Variation",
                                    "Seasonal emissions variations require 4 "+
                                    "values. Sources: " + ", ".join(s_wrong) +
                                    " do not have the correct number of values. " +
                                    "Please update your Emission Variation File.")
                return None

        # check wind speed is only 6 values
        if 'WSPEED' in vtype:
            wspeed = df[df['variation'].str == 'WSPEED']
            w_wrong = []
            for row in wspeed.iterrows():
                if len(row[1].values[3:]) != 6:
                    w_wrong.append(wspeed[source_id].values[0])

            if len(w_wrong) > 0:
                messagebox.showinfo("Wind Speed Emissions Variation",
                                    "Wind speed emissions variations require 6 "+
                                    "values. Sources: " + ", ".join(w_wrong) +
                                    " do not have the correct number of values. " +
                                    "Please update your Emission Variation File.")
                return None

        # make sure the monthly emissions variation has 12 values
        if 'MONTH' in vtype:
            month = df[df['variation'].str == 'MONTH']
            m_wrong = []
            for row in month.iterrows():
                if len(row[1].values[3:]) != 12:
                    m_wrong.append(month[source_id].values[0])

            if len(m_wrong) > 0:
                messagebox.showinfo("Monthly Emissions Variation",
                                    "Monthly emissions variations require 12 "+
                                    "values. Sources: " + ", ".join(m_wrong) +
                                    " do not have the correct number of values. " +
                                    "Please update your Emission Variation File.")
                return None

        if 'HROFDY' in vtype or 'SEASHR' in vtype or 'SHRDOW' in vtype or 'SHRDOW7' in vtype:
            other = df[~df['variation'].str.isin(['MONTH', 'WSPEED', 'SEASON'])]
            variation = other[other.columns[3:]].values

            o_wrong = 0
            for row in variation:
                if len(row) != 12:
                    o_wrong += 1

            if o_wrong > 0:
                messagebox.showinfo("Emissions Variation Error",
                                    "One of the emissions variations type does "+
                                    "not have the correct number of values. "+
                                    "Please check your input file to make all "+
                                    "values are either a multiple or factor "+
                                    "of 12.")
                return None

        Logger.logMessage("Uploaded emissions variations for " + " ".join(var_ids))
        return df
