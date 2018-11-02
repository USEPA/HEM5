# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 12:35:08 2018

@author: 
"""
import pandas as pd
from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class EmisVar(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency
        self.path = path
        
    def createDataframe(self):
        
        emisloc_df = self.dependency
        
        #not calling standard read_file because length of columns is variable
        #depending on varation type
        emisvar_df = pd.read_excel(self.path)
        
        emisvar_df.columns = map(str.lower, emisvar_df.columns)
        
        #rename first two columns
        emisvar_df.rename({"facility id": "fac_id", "source id": "source_id"}, 
                          inplace=True)
        
        
        #check source ids against emislocs
        var_source_ids = emisvar_df["source_id"].tolist()
        
        model_source_ids = emisloc_df["source_id"].tolist()
        
        
        #make sure no emission sources missing from 
        if len(set(var_source_ids).difference(set(model_source_ids))) > 0:
            missing = set(var_source_ids).difference(set(model_source_ids)).tolist()
            
            messagebox.showinfo("Missing Emission Location", "The emission " + 
                                "variation file indicates variation for " + 
                                ", ".join(missing) + " which are not in the " + 
                                "emissions location file. Please edit " + 
                                "the emissions variation or emissions location "+
                                " file.")
        
        
        if ('SEASON' in emisvar_df['variation'].tolist() or 
              'season' in  emisvar_df['variation'].tolist()):
            
            #check that seasonal varaiton only has 4 values
                seasons = emisvar_df[emisvar_df['variation'].str.lower() == 'season']
                s_wrong = []
                for row in seasons.iterrows():
                    if len(seasons[:2]) != 4:
                        
                        s_wrong.append(seasons["source_id"])        
                
                
                messagebox.showinfo("Seasonal Emissions Variation", 
                                    "Seasonal emissions variations require 4 "+
                                    "values. Sources: " + ", ".join(s_wrong) +
                                    " do not have the correct number of values. " +
                                    "Please update your Emission Variation File.")
                
        if ('WSPEED' in emisvar_df['variation'].tolist() or 
              'wspeed' in  emisvar_df['variation'].tolist()):    
                #check wind speed is only 6 values

                wspeed = emisvar_df[emisvar_df['variation'].str.lower() == 'wspeed']
                w_wrong = []
                for row in wspeed.iterrows():
                    if len(wspeed[:2]) != 6:
                        
                        w_wrong.append(seasons["source_id"])        
                
                
                messagebox.showinfo("Wind Speed Emissions Variation", 
                                    "Wind speed emissions variations require 6 "+
                                    "values. Sources: " + ", ".join(w_wrong) +
                                    " do not have the correct number of values. " +
                                    "Please update your Emission Variation File.")
            
            
            
            
    
               #make sure the len of inputs is divisable by 12
               
               
        #make sure this is triggered correctly!
        self.log.append("Uploaded emissions variations for " + 
                            " ".join(var_source_ids))
        self.dataframe = emisvar_df
            
        
        
        
        