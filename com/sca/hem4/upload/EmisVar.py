# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 12:35:08 2018
@author: 
"""
import pandas as pd
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.model.Model import *

class EmisVar(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)
        self.dependency = dependency
        self.path = path
        
    def createDataframe(self):
                
        emisloc_df = self.dependency
        
        #not calling standard read_file because length of columns is variable
        #depending on varation type
        
        #checking to see if variaiton file is excel or txt.
        #NEED TO MAKE SURE THE LINKED FILE HAS A .txt in it or append
        
        if self.path[-3:] == 'txt': 
            
            self.dataframe = self.path #save linked file path in place of dataframe
        
        else: #excel file used
        
            emisvar_df = pd.read_excel(self.path, skiprows=0, dtype=str)
            
            emisvar_df.columns = map(str.lower, emisvar_df.columns)
            
            #rename first three columns
            emisvar_df.rename(columns={"facility id": fac_id,
                                       "source id": source_id,
                                       emisvar_df.columns[2]: "variation"}, inplace=True)
            
            #convert all columns to float64 except first three
            float_cols=[i for i in emisvar_df.columns if i not in ["fac_id","source_id","variation"]]
            for col in float_cols:
                emisvar_df[col]=pd.to_numeric(emisvar_df[col], errors="coerce")
            
            # facility/source ids from emission variation file
            var_ids = set(emisvar_df[[fac_id, source_id]].apply(lambda x: ''.join(x), axis=1).tolist())

            # facility/source ids from emission location file
            model_ids = set(emisloc_df[[fac_id, source_id]].apply(lambda x: ''.join(x), axis=1).tolist())
            
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
            
            
            vtype = emisvar_df['variation'].str.lower().tolist()
            
            
            if ('season' in vtype):
                
                #check that seasonal variaton only has 4 values
                    seasons = emisvar_df[emisvar_df['variation'].str.lower() == 'season']
                    print(seasons)
                    s_wrong = []
                    for row in seasons.iterrows():
                        #print('row', row[1].values[3:])
                        if len(row[1].values[3:]) != 4:
                            
                            s_wrong.append(seasons[source_id].values[0])
                    
                    
                    if len(s_wrong) > 0:
                        messagebox.showinfo("Seasonal Emissions Variation", 
                                        "Seasonal emissions variations require 4 "+
                                        "values. Sources: " + ", ".join(s_wrong) +
                                        " do not have the correct number of values. " +
                                        "Please update your Emission Variation File.")
             
             #check wind speed is only 6 values   
            if ('wspeed' in vtype):    
                    
    
                    wspeed = emisvar_df[emisvar_df['variation'].str.lower() == 'wspeed']
                    #print(wspeed)
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
                
                
                 #make sure the monthly emissions variation has 12 values
            if ('month'  in vtype):
                
                month = emisvar_df[emisvar_df['variation'].str.lower() == 'month']
                #print(wspeed)
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
            
                    
                    
              
            if ('hrofdy' in vtype or 'seashr' in vtype or 'shrdow' in vtype or 
                'shrdow7' in vtype):
                
                other = emisvar_df[~emisvar_df['variation'].str.lower().isin(['month', 'wspeed', 'season'])]
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
                    
               
                
            #make sure this is triggered correctly!
            self.log.append("Uploaded emissions variations for " + 
                                " ".join(var_ids))
            self.dataframe = emisvar_df
            
        
        