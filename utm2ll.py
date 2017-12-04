"""
Created:   Thu Jun 01, 2017, 11:46
Last Edit: Thu Jun 01, 2017, 13:30

@author: jbaker

Inputs:
    Requires : lat, lon, nad
    Optional : 

Outputs:
    Primary  : utmn, utme, zone
"""
# %% START PROGRAM

def utm2ll(utmn,utme,zone):
        
    # %% Import Modules
    
    import numpy as np
    import math as m
    import sys

    
    lat = np.zeros(len(utmn))
    lon = np.zeros(len(utme))
    nad = 83*np.ones(len(utmn))
        
    # %% Main For Loop
     
    for i in np.arange(len(utmn)):
        
        if utmn[i] < 180 and utme[i] < 90:
            lat[i] = utmn[i]
            lon[i] = utme[i]
        else:
    
        # %% Datum Constants
        
            if nad[i] == 27:
                sf =        0.9996
                er =  6378206.4
                rf =      294.978698
            else:
                sf =        0.9996
                er =  6378137.0
                rf =      298.257222101
                
            raddeg = ( 180.0 / m.pi )
            degrad = ( m.pi / 180.0 )
            
            fe = 500000.0
            
            # %% Find the Central Median if the Zone Number is < 30
            
            if zone[i] < 30:
                iz  = int(zone[i])
                icm = ( 183 - ( 6 * iz ) )
                cm  = ( icm * degrad )
                ucm = ( icm + 3 ) * degrad
                lcm = ( icm - 3 ) * degrad
            
            # ... if the Zone Number is > 30
            
            if zone[i] > 30:
                iz  = int(zone[i])
                icm = ( 543 - ( 6 * iz ) )
                cm  = ( icm * degrad )
                ucm = ( ( icm + 3 ) * degrad )
                lcm = ( ( icm - 3 ) * degrad )
            
            # %% Constant Calculations
            
            F   = ( 1 / rf )
            esq = ( F + F - F * F )
            eps = ( esq / ( 1 - esq ) )
            pr  = ( ( 1 - F ) * er )
            en  = ( er - pr ) / ( er + pr )
            en2 = ( en * en )
            en3 = ( en * en * en )
            en4 = ( en2 * en2 )
            
            # %% Calculation of Additional UTM Constants
            
            c2 = ( 3 * en / 2 - 27 * en3 / 32 )
            c4 = ( 21 * en2 / 16 - 55 * en4 / 32 )
            c6 = ( 151 * en3 / 96 )
            c8 = ( 1097 * en4 / 512 )
            
            v0 = ( 2 * ( c2 - 2 * c4 + 3 * c6 - 4 * c8 ) )
            v2 = ( 8 * ( c4 - 4 * c6 + 10 * c8 ) )
            v4 = ( 32 * ( c6 - 6 * c8 ) )
            v6 = ( 128 * c8 )
            
            # %% Continue Constant Calculations
            
            r = ( er * ( 1 - en ) * ( 1 - en * en ) * ( 1 + 2.25 * en * en + ( 225 / 64 ) * en4 ) )
            
            om     = ( utmn[i] / ( r * sf ) )
            cosom  = ( np.cos(om) )
            t_foot = ( om + np.sin(om) * cosom * ( v0 + v2 * cosom * cosom + v4 * cosom**4 + v6 * cosom**6 ) )
            sinf   = ( np.sin(t_foot) )
            cosf   = ( np.cos(t_foot) )
            tn     = ( sinf / cosf )
            ts     = ( tn * tn )
            ets    = ( eps * cosf * cosf )
            rn     = ( er * sf / np.sqrt(1 - esq * sinf * sinf) )
            q      = ( ( utme[i] - fe ) / rn )
            qs     = ( q * q )
            
            # %% Calculation of B Constants for UTM Conversion
            
            b1 = 1
            b2 = ( -1 * tn * ( 1 + ets ) / 2 )
            b3 = ( -1 * ( 1 + ts + ts + ets ) / 6 )
            b4 = ( -1 * ( 5 + 3 * ts + ets * ( 1 - 9 * ts ) - 4 * ets * ets ) / 12 )
            b5 = ( ( 5 + ts * ( 28 + 24 * ts ) + ets * (46 - 252 * ts - 60 * ts * ts ) ) / 360 )
            b6 = ( ( 61 + 45 * ts * ( 2 + ts ) + ets * ( 46 - 252 * ts - 60 * ts *ts ) ) / 360 )
            b7 = ( -1 * ( 61 + 662 * ts + 1320 * ts * ts + 720 * ts**3 ) / 5040 )
            
            # %% Initial Calculation of Latitude & Longitude
            
            tlat = ( t_foot + b2 * qs * ( 1 + qs * ( b4 + b6 * qs ) ) )
            l    = ( b1 * q * ( 1 + qs * ( b3 + qs * ( b5 + b7 * qs ) ) ) )
            tlon = ( -1 * l ) / cosf + cm
            
            # %% Finally, Compute Latitude/Longitude Degrees
            
            lat[i] = ( tlat * raddeg )
            lon[i] = ( ( -1 * tlon ) * raddeg )
        
    return lat, lon
        
    # %% END PROGRAM