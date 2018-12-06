# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 14:39:53 2118

@author: dlindsey
"""


#for testing
#facops = pd.read_excel("Template_Multi_Facility_List_Options_part_dep_sort_test.xlsx")
#facops.rename(columns={'FacilityID':'fac_id'}, inplace=True)

def sort(facops):
    
    """
    
    """
    print('facility slice:', facops)
    print('phase', facops['phase'])
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
        
   
    
    
        return {'phase': phase, 'settings': opts}
    
        ## split it into two lists, duplicate the row and call dep_sort on each?