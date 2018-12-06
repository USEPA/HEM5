import numpy as np
import sys
import math as m
import pandas as pd

utme = 'utme';
utmn = 'utmn';
utmzone = 'utmzone';
utmz = 'utmz';
utms = 'utms';

class UTM:
    """
    A utility class with functions related to UTM zones.
    """

    @staticmethod
    def zone2use(el_df):

        """
        Create a common UTM Zone for this facility

        All emission sources input to Aermod must have UTM coordinates
        from a single UTM zone. This function will determine the single
        UTM zone to use. Parameter is the emissions location data frame.

        """

        # First, check for any utm zones provided by the user in the emission location file
        utmzones_df = el_df["utmzone"].loc[el_df["location_type"] == "U"]
        if utmzones_df.shape[0] > 0:
            # there are some; find the smallest one
            min_utmzu = int(np.nan_to_num(utmzones_df).min(axis=0))
        else:
            min_utmzu = 0

        # Next, compute utm zones from any user provided longitudes and find smallest
        lon_df = el_df[["lon"]].loc[el_df["location_type"] == "L"]
        if lon_df.shape[0] > 0:
            lon_df["z"] = ((lon_df["lon"]+180)/6 + 1).astype(int)
            min_utmzl = int(np.nan_to_num(lon_df["z"]).min(axis=0))
        else:
            min_utmzl = 0

        if min_utmzu == 0:
            utmzone = min_utmzl
        else:
            if min_utmzl == 0:
                utmzone = min_utmzu
            else:
                utmzone = min(min_utmzu, min_utmzl)

        if utmzone == 0:
            print("Error! UTM zone is 0")
            sys.exit()
        ########### Route error to log ##################

        return utmzone

    @staticmethod
    def utm2ll(utmn,utme,zone):

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

    @staticmethod
    def ll2utm(lat,lon,zone):

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

    @staticmethod
    def ll2utm_alt(lat,lon,zone):
        lat = float(lat)
        lon = float(lon)

        #print(lon)
        #print(lat)

        utmn = 0
        utme = 0
        utmz = zone
        nad = 83

        # %% Main For Loop

        if int(lon) > 180 and int(lat) > 90:
            utmn = lat
            utme = lon
            utmz = zone
        else:

            # %% Latitude - Longitude Conversions

            if lon < 0.:
                nlon = -1 * lon
            else:
                nlon = 360.0 - lon

            # %% Datum Constants

            # NAD 27
            if nad == 27:
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

                if zone == 0:
                    iz = int(lond / 6)
                    iz = ( 30 - iz )
                elif zone == "":
                    iz = int(lond / 6)
                    iz = ( 30 - iz )
                else:
                    iz = zone

                icm = ( 183 - ( 6 * iz ) )
                cm  = ( icm * dtr )
                ucm = ( ( icm + 3 ) * dtr )
                lcm = ( ( icm - 3 ) * dtr )

            # ... for Longitude Greater Than 180 Degrees

            if nlon > 180:
                if zone == 0:
                    iz = int(lond / 6)
                    iz = ( 90 - iz )
                else:
                    iz = zone

                icm = ( 543 - ( 6 * iz ) )
                cm  = ( icm * dtr )
                ucm = ( icm + 3 ) * dtr
                lcm = ( icm - 3 ) * dtr

            # %% Continue Constant Calculation with Zone Outputs

            fi    = ( lat * dtr )
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

            utmn = round( s + a2 * ls * ( 1.0 + ls * ( a4 + a6 * ls ) ) )
            utme = round( fe + a1 * l * (1.0 + ls * (a3 + ls * (a5 + a7 * ls ) ) ) )
            utmz = iz


        return [utmn, utme, utmz]


    def center(sourcelocs, utmz):

        # Fill up lists of x and y coordinates of all source vertices    
        vertx_l = []
        verty_l = []
        for index, row in sourcelocs.iterrows():
    
            vertx_l.append(row["utme"])
            verty_l.append(row["utmn"])
    
            # If this is an area source, add the other 3 corners to vertex list
            if row["source_type"].upper() == "A":
                angle_rad = m.radians(row["angle"])
                utme1 = row["utme"] + row["lengthx"] * m.cos(angle_rad)
                utmn1 = row["utmn"] - row["lengthx"] * m.sin(angle_rad)
                utme2 = (row["utme"] + (row["lengthx"] * m.cos(angle_rad)) +
                         (row["lengthy"] * m.sin(angle_rad)))
                utmn2 = (row["utmn"] + (row["lengthy"] * m.cos(angle_rad)) -
                         (row["lengthx"] * m.sin(angle_rad)))
                utme3 = row["utme"] + row["lengthy"] * m.sin(angle_rad)
                utmn3 = row["utmn"] + row["lengthy"] * m.cos(angle_rad)
                vertx_l.append(utme1)
                vertx_l.append(utme2)
                vertx_l.append(utme3)
                verty_l.append(utmn1)
                verty_l.append(utmn2)
                verty_l.append(utmn3)
    
            # If this is a volume source, then add the vertices of it
            if row["source_type"].upper() == "V":
                utme1 = row["utme"] + row["lengthx"] * m.sqrt(2)/2
                utmn1 = row["utmn"] - row["lengthy"] * m.sqrt(2)/2
                utme2 = row["utme"] + row["lengthx"] * m.sqrt(2)/2
                utmn2 = row["utmn"] + row["lengthy"] * m.sqrt(2)/2
                utme3 = row["utme"] - row["lengthx"] * m.sqrt(2)/2
                utmn3 = row["utmn"] + row["lengthy"] * m.sqrt(2)/2
                vertx_l.append(utme1)
                vertx_l.append(utme2)
                vertx_l.append(utme3)
                verty_l.append(utmn1)
                verty_l.append(utmn2)
                verty_l.append(utmn3)
    
            # If line or buoyant line source, add second vertex
            if row["source_type"].upper() == "N" or row["source_type"].upper() == "B":
                vertx_l.append(row["utme_x2"])
                verty_l.append(row["utmn_y2"])
    
            #TODO  If a polygon source, read the polygon vertex file
    
        vertx_a = np.array(vertx_l)
        verty_a = np.array(verty_l)
    
        # Combine the x and y vertices lists into list of tuples and then get a
        # unique list of vertices of the form (x, y) where x=utme and y=utmn
        sourceverts = list(zip(vertx_l, verty_l))
        unique_verts = list(set(sourceverts))
    
        # Find the two vertices that are the farthest apart
        # Also find the corners of the modeling domain
    
        max_dist = 0
        max_x = min_x = unique_verts[0][0]
        max_y = min_y = unique_verts[0][1]
    
        if len(unique_verts) > 1: #more than one source coordinate
            for i in range(0, len(unique_verts)-1):
                dist = (unique_verts[i][0] - unique_verts[i+1][0])**2 + (unique_verts[i][1] - unique_verts[i+1][1])**2
                if dist > max_dist:
                    max_x = max(max_x, unique_verts[i+1][0])
                    max_y = max(max_y, unique_verts[i+1][1])
                    min_x = min(min_x, unique_verts[i+1][0])
                    min_y = min(min_y, unique_verts[i+1][1])
                    max_dist = m.sqrt(dist)
                    xmax1 = unique_verts[i][0]
                    ymax1 = unique_verts[i][1]
                    xmax2 = unique_verts[i+1][0]
                    ymax2 = unique_verts[i+1][1]
    
            #        for i in range(0, len(vertx_a)-1):
            #            for j in range(0, len(verty_a)-1):
            #                dist = (vertx_a[i] - vertx_a[i+1])**2 + (verty_a[j] - verty_a[j+1])**2
            #                if dist > max_dist:
            #                    max_x = max(max_x,vertx_a[i+1])
            #                    max_y = max(max_y,verty_a[i+1])
            #                    min_x = min(min_x,vertx_a[i+1])
            #                    min_y = min(min_y,verty_a[i+1])
            #                    max_dist = math.sqrt(dist)
            #                    xmax1 = vertx_a[i]
            #                    ymax1 = verty_a[i]
            #                    xmax2 = vertx_a[i+1]
            #                    ymax2 = verty_a[i+1]
    
            # Calculate the center of the facility in utm coordinates
            cenx = (xmax1 + xmax2) / 2
            ceny = (ymax1 + ymax2) / 2
    
            # Compute the lat/lon of the center
            sceny = pd.Series([ceny])
            scenx = pd.Series([cenx])
            sutmz = pd.Series([utmz])
            acenlat, acenlon = UTM.utm2ll(sceny, scenx, sutmz)
    
            cenlon = acenlon[0]
            cenlat = acenlat[0]
    
        else: #single source coordinate
    
            # Calculate the center of the facility in utm coordinates
            cenx = max_x
            ceny = max_y
    
            # Compute the lat/lon of the center
            sceny = pd.Series([ceny])
            scenx = pd.Series([cenx])
            sutmz = pd.Series([utmz])
            acenlat, acenlon = UTM.utm2ll(sceny, scenx, sutmz)
    
            cenlon = acenlon[0]
            cenlat = acenlat[0]
    
        return cenx, ceny, cenlon, cenlat, max_dist, vertx_a, verty_a
