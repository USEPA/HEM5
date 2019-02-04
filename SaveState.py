# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 23:10:19 2019

@author: David Lindsey

"""
import traceback
import os
from model.Model import *


class SaveState():
    
    def __init__(self, runid, model):
        
        self.runid = runid
        self.model = model
        
        #create folder to save files in 
       #set output folder
        save_folder = "save/"+self.runid + "/"
        self.save_folder = save_folder
       
        try:
            os.makedirs(save_folder)
            
        except Exception as ex:

            exception = ex
            fullStackInfo=''.join(traceback.format_exception(
                etype=type(ex), value=ex, tb=ex.__traceback__))

            message = "An error occurred while running a facility:\n" + fullStackInfo
            print(message)
           
        else:
            print("created", self.save_folder)
        
        

    def save_model(self, facid):
        
        print("removing fac id:", facid)
        
        attr_list = (['faclist', 'emisloc', 'hapemis', 'multipoly', 'multibuoy',
                      'ureceptr', 'haplib', 'bldgdw', 'partdep', 'landuse', 
                      'seasons', 'emisvar'])
        #get list of attributes and write them 
        
        #print("model attributes", self.model.__dict__)
        
        for k, v in self.model.__dict__.items():
        
            if k in attr_list and v is not None:
                
               #remove the faclist row then pickle
               
               remaining = v.dataframe[v.dataframe['fac_id'] != facid]
               
               #pikle
               remaining.to_pickle(f"{self.save_folder}/{k}.pkl")
               
               
               print(k, 'pickled')
                
        
            
#            pass
#        else:
#            os.makedirs(save_folder)
#        
            
        
        #remove facid row from all source inputs
        
#        faclist = model.faclist.dataframe
#        
#        emisloc = model.emisloc.dataframe
#        
#        hapemis = model.hapemis.dataframe
#        
#        
#         #%%---------- Optional User Receptors -----------------------------------------
#    
#        if hasattr(model.ureceptr, "dataframe"):
#            pass
#    
#        
#         #%%---------- Optional Buoyant Line Parameters ----------------------------------------- 
#    
#        if hasattr(model.multibuoy, "dataframe"):
#    
#            buoyant_df = model.multibuoy.dataframe.loc[ model.multibuoy.dataframe[fac_id] == facid].copy()
#    
#        #%%---------- Optional Polygon Vertex File ----------------------------------------- 
#    
#    
#        if hasattr(model.multipoly, "dataframe"):
#            pass
#        
#           #%%---------- Optional Building Downwash -------------------------------------
#        
#        if hasattr(model.bldgdw, "dataframe"):
#    
#                bldgdw_df = model.bldgdw.dataframe.loc[model.bldgdw.dataframe[fac_id] == facid].copy()
#    
#    
#            #%% ------ Optional Particle Data -------------------------------------
#    
#        if hasattr(model.partdep, "dataframe"):
#    
#            partdia_df = model.partdep.dataframe.loc[model.partdep.dataframe[fac_id] == facid].copy()
#    
#    
#    
#        #%% -- Optional Land Use ----------------------------------------------
#    
#        if hasattr(model.landuse, "dataframe"):
#            landuse_df = model.landuse.dataframe.loc[model.landuse.dataframe[fac_id] == facid].copy()
#    
#    
#    
#        #%% --- Optional Seasons ---------------------------------------------
#    
#        if hasattr(model.seasons, "dataframe"):
#            seasons_df = model.seasons.dataframe.loc[model.seasons.dataframe[fac_id] == facid].copy()
#    
#    
#        #%% --- Optional Emissions Variations --------------------------------
#    
#        if hasattr(model.emisvar, "dataframe"):
#            
#           pass
#    
#       
