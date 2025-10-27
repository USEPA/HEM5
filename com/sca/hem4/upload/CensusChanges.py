# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:57:27 2023

@author: SteveFudge
"""

from com.sca.hem4.upload.InputFile import InputFile
from tkinter import messagebox
from com.sca.hem4.log import Logger

class CensusChanges(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):
        
        # Specify dtypes for all fields
        self.numericColumns = ["lat", "lon", "population", "elev", "hill"]
        self.strColumns = ["change", "facid", "category", "blockid"]

        changes_df = self.readFromPath(('change', 'facid', 'category', 'blockid',
                                        'lat', 'lon', 'population', 'elev', 'hill'))
        
        if changes_df.empty == False:
            changes_df['population'] = changes_df['population'].fillna(0)
            changes_df['population'] = changes_df['population'].astype(int)
        
        self.dataframe = changes_df
        
        
    def validate(self, df):
        
        # Make sure all changes are using valid types
        valid = ['ADD', 'DELETE','MOVE', 'ZERO', 'ELEVHILL']
        for index, row in df.iterrows():
            if not row['change'].upper() in valid:                
                messagebox.showinfo("Invalid change type", "An invalid census change type of "
                       + row['change'].upper() + " was found in the Census Change file. "
                       + "Please correct and rerun the Census Update utility.")

                msg = ("An invalid census change type of \n"
                       + row['change'].upper() + " was found in the Census Change file. \n"
                       + "Please correct and rerun the Census Update utility.\n")
                
                Logger.logMessage(msg)
                return None
            
        return df