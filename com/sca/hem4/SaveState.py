# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 23:10:19 2019

@author: David Lindsey

"""
import traceback
import os
import shutil


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
        
        #if faclist is greater than 1 fac_id then save
        if len(self.model.faclist.dataframe[fac_id]) > 1:
            #loop through dataframes
        
            for k, v in self.model.__dict__.items():
            
                if k in attr_list and v is not None:

                   #remove the faclist row then pickle
                   try:
                       
                       remaining = v.dataframe[v.dataframe['fac_id'] != facid]
                       
                   except:
                       
                       #means its does response or some other df
                       pass
                       
                   else:
                   
                   #pikle
                       remaining.to_pickle(f"{self.save_folder}/{k}.pkl")
                       print(k, 'pickled')
                       
      
            
                
    def remove_folder(self):
        
        #remove save folder and everythign else
        shutil.rmtree(self.save_folder)
        
