"""
Created:   Thu Jun 01, 2017, 11:46
Last Edit: Thu Jun 01, 2017, 13:30

@author: jbaker

Inputs:
    Requires : lat, lon, nad
    Optional : 

Outputs:
    Primary  : utmn, utme, utmz
"""
# %% START PROGRAM

def ll2utm(lat,lon,zone):
        
    # %% Import Modules
    
    import numpy as np
    import math as m
    
    utmn = np.zeros(len(lat))
    utme = np.zeros(len(lat))
    utmz = np.zeros(len(lat))
    nad = 83*np.ones(len(lat))

    # %% Main For Loop
    
    for i in np.arange(len(lat)):
        
        if int(lon[i]) > 180 and int(lat[i]) > 90:
            utmn[i] = lat[i]
            utme[i] = lon[i]
            utmz[i] = zone[i]
        else:
        
            # %% Latitude - Longitude Conversions
            
            if lon[i] < 0.:
                nlon = -1 * lon[i]
            else:
                nlon = 360.0 - lon[i]
            
            # %% Datum Constants
            
            # NAD 27
            if nad[i] == 27:
                sf =       0.9996
                er = 6378206.4          # Equatorial Radius of Ellipsoid
                rf =     294.978698     # Reciprocal of Flattening of the Ellipsoid
                
            # NAD 83
            else:
                sf =       0.9996
                er = 6378137.0          # Equatorial Radius of Ellipsoid
                rf =     298.257222101  # Reciprocal of Flattening of the Ellipsoid
                
            # %% Constant Calculation
            
            F   = ( 1.0 / rf )
            esq = ( F + F - F**2 )
            eps = ( esq / ( 1.0 - esq ) )
            pr  = ( ( 1.0 - F ) * er )
            en  = ( ( er - pr ) / ( er + pr ) )
            
            a = ( -1.5 * en ) + ( ( 9.0 / 16.0 ) * en**3 )
            b = ( 0.9375 * en**2 ) - ( ( 15.0 / 32.0 ) * en**4 )
            c = ( - ( 35.0 / 48.0 ) * en**3 )
            
            r = ( er * ( 1 - en ) * ( 1 - en**2 ) * ( 1 + ( 2.25 * en**2 ) + ( 225 / 64 ) * en**4 ) )
            
            fe   = 500000.0              # Prescribe a false easting coordinate
            dtr  = ( m.pi / 180.0 )      # Conversion from degrees to radians
            lond = int(nlon)
            
            
            # %%  Find the Zone for Longitude Less Than 180 Degrees
            
            if nlon < 180:
                
                if zone[i] == 0:
                    iz = int(lond / 6)
                    iz = ( 30 - iz )
                elif zone[i] == "":
                    iz = int(lond / 6)
                    iz = ( 30 - iz )
                else:
                    iz = zone[i]
                    
                icm = ( 183 - ( 6 * iz ) )
                cm  = ( icm * dtr )
                ucm = ( ( icm + 3 ) * dtr )
                lcm = ( ( icm - 3 ) * dtr )
                
            # ... for Longitude Greater Than 180 Degrees
            
            if nlon > 180:
                if zone[i] == 0:
                    iz = int(lond / 6)
                    iz = ( 90 - iz )
                else:
                    iz = zone[i]
                    
                icm = ( 543 - ( 6 * iz ) )
                cm  = ( icm * dtr )
                ucm = ( icm + 3 ) * dtr
                lcm = ( icm - 3 ) * dtr
            
            # %% Continue Constant Calculation with Zone Outputs
            
            fi    = ( lat[i] * dtr )
            lam   = ( nlon * dtr )
            om    = ( fi + ( a * np.sin( 2.0 * fi ) ) + ( b * np.sin( 4.0 * fi ) ) + ( c * np.sin( 6.0 * fi ) ) )
            s     = ( r * om * sf )
            sinfi = ( np.sin( fi ) )
            cosfi = ( np.cos( fi ) )
            tn    = ( sinfi / cosfi )
            ts    = ( tn * tn )
            ets   = ( eps * cosfi**2 )
            l     = ( ( lam - cm ) * cosfi )
            ls    = ( l * l )
            rn    = ( sf * er / np.sqrt( 1.0 - esq * sinfi**2 ) )
            
            # %% Calculation of A constants for UTM Conversion
            
            a1 = ( -1 * rn )
            a2 = ( rn * tn / 2.0 )
            a3 = ( ( 1.0 - ts + ets ) / 6.0 )
            a4 = ( ( 5.0 - ts + ets * ( 9.0 + 4.0 * ets ) ) / 12.0 )
            a5 = ( ( 5.0 + ts * ( ts - 18.0 ) + ets * ( 14.0 - 58.0 * ts ) ) / 120.0 )
            a6 = ( ( 61.0 + ts * ( ts - 58.0 ) + ets * ( 270.0 - 330.0 * ts ) ) / 360.0 )
            a7 = ( ( 61.0 - 479.0 * ts + 179.0 * ts**2 - ts**3 ) / 5040.0 )
            
            # %% Finally, Compute UTM Coordainates
            
            utmn[i] = round( s + a2 * ls * ( 1.0 + ls * ( a4 + a6 * ls ) ) )
            utme[i] = round( fe + a1 * l * (1.0 + ls * (a3 + ls * (a5 + a7 * ls ) ) ) )
            utmz[i] = iz
            
    return utmn, utme, utmz
        
    # %% END PROGRAM