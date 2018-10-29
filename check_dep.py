# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 15:21:42 2018

@author: dlindsey
"""
import pandas as pd
import math

#for testing
#facops = pd.read_excel("Template_Multi_Facility_List_Options_dep_deplt_test.xlsx")
#facops.rename(columns={'FacilityID':'fac_id'}, inplace=True)

def check_dep(dataframe):
    """
    Looks through deposition and depletion flags and returns optional inputs and 
    dataframe with keywords.
    
    """
    
    inputs = []
    
    
    phase = dataframe[['fac_id', 'phase']].values

    
    deposition = dataframe['dep'].tolist()
    vapor_depo = dataframe['vdep'].tolist()
    part_depo = dataframe['pdep'].tolist()
    
    depletion = dataframe['depl'].tolist()
    vapor_depl = dataframe['vdepl'].tolist()
    part_depl = dataframe['pdepl'].tolist()
    
    print("phase", phase)
    
    print("deposition:", deposition, type(deposition))
    print("vapor deposition:", vapor_depo)
    print("particle deposition:", part_depo)
    
    
    print("depletion:", depletion)
    print("vapor depletion", vapor_depl)
    print("particle depletion", part_depl)
    
    #loop through each positionally
    i = 0
    for fac_id, p in phase:
        
        
        if p == 'P':
            #add facid
            options = [fac_id]
            options.append('particle size')
      
            inputs.append(options)
                            
        elif p == 'V':
            #add facid
            options = [fac_id]
            
            if (deposition[i] == 'Y' and depletion[i] != 'Y'):
                
                if 'DO' or 'WD' in vapor_depo[i]:
                    options.append('land use')
                    options.append('seasons')
                    
            elif deposition[i] == 'Y' and depletion[i] == 'Y':
                if 'DO' in vapor_depo[i] and 'DO' in vapor_depl[i]:
                    options.append('land use')
                    options.append('seasons')
            
            
                elif 'WD' in vapor_depo[i] and 'WD' in vapor_depl[i]:
                    options.append('land use')
                    options.append('seasons')
            
            inputs.append(options)
      
        elif p == 'B':
            #add facid
            options = [fac_id]
            
            if (deposition[i] == 'Y' and depletion[i] != 'Y'): 
            
                if 'DO' or 'WO' or 'WD' in part_depo[i]:
                    options.append('particle size')
                
                    if 'WD' or 'DO' in vapor_depo[i]:
                        options.append('land use')
                        options.append('seasons')
            
                elif 'NO' in part_depo[i] and 'WD' or 'DO' in vapor_depo[i]:
                     options.append('land use')
                     options.append('seasons')
                
            elif (depletion[i] == 'Y' and deposition[i] != 'Y'):
                
                if 'DO' or 'WO' or 'WD' in part_depl[i]:
                    options.append('particle size')
                
                elif 'NO' in part_depl[i] and 'WD' or 'DO' in vapor_depl[i]:
                    options.append('land use')
                    options.append('seasons')
                    
                elif 'NO' in part_depl[i] and 'NO' in vapor_depl[i]:
                    options.append('particle size')
    
    
            elif deposition == 'Y' and depletion == 'Y':
                
                if ('DO' or 'WO' or 'WD' in part_depo[i] and 
                    'DO' or 'WO' or 'WD' in part_depl[i]):
                    options.append('particle size')
                    
                    if ('WD' or 'DO' in vapor_depo[i] and 
                        'WD' or 'DO' in vapor_depl[i]):
                        options.append('land use')
                        options.append('seasons')
                    
                elif 'NO' in part_depo[i] and 'NO' in part_depl[i]:
                    if ('WD' or 'DO' in vapor_depo[i] and 
                        'WD' or 'DO' in vapor_depl[i]):
                        options.append('land use')
                        options.append('seasons')
                    
         
            inputs.append(options)
        i += 1
     
    #print(inputs)  
     
    return(inputs)
    
    

#dep_test = check_dep(facops)