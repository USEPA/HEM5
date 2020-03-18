# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 15:21:42 2018

@author: dlindsey
"""
import numpy as np
#for testing
#facops = pd.read_excel("Template_Multi_Facility_List_Options_dep_deplt_test.xlsx")
#facops.rename(columns={'FacilityID':'fac_id'}, inplace=True)
from com.sca.hem4.upload.EmissionsLocations import method


def check_phase(r):
    
    print('facility', r['fac_id'])
                
    print('vdep:', r['vdep'])
    
    print('vdepl:', r['vdepl'])
    
    print('pdep:', r['pdep'])
    
    print ('pdepl:', r['pdepl'])
    
    if r['vdep'] is not np.nan:
        if r['vdep'] is not 'NO':
            vdep = r['vdep'].upper()
    else:
        vdep = ''
    
    
    if r['vdepl'] is not np.nan:
        if r['vdepl'] is not 'NO':
            vdepl = r['vdepl']
        
    else:
        vdepl = ''
    
    
    if r['pdep'] is not np.nan:
        if r['pdep'] is not 'NO':
            pdep = r['pdep']
        
    else:
        pdep = ''
    
    if r['pdepl'] is not np.nan:
        if r['pdepl'] is not 'NO':
            pdepl = r['pdepl']
        
    else:
        pdepl = ''
        
        
    poss = ['DO', 'WO', 'WD']
    
    
    phaseResult = []
     
    if vdep in poss or vdepl in poss:
        if pdep in poss:
            phase = 'B'
            phaseResult.append(phase)
            
        elif pdepl in poss:
            phase = 'B'
            phaseResult.append(phase)      
    
    if vdep in poss or vdepl in poss: 
    
        if pdep not in poss:
            phase = 'V'
            phaseResult.append(phase)
            
        elif pdepl not in poss:
            phase = 'V'
            phaseResult.append(phase)
        
    if pdep in poss or pdepl in poss:
    
        if vdep not in poss:
            phase = 'P'
            phaseResult.append(phase)
            
        elif vdepl not in poss:
            phase = 'P'
            phaseResult.append(phase)
    

        
    if len(phaseResult) > 1:
        phaseResult = 'B'
        
    elif len(phaseResult) == 1:
        phaseResult = phaseResult[0]
        
    else:
        phaseResult = ''
        
     
    print(phaseResult)
    return(phaseResult)

def check_dep(faclist_df, emisloc_df):
    """
    Looks through deposition and depletion flags and returns optional inputs and 
    dataframe with keywords.
    
    """
    
    inputs = []
                
            
    
    phase = faclist_df[['fac_id', 'phase']].values

    
#    phase = phaseList
#    print('NEW PHASE LIST:', phase)

    
    deposition = faclist_df['dep'].tolist()
    vapor_depo = faclist_df['vdep'].tolist()
    part_depo = faclist_df['pdep'].tolist()
    
    depletion = faclist_df['depl'].tolist()
    vapor_depl = faclist_df['vdepl'].tolist()
    part_depl = faclist_df['pdepl'].tolist()
    
#    print("phase", phase)
#    
#    print("deposition:", deposition, type(deposition))
#    print("vapor deposition:", vapor_depo)
#    print("particle deposition:", part_depo)
#    
#    
#    print("depletion:", depletion)
#    print("vapor depletion", vapor_depl)
#    print("particle depletion", part_depl)
    
    #loop through each positionally
    i = 0
    for fac_id, p in phase:
        
        
        if p == 'P':

            if usingMethodOne(emisloc_df):
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
                    if usingMethodOne(emisloc_df):
                        options.append('particle size')
                
                    if 'WD' or 'DO' in vapor_depo[i]:
                        options.append('land use')
                        options.append('seasons')
            
                elif 'NO' in part_depo[i] and 'WD' or 'DO' in vapor_depo[i]:
                     options.append('land use')
                     options.append('seasons')
                
            elif (depletion[i] == 'Y' and deposition[i] != 'Y'):
                
                if 'DO' or 'WO' or 'WD' in part_depl[i]:

                    if usingMethodOne(emisloc_df):
                        options.append('particle size')

                    if 'WD' or 'DO' in vapor_depl[i]:
                        options.append('land use')
                        options.append('seasons')                        
                
                elif 'NO' in part_depl[i] and 'WD' or 'DO' in vapor_depl[i]:
                    options.append('land use')
                    options.append('seasons')
                    
                elif 'NO' in part_depl[i] and 'NO' in vapor_depl[i]:
                    if usingMethodOne(emisloc_df):
                        options.append('particle size')
    
    
            elif (deposition[i] == 'Y' and depletion[i] == 'Y'):
                
                if ('DO' or 'WO' or 'WD' in part_depo[i] and 
                    'DO' or 'WO' or 'WD' in part_depl[i]):

                    if usingMethodOne(emisloc_df):
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
     
    print("inputs", inputs)  
     
    return(inputs)

def usingMethodOne(emisloc_df):
    return 1 in emisloc_df[method].values

def sort(facops):

    """

    """
    #print('facility slice:', facops)
    #Sprint('phase', facops['phase'])
    phase = facops['phase'].tolist()[0].upper()                    # Phase

    depos = facops['dep'].fillna("").tolist()[0]                       # Deposition
    vdepo = facops['vdep'].fillna("").tolist()[0]                       # Vapor Deposition
    pdepo = facops['pdep'].fillna("").tolist()[0]                       # Particle Deposition

    deple = facops['depl'].fillna("").tolist()[0]                       # Depletion
    vdepl = facops['vdepl'].fillna("").tolist()[0]                       # Vapor Depletion
    pdepl = facops['pdepl'].fillna("").tolist()[0]                       # Particle Depletion

    if depos == "":
        depos = "N"

    if deple =="":
        deple = "N"

    ## don't forget to call upper!

    if phase == 'P' or phase =='V':

        return single_phase(phase, depos, deple, vdepo, pdepo, vdepl, pdepl)

    elif phase == 'B':

        #construct particle and vapor runs separately
        particle = single_phase('P', depos, deple, None, pdepo, None, pdepl)

        vapor = single_phase('V', depos, deple, vdepo, None, vdepl, None)

        return [particle, vapor]




    ##order matters for pahse 'B'-- particle first, then vapor

##order matters for phase 'B'-- particle first, then vapor
def single_phase(phase, depos, deple, vdepo, pdepo, vdepl, pdepl):

    opts = []
    if "Y" in depos:

        if pdepo == "WO" or vdepo == "WO":
            if deple == "N":
                opts.append(" WDEP NOWETDPLT ")
            else:
                opts.append(" WDEP ")

        #        if phase == 'B':
        #            if pdepo == "WO" and vdepo == "WO":
        #                opts.append(" WDEP NOWETDPLT ")

        if pdepo == "DO" or vdepo == "DO":
            if deple == "N":
                opts.append(" DDEP NODRYDPLT ")
            else:
                opts.append(" DDEP ")

        #        if phase == 'B':
        #            if pdepo == "DO" and vdepo == "DO":
        #                opts.append(" DDEP NODRYDPLT ")

        if pdepo == "WD" or vdepo == "WD":
            if deple == "N":
                opts.append(" WDEP DDEP NOWETDPLT NODRYDPLT ")
            else:
                opts.append(" WDEP DDEP ")

        #        if phase == 'B':
        #            if pdepo == "WD" and vdepo == "WD":
        #                opts.append(" WDEP DDEP NOWETDPLT NODRYDPLT ")
        if pdepo == 'NO' or vdepo == 'NO':
            opts.append("")
    #----------------------------------------------------------------------------------------
    if "Y" in deple:
        #            print(deple)
        #            print(pdepl)
        if pdepl == "WD" or vdepl == "WD":
            if depos == "N":
                opts.append(" WETDPLT DRYDPLT ")

            else:
                opts.append(" WDEP DDEP " )

        if pdepl == "DO" or vdepl == "DO":
            if depos == "N":
                opts.append(" DRYDPLT ")
            else:
                opts.append(" DDEP ")

        if pdepl == "WO" or vdepl == "WO":
            if depos == "N":
                opts.append(" WETDPLT ")

            else:
                opts.append(" WDEP ")

        if pdepl == 'NO' or vdepl == 'NO':
            opts.append("")

    print('Keyword', opts)
    return {'phase': phase, 'settings': opts}

    ## split it into two lists, duplicate the row and call dep_sort on each?
#dep_test = check_dep(facops)