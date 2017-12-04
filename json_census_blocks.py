
# coding: utf-8

# In[ ]:




# In[58]:

import math  
import pandas as pd
import ll2utm
import numpy as np
import time
import sys
import json


def ll2utm(lat,lon,zone):
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
            dtr  = ( math.pi / 180.0 )      # Conversion from degrees to radians
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


#%% compute a bearing from the center of a facility to a census receptor

def bearing(utme, utmn, cenx, ceny):
    if utmn > ceny:
        if utme > cenx:
            angle = math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
        else:
            angle = 360 + math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
    elif utmn < ceny:
        angle = 180 + math.degrees(math.atan((utme-cenx)/(utmn-ceny)))
    else:
        if utme >= cenx:
            angle = 90
        else:
            angle = 270
    
    return angle        


#%%

def polygonbox(vertex1, vertex2, blkcoor, modeldist):
    nearpoly = False
    
    v1_to_blk = ((vertex1[0]-blkcoor[0])**2) + ((vertex1[1]-blkcoor[1])**2)
    v2_to_blk = ((vertex2[0]-blkcoor[0])**2) + ((vertex2[1]-blkcoor[1])**2)
    v1_to_v2 = ((vertex1[0]-vertex2[0])**2) + ((vertex1[1]-vertex2[1])**2)
    if v2_to_blk <= modeldist**2:
        nearpoly = True
    elif v1_to_blk + v1_to_v2 > v2_to_blk and v2_to_blk + v1_to_v2 > v1_to_blk:
        d = np.linalg.norm(np.cross(vertex2-vertex1,vertex1-blkcoor))/np.linalg.norm(vertex2-vertex1)
        if d <= modeldist:
            nearpoly = True
    return nearpoly


#%%

def rotatedbox(xt, yt, box_x, box_y, len_x, len_y, angle, fringe):

    # Determines whether a point (xt,yt) is within a fringe of width F around a box
    #	with origin (Box_x,Box_y), dimensions (Len_x,Len_y), and oriented at an given
    #   "Angle", measured clockwise from North.

    inbox = False
        
    A_rad = math.radians(angle)
    D_e = (yt-box_y)*math.cos(A_rad) + (xt-box_x)*math.sin(A_rad) - len_y
    D_w = (box_y-yt)*math.cos(A_rad) + (box_x-xt)*math.sin(A_rad)
    D_n = (xt-box_x)*math.cos(A_rad) + (yt-box_y)*math.sin(A_rad) - len_x
    D_s = (box_x-xt)*math.cos(A_rad) + (box_y-yt)*math.sin(A_rad)
    D_sw = math.sqrt((xt-box_x)**2 + (yt-box_y)**2)
    D_se = (math.sqrt((box_x+len_x*math.cos(A_rad) - xt)**2 
                    + (box_y-len_x*math.sin(A_rad) - yt)**2))
    D_ne = (math.sqrt((box_x+len_x*math.cos(A_rad)+len_y*math.sin(A_rad) - xt)**2
				                    + (box_y+len_y*math.cos(A_rad)-len_x*math.sin(A_rad) - yt)**2))
    D_nw = (math.sqrt((box_x+len_y*math.sin(A_rad) - xt)**2
				                    + (box_y+len_y*math.cos(A_rad) - yt)**2))
    if D_e <= 0 and D_w <= 0:
        D_test = max(D_e, D_w, D_n, D_s)
    elif D_n <= 0 and D_s <= 0:
        D_test = max(D_e, D_w, D_n, D_s)
    else:
        D_test = min(D_ne, D_nw, D_se, D_sw)
           
    # First see if the point is in the rectangle
    if  (xt < box_x + math.tan(A_rad)*(yt-box_y) + (len_x+fringe)/math.cos(A_rad)
	                        and xt > box_x + math.tan(A_rad)*(yt-box_y) - fringe/math.cos(A_rad)
	                        and yt < box_y - math.tan(A_rad)*(xt-box_x) + (len_y+fringe)/math.cos(A_rad)
	                        and yt > box_y - math.tan(A_rad)*(xt-box_x) - fringe/math.cos(A_rad)):
         
         # Now check the corners
         if ((xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and fringe < math.sqrt((box_x - xt)**2 + (box_y - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and fringe < math.sqrt((box_x+len_x*math.cos(A_rad) - xt)*2
				                + (box_y-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and fringe < math.sqrt((box_x+len_x*math.cos(A_rad)+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad)-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and fringe < math.sqrt((box_x+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad) - yt)**2))):
                   inbox = False
         else:
               inbox = True

    return inbox

#%%    

def in_box(modelblks, sourcelocs, modeldist, maxdist):

    ## This function determines if a block within modelblks is within a fringe of any source ##
    
    outerblks = modelblks.copy()
    innerblks = pd.DataFrame([])
    
    #...... Find blocks within modeldist of point sources.........
    
    ptsources = sourcelocs.query("source_type in ('P','C','H','V','N','B')")
    for index, row in ptsources.iterrows():
        src_x = row["utme"]
        src_y = row["utmn"]
        indist = outerblks.query('sqrt((@src_x - utme)**2 + (@src_y - utmn)**2) <= @modeldist')
        
        
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks['IDMARPLOT'].apply(tuple).duplicated()]
            print(innerblks)
            
            outerblks = outerblks[~outerblks['IDMARPLOT'].isin(innerblks['IDMARPLOT'])]


    
    
    print("first innerblks size = ", innerblks.shape, " first outerblks size = ", outerblks.shape)

    #....... Find blocks within modeldist of area sources with angle 0..........
    
    area0sources = sourcelocs.query("source_type in ('A') and angle == 0")
    for index, row in area0sources.iterrows():
        sw_x = row["utme"] - modeldist
        sw_y = row["utmn"] - modeldist
        ne_x = row["utme"] + row["lengthx"] + modeldist
        ne_y = row["utmn"] + row["lengthy"] + modeldist
        indist = outerblks.query('utme >= @sw_x and utme <= @ne_x and utmn >= @sw_y and utmn <= @ne_y')
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks['IDMARPLOT'].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks['IDMARPLOT'].isin(innerblks['IDMARPLOT'])]

    print("second innerblks size = ", innerblks.shape, " second outerblks size = ", outerblks.shape)

    #....... Find blocks within modeldist of area sources with non-zero angle..........

    areasources = sourcelocs.query("source_type in ('A') and angle > 0")
    for index, row in areasources.iterrows():
        box_x = row["utme"]
        box_y = row["utmn"]
        len_x = row["lengthx"]
        len_y = row["lengthy"]
        angle = row["angle"]
        fringe = modeldist
        outerblks["inbox"] = (outerblks.apply(lambda row: rotatedbox(row['utme'], 
                 row['utmn'], box_x, box_y, len_x, len_y, angle, fringe), axis=1))
        indist = outerblks.query('inbox == True')
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks['IDMARPLOT'].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks['IDMARPLOT'].isin(innerblks['IDMARPLOT'])]
                  
    print("third innerblks size = ", innerblks.shape, " third outerblks size = ", outerblks.shape)


    #....... If there are polygon sources, find blocks within modeldist of any polygon side ..........

    polyvertices = sourcelocs.query("source_type in ('I')")
    if len(polyvertices) > 1:
            
        # for tract polygons, any outerblks in the same tract as any polygon vertex will be counted as inner
        outerblks["tract"] = outerblks["IDMARPLOT"].str[0:10]
        polyvertices["tract"] = polyvertices["fac_id"].str[1:11]
        intract = pd.merge(outerblks, polyvertices, how='inner', on='tract')
        if len(intract) > 0:
            innerblks = innerblks.append(intract).reset_index(drop=True)
            innerblks = innerblks[~innerblks['IDMARPLOT'].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks['IDMARPLOT'].isin(innerblks['IDMARPLOT'])]
        
        # for non-tract polygons, are any blocks within the modeldist of any polygon side?
        #     process each source_id
        for grp,df in polyvertices.groupby("source_id"):
            # loop over each row of the source_id specific dataframe (df)
            for i in range(0, df.shape[0]-1):
                v1 = np.array([df.iloc[i]["utme"], df.iloc[i]["utmn"]])
                v2 = np.array([df.iloc[i+1]["utme"], df.iloc[i+1]["utmn"]])
                outerblks["nearpoly"] = (outerblks.apply(lambda row: polygonbox(v1, v2, 
                     np.array([row["utme"],row["utmn"]]), modeldist), axis=1))
                polyblks = outerblks.query('nearpoly == True')
                if len(polyblks) > 0:
                    innerblks = innerblks.append(polyblks).reset_index(drop=True)
                    innerblks = innerblks[~innerblks['IDMARPLOT'].apply(tuple).duplicated()]
                    outerblks = outerblks[~outerblks['IDMARPLOT'].isin(innerblks['IDMARPLOT'])]

    print("fourth innerblks size = ", innerblks.shape, " fourth outerblks size = ", outerblks.shape)
        
    return innerblks, outerblks    
    
    

    
    
    

#%%
def read_json_file(path_to_file):
    with open(path_to_file) as p:
        return json.load(p)

    
#%%
def cntyinzone(lat_min, lon_min, lat_max, lon_max, cenlat, cenlon, maxdist_deg):
    inzone = False
    if ((cenlat - lat_max <= maxdist_deg and cenlat >= lat_min)         or (lat_min - cenlat <= maxdist_deg and cenlat <= lat_max))         and ((cenlon - lon_max <= maxdist_deg/math.cos(math.radians(cenlat)) and cenlon >= lon_min)         or (lon_min - cenlon <= maxdist_deg/math.cos(math.radians(cenlat)) and cenlon <= lon_max)):
            inzone = True
    return inzone

#%%
def getblocks(cenx, ceny, cenlon, cenlat, utmzone, maxdist, modeldist, sourcelocs):
    

    # convert max outer ring distance from meters to degrees latitude
    maxdist_deg = maxdist*39.36/36/2000/60

    ##%% census key look-up

    #load in json data
    ck_data = pd.read_json("census/census_key.json")
    ck_data

    #convert each row from json string to columns and sort by index
    census_key = pd.read_json( ck_data['data'].to_json(), orient='index' ).sort_index(axis=0)

    #find counties in the "inzone"

    census_key.columns = ['cyear', 'elevmax','file_name', 'fips', 'lat_max','lat_min','lon_max','lon_min','minrec', 'num']


    #create selection for "inzone" and find where true in census_key dataframe

    census_key["inzone"] = census_key.apply(lambda row: cntyinzone(row["lat_min"], row["lon_min"], row["lat_max"], row["lon_max"], cenlat, cenlon, maxdist_deg), axis=1)
    cntyinzone_df = census_key.query('inzone == True')

    censusfile2use = {}    
    
    # Find all blocks within the intersecting counties that intersect the modeling zone. Store them in modelblks.
    frames = []

    for index, row in cntyinzone_df.iterrows():
        #print("starting loop")
        #print(row)
        state = "census/" + row['file_name'] + ".json"
        # Query state census file
        if state in censusfile2use:
            censusfile2use[state].append(str(row["fips"]))
        else:
            censusfile2use[state] = [str(row["fips"])]
            #print("done!")
       
    for state, fips in censusfile2use.items():
        #print(locations)
        locations = fips
        state_data = read_json_file(state)
        state_pd = pd.DataFrame.from_dict(state_data['data'], orient='columns')
   
        check = state_pd[state_pd['FIPS'].isin(locations)]
        frames.append(check)

    #combine dataframes to modelblks
    censusblks = pd.concat(frames)

    #lowercase column names
    #censusblks.columns = map(str.lower, censusblks.columns)
    #print(censusblks)

    #convert to utm if necessary
    censusblks["utms"] = censusblks.apply(lambda row: ll2utm(row['LAT'], row['LON'], utmzone), axis=1)

    #split utms column into utmn, utme, utmz
    censusblks[['utmn', 'utme', 'utmz']] = pd.DataFrame(censusblks.utms.values.tolist(), index= censusblks.index)
    #clean up censusblks df
    del censusblks['utms']
    
    #coerce hill and elevation into floats
    censusblks['HILL'] = pd.to_numeric(censusblks['HILL'], errors='coerce').fillna(0)
    censusblks['ELEV'] = pd.to_numeric(censusblks['ELEV'], errors='coerce').fillna(0)

    #compute distance and bearing (angle) from the center of the facility
    censusblks['DISTANCE'] = np.sqrt((cenx - censusblks.utme)**2 + (ceny - censusblks.utmn)**2)
    censusblks['ANGLE'] = censusblks.apply(lambda row: bearing(row["utme"],row["utmn"],cenx,ceny), axis=1)  

    #subset the censusblks dataframe to blocks that are within the modeling distance of the facility 
    modelblks = censusblks.query('DISTANCE <= @maxdist')
    #modelblks = censusblks.query('sqrt((@cenx-utme)**2 + (@ceny-utmn)**2) <= @maxdist')


    # Split modelblks into inner and outer data frames
    innerblks, outerblks = in_box(modelblks, sourcelocs, modeldist, maxdist)
        
    
    # convert utme and utme to integers
    innerblks["utme"] = innerblks["utme"].astype(int)
    innerblks["utmn"] = innerblks["utmn"].astype(int)
    
    return innerblks, outerblks







