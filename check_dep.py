# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 15:21:42 2018

@author: dlindsey
"""
import pandas as pd
import math





def check_dep(dataframe):
    """
    Looks through deposition and depletion flags and returns optional inputs and 
    dataframe with keywords.
    
    """
    
    inputs = []
    
    
    phase = dataframe['phase'].tolist()
    
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
    
    for i in range(len(phase)):
        
        if phase[i] == 'P':
            
            if deposition[i] == 'Y' and depletion[i] == 'N':
                
                #all particle deposition uses particle size file
                inputs.append('particle size')
                
                if 'DO' or 'WD' in part_depo[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
                                
            elif deposition[i] == 'N' and depletion[i] == 'Y':
                inputs.append('particle size')
                                
            elif deposition[i] == 'Y' and depletion[i] == 'Y':
                inputs.append('particle size')
                
                if 'DO' in part_depo[i] and 'DO' in part_depl[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
                    
                elif 'WD' in part_depo[i] and 'WD' in part_depl[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
                            
        elif phase[i] == 'V':
            
            if deposition[i] == 'Y' and depletion[i] == 'N':
                if 'DO' or 'WD' in vapor_depo[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
                    
            elif deposition[i] == 'Y' and depletion[i] == 'Y':
                if 'DO' in vapor_depo[i] and 'DO' in vapor_depl[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
            
            
                elif 'WD' in vapor_depo[i] and 'WD' in vapor_depl[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
      
        elif phase[i] == 'B':
               
            if deposition[i] == 'Y' and depletion[i] == 'N': 
            
                if 'DO' or 'WO' or 'WD' in part_depo[i]:
                    inputs.append('particle size')
                
                    if 'WD' or 'DO' in vapor_depo[i]:
                        inputs.append('land use')
                        inputs.append('vegetation')
            
                elif 'NO' in part_depo[i] and 'WD' or 'DO' in vapor_depo[i]:
                     inputs.append('land use')
                     inputs.append('vegetation')
                
            elif depletion[i] == 'Y' and deposition[i] == 'N':
                
                if 'DO' or 'WO' or 'WD' in part_depl[i]:
                    inputs.append('particle size')
                
                elif 'NO' in part_depl[i] and 'WD' or 'DO' in vapor_depl[i]:
                    inputs.append('land use')
                    inputs.append('vegetation')
                    
                elif 'NO' in part_depl[i] and 'NO' in vapor_depl[i]:
                    inputs.append('particle size')
    
    
            elif deposition == 'Y' and depletion == 'Y':
                
                if ('DO' or 'WO' or 'WD' in part_depo[i] and 
                    'DO' or 'WO' or 'WD' in part_depl[i]):
                    inputs.append('particle size')
                    
                    if ('WD' or 'DO' in vapor_depo[i] and 
                        'WD' or 'DO' in vapor_depl[i]):
                        inputs.append('land use')
                        inputs.append('vegetation')
                    
                elif 'NO' in part_depo[i] and 'NO' in part_depl[i]:
                    if ('WD' or 'DO' in vapor_depo[i] and 
                        'WD' or 'DO' in vapor_depl[i]):
                        inputs.append('land use')
                        inputs.append('vegetation')
                    
                    
    
    return(set(inputs))
    
    

