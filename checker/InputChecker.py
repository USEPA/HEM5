# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 13:08:48 2018

@author: jbaker
"""

import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from upload.EmissionsLocations import source_type
from upload.FacilityList import *


class InputChecker():
    
    def __init__(self, model):
        """
        The Input Checker takes the model class (with all inputs) and checks that
        required inputs (Facilities Options List, Hap Emissions, and Emissions Locations)
        are present and correspond to each other as well as additional optional inputs.
        
        There are two functions, check_required and check_dependent
        
        check_required returns the result dictionary with:
        - any error messages triggered
        - a list of dependent inputs flagged from the FOL
        - a reset key for an incorrectly uploaded required input (if applicable) 
        
        check_dependent
        
        """ 
        #pull in model
        self.model = model    
    
       
        

    def check_required(self):
        
        #store result in dictionary
        result = {'result': None, 'dependencies': [], 'reset': None  }
        
        #check if dataframe exists        
        try:
             self.model.faclist.dataframe
        
        #raise attribute error if it doesn't
        except AttributeError:
            logMsg = ("Facilities list options file uploaded incorrectly," + 
                      " please try again")
            
            result['result'] =  logMsg
            result['reset'] = 'fac'
            return result
        
        else:
            #make sure dataframe isn't empty
            if self.model.faclist.dataframe.empty:
                logMsg = ("There was an error uploading Facilities Options List" + 
                          " file, please try again")
                
                result['result'] =  logMsg
                return result
        
            
            #extract idsand determine if there are dependent uploads .
            else:
                fids = set(self.model.faclist.dataframe[fac_id])
        
                
                #find dependents and return which ones need to be checked
                #user receptors
                if 'Y' in self.model.faclist.dataframe[user_rcpt].tolist():
                    result['dependencies'].append(user_rcpt)
                    
                    
                #add bldgdw
                
                
                #add dep/depl
              
                         
        try:
             self.model.hapemis.dataframe
             
        except AttributeError:
            logMsg2 = "HAP Emissions file uploaded incorrectly, please try again"
            result['result'] =  logMsg2
            result['reset'] = 'hap'
            return result
        
        
        else:
            
            if self.model.hapemis.dataframe.empty:
                logMsg2 = ("There was an error uploading HAP Emissions file," +
                           " please try again")
                
                result['result'] =  logMsg2
                return result
        
                
            else:
                #get locations and source ids
                hfids = set(self.model.hapemis.dataframe[fac_id])
                
                
   
        try:
             self.model.emisloc.dataframe
             
        except AttributeError:
            logMsg3 = "Emissions Locations file uploaded incorrectly, please try again"
            
            result['result'] =  logMsg3
            return result
        
        
        else:
             if self.model.emisloc.dataframe.empty:
                logMsg3 = ("There was an error uploading Emissions Locations" + 
                           " file, please try again")
                
                result['result'] =  logMsg3
                result['reset'] = 'emis'
                return result
        
                
             else:
                #check facility id with emis loc ids
                efids = set(self.model.emisloc.dataframe[fac_id])
               
               
                
                #check source types for optional inputs
                
                if 'I' in self.model.emisloc.dataframe[source_type].tolist():
                    result['dependencies'].append('polyvertex')
                    
                if 'B' in self.model.emisloc.dataframe[source_type].tolist():
                    result['dependencies'].append('bouyant')
                    
                #check for deposition and depletion and pass to dep_check model
                
                
           
        
        #make sure emis locs has facility ids
        if fids.intersection(efids) != fids:   
            logMsg4 = ("The Emissions Locations file is missing one or more" + 
                       " facilities please make sure to upload the correct" + 
                       " Emissions Location file.")
            
            result['result'] =  logMsg4
            return result
        
        
        #make sure hapemis has facility ids      
        if fids.intersection(hfids) != fids:     
            logMsg5 = ("The HAP Emissions file is missing one or more" + 
                       " facilities please make sure to upload the correct HAP" + 
                       " Emissions file.")
            
            result['result'] =  logMsg5
            return result
        
        #make sure source ids match in hap emissions and emissions location
        #for facilities in faclist file
        
        hsource = set(self.model.hapemis.dataframe[self.model.hapemis.dataframe[fac_id].isin(fids.tolist())])
        esource = set(self.model.emisloc.dataframe[self.model.emisloc.dataframe[fac_id].isin(fids.tolist())])
        
        if hsource != esource:
            logMsg6 = ("Source ids for Hap Emissions and Emissions Locations" + 
                       " do not match, please upload corresponding files.")
            result['result'] =  logMsg6
            return result
         


        result['result'] =  'ready'
        return result
        


        
    def check_dependent(self, optional_list):
        
        #store result in dictionary
        result = {'result': None, 'reset': None  }
        
        for option in optional_list:
            
            if option is 'user_rcpt':
                
                try:
                    
                    self.model.ureceptr.dataframe
            
                except AttributeError:
                    logMsg7 = ("User receptors are specified in the Facilities" +
                              " List Options file, please upload user recptors" + 
                              " for " )
                    
                    result['result'] = logMsg7
                    result['reset'] = 'user_rcpt'
                    return result
                
                else:
                
                    #check facility ids in ureceptors 
                    uids = set(self.model.ureceptr.dataframe[fac_id])
                    fids = set(self.model.faclist.dataframe[fac_id])
                    
                    if fids.intersection(uids) != fids:
                        
                        missing = fids - uids
                        
                        logMsg7b = ("Facilities: " + ",".join(list(missing)) + 
                                    " are missing user receptors that were" +
                                    " indicated in the Facilities list options file")
            
                        result['result'] =  logMsg7b
                        result['reset'] = 'user_rcpt'
                        return result
                       
                
            elif option is 'bouyant_line':
                
                try:
                    
                    self.model.multibuoy.dataframe
                
                except AttributeError:
                    logMsg8 = ("Buoyant Line parameters are specified in the " + 
                               " Facilities List Options file, please upload " + 
                               " buoyant line sources for " )
                    
                    
                    result['result'] = logMsg8
                    result['reset'] = 'bouyant_line'
                    return result
                
                else:
                    
                    #check facility ids against bouyant line ids
                    bids = set(self.model.multibuoy.dataframe[fac_id])
                    fids = set(self.model.faclist.dataframe[fac_id])
                    
                    if fids.intersection(bids) != fids:
                        
                        missing = fids - bids
                        
                        logMsg8b = ("Facilities: " + ",".join(list(missing)) + 
                                    " are missing bouyant line sources that" +
                                    " were indicated in the Facilities list" +
                                    " options file")
            
                        result['result'] =  logMsg8b
                        result['reset'] = 'bouyant_line'
                        return result
                    
                    else:
                        #set ureceptr model option to TRUE
                        self.model.model_optns['ureceptr'] = True
                        
                
            elif option is 'polyvertex':
                
                try: 
                    
                    self.model.multipoly.dataframe
                    
                except AttributeError:
                    
                    logMsg9 = ("Polyvertex parameters are specified in the " + 
                               " Facilities List Options file, please upload " + 
                               " polyvertex sources for " )
                    
                    
                    result['result'] = logMsg9
                    result['reset'] = 'polyvertex'
                    return result
                       
                
                else:
                    
                    #check facility ids against polyvertex ids
                    pids = set(self.model.multipoly.dataframe[fac_id])
                    fids = set(self.model.emisloc.dataframe[self.model.emisloc.dataframe[source_type] == 'I'][fac_id].values)
                    print('pids', pids)
                    print('fids', fids)
                    
                    if fids.intersection(pids) != fids:
                        
                        missing = fids - pids
                        
                        logMsg9b = ("Facilities: " + ",".join(list(missing)) + 
                                    " are missing polyvertex sources that" +
                                    " were indicated in the Facilities list" +
                                    " options file")
            
                        result['result'] =  logMsg9b
                        result['reset'] = 'poly_vertex'
                        return result
                
        
        result['result'] = 'ready'
        return result
    

