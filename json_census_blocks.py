from FacilityPrep import *
from support.UTM import *
from model.Model import *

rec_no = 'rec_no';
fips = 'fips';
idmarplot = 'idmarplot';
population = 'population';
moved = 'moved';
urban_pop = 'urban_pop';

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

def rotatedbox(xt, yt, box_x, box_y, len_x, len_y, angle, fringe, overlap_dist):

    # Determines whether a rececptor point (xt,yt) is within a fringe of width F around a box
    #	with origin (Box_x,Box_y), dimensions (Len_x,Len_y), and oriented at an given
    #   "Angle", measured clockwise from North.
    # Also determine if this box overlaps the point.

    inbox = False
    overlap = "N"
        
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

    # Check for overlap
    if  (xt < box_x + math.tan(A_rad)*(yt-box_y) + (len_x+overlap_dist)/math.cos(A_rad)
	                        and xt > box_x + math.tan(A_rad)*(yt-box_y) - overlap_dist/math.cos(A_rad)
	                        and yt < box_y - math.tan(A_rad)*(xt-box_x) + (len_y+overlap_dist)/math.cos(A_rad)
	                        and yt > box_y - math.tan(A_rad)*(xt-box_x) - overlap_dist/math.cos(A_rad)):         
         if ((xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and overlap_dist < math.sqrt((box_x - xt)**2 + (box_y - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt < box_y - math.tan(A_rad)*(xt-box_x)
			                   and overlap_dist < math.sqrt((box_x+len_x*math.cos(A_rad) - xt)*2
				                + (box_y-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt > box_x + math.tan(A_rad)*(yt-box_y) + len_x/math.cos(A_rad)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and overlap_dist < math.sqrt((box_x+len_x*math.cos(A_rad)+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad)-len_x*math.sin(A_rad) - yt)**2))
		                   or (xt < box_x + math.tan(A_rad)*(yt-box_y)
			                   and yt > box_y - math.tan(A_rad)*(xt-box_x) + len_y/math.cos(A_rad)
			                   and overlap_dist < math.sqrt((box_x+len_y*math.sin(A_rad) - xt)**2
				                + (box_y+len_y*math.cos(A_rad) - yt)**2))):
                   overlap = "N"
         else:
               overlap = "Y"

    return inbox, overlap

#%%    

def in_box(modelblks, sourcelocs, modeldist, maxdist, overlap_dist):

    ## This function determines if a block within modelblks is within a fringe of any source ##
    
    outerblks = modelblks.copy()
    innerblks = pd.DataFrame([])
    
    #...... Find blocks within modeldist of point sources.........
    
    ptsources = sourcelocs.query("source_type in ('P','C','H','V','N','B')")
    for index, row in ptsources.iterrows():
        src_x = row[utme]
        src_y = row[utmn]
        indist = outerblks.query('sqrt((@src_x - utme)**2 + (@src_y - utmn)**2) <= @modeldist')
        
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks[idmarplot].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks[idmarplot].isin(innerblks[idmarplot])]

            #Do any of these inner or outer blocks overlap this source?
            innerblks['overlap'] = np.where(np.sqrt((innerblks[utme]-src_x)**2 + (innerblks[utmn]-src_y)**2) <= overlap_dist, "Y", "N")
            outerblks['overlap'] = np.where(np.sqrt((outerblks[utme]-src_x)**2 + (outerblks[utmn]-src_y)**2) <= overlap_dist, "Y", "N")
    
    print("first innerblks size = ", innerblks.shape, " first outerblks size = ", outerblks.shape)

    #....... Find blocks within modeldist of area sources with angle 0..........
    
    area0sources = sourcelocs.query("source_type in ('A') and angle == 0")
    for index, row in area0sources.iterrows():
        sw_x = row[utme] - modeldist
        sw_y = row[utmn] - modeldist
        ne_x = row[utme] + row["lengthx"] + modeldist
        ne_y = row[utmn] + row["lengthy"] + modeldist
        indist = outerblks.query('utme >= @sw_x and utme <= @ne_x and utmn >= @sw_y and utmn <= @ne_y')
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks[idmarplot].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks[idmarplot].isin(innerblks[idmarplot])]

            #Do any of these inner or outer blocks overlap this source?
            sw_x = row[utme] - overlap_dist
            sw_y = row[utmn] - overlap_dist
            ne_x = row[utme] + row["lengthx"] + overlap_dist
            ne_y = row[utmn] + row["lengthy"] + overlap_dist
            innerblks[overlap] = np.where((innerblks[utme] >= sw_x) & (innerblks[utme] <= ne_x) & (innerblks[utmn] >= sw_y) & (innerblks[utmn] <= ne_y), "Y", "N")
            outerblks[overlap] = np.where((outerblks[utme] >= sw_x) & (outerblks[utme] <= ne_x) & (outerblks[utmn] >= sw_y) & (outerblks[utmn] <= ne_y), "Y", "N")
            
    print("second innerblks size = ", innerblks.shape, " second outerblks size = ", outerblks.shape)

    #....... Find blocks within modeldist of area sources with non-zero angle..........

    areasources = sourcelocs.query("source_type in ('A') and angle > 0")
    for index, row in areasources.iterrows():
        box_x = row[utme]
        box_y = row[utmn]
        len_x = row["lengthx"]
        len_y = row["lengthy"]
        angle = row[angle]
        fringe = modeldist
        outerblks["inbox"], outerblks[overlap] = zip(*outerblks.apply(lambda row: rotatedbox(row[utme],
                 row[utmn], box_x, box_y, len_x, len_y, angle, fringe, overlap_dist), axis=1))
        indist = outerblks.query('inbox == True')
        if len(indist) > 0:
            innerblks = innerblks.append(indist).reset_index(drop=True)
            innerblks = innerblks[~innerblks[idmarplot].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks[idmarplot].isin(innerblks[idmarplot])]
                  
    print("third innerblks size = ", innerblks.shape, " third outerblks size = ", outerblks.shape)


    #....... If there are polygon sources, find blocks within modeldist of any polygon side ..........

    polyvertices = sourcelocs.query("source_type in ('I')")
    if len(polyvertices) > 1:
            
        # for tract polygons, any outerblks in the same tract as any polygon vertex will be counted as inner
        outerblks["tract"] = outerblks[idmarplot].str[0:10]
        polyvertices["tract"] = polyvertices[fac_id].str[1:11]
        intract = pd.merge(outerblks, polyvertices, how='inner', on='tract')
        if len(intract) > 0:
            innerblks = innerblks.append(intract).reset_index(drop=True)
            innerblks = innerblks[~innerblks[idmarplot].apply(tuple).duplicated()]
            outerblks = outerblks[~outerblks[idmarplot].isin(innerblks[idmarplot])]
        
        # for non-tract polygons, are any blocks within the modeldist of any polygon side?
        #     process each source_id
        for grp,df in polyvertices.groupby(source_id):
            # loop over each row of the source_id specific dataframe (df)
            for i in range(0, df.shape[0]-1):
                v1 = np.array([df.iloc[i][utme], df.iloc[i][utmn]])
                v2 = np.array([df.iloc[i+1][utme], df.iloc[i+1][utmn]])
                outerblks["nearpoly"] = (outerblks.apply(lambda row: polygonbox(v1, v2, 
                     np.array([row[utme],row[utmn]]), modeldist), axis=1))
                polyblks = outerblks.query('nearpoly == True')
                if len(polyblks) > 0:
                    innerblks = innerblks.append(polyblks).reset_index(drop=True)
                    innerblks = innerblks[~innerblks[idmarplot].apply(tuple).duplicated()]
                    outerblks = outerblks[~outerblks[idmarplot].isin(innerblks[idmarplot])]

    print("fourth innerblks size = ", innerblks.shape, " fourth outerblks size = ", outerblks.shape)
        
    return innerblks, outerblks    
    
    

    
    
    

#%%
def read_json_file(path_to_file, dtype_dict):
    with open(path_to_file) as p:
        raw = pd.read_json(p, orient="columns", dtype=eval(dtype_dict))
        raw.columns = [x.lower() for x in raw.columns]
        return raw

    
#%%
def cntyinzone(lat_min, lon_min, lat_max, lon_max, cenlat, cenlon, maxdist_deg):
    inzone = False
    if ((cenlat - lat_max <= maxdist_deg and cenlat >= lat_min) or (lat_min - cenlat <= maxdist_deg and cenlat <= lat_max)) and ((cenlon - lon_max <= maxdist_deg/math.cos(math.radians(cenlat)) and cenlon >= lon_min) or (lon_min - cenlon <= maxdist_deg/math.cos(math.radians(cenlat)) and cenlon <= lon_max)):
            inzone = True
    return inzone

#%%
def getblocks(cenx, ceny, cenlon, cenlat, utmzone, maxdist, modeldist, sourcelocs, overlap_dist):
    

    # convert max outer ring distance from meters to degrees latitude
    maxdist_deg = maxdist*39.36/36/2000/60

    ##%% census key look-up

    #load census key into data frame
    dtype_dict = '{"ELEV_MAX":float,"FILE_NAME":object,"FIPS":object,"LAT_MAX":float,"LAT_MIN":float,"LON_MAX":float,"LON_MIN":float,"MIN_REC":int,"NO":int,"YEAR":int}'
    census_key = read_json_file("census/census_key.json", dtype_dict)
    census_key.columns = [x.lower() for x in census_key.columns]


    #convert each row from json string to columns and sort by index
    #census_key = pd.read_json( ck_data['data'].to_json(), orient='index' ).sort_index(axis=0)
#    census_key = pd.DataFrame.from_dict(ck_data['data'], orient='columns')
#    census_key[['LAT_MAX', 'LON_MAX', 'LAT_MIN', 'LON_MIN']] = census_key[['LAT_MAX', 'LON_MAX', 'LAT_MIN', 'LON_MIN']].apply(pd.to_numeric)
#    #find counties in the "inzone"
#
#    census_key.columns = ['cyear', 'elevmax','file_name', 'fips', 'lat_max','lat_min','lon_max','lon_min','minrec', 'num']


    #create selection for "inzone" and find where true in census_key dataframe

    census_key["inzone"] = census_key.apply(lambda row: cntyinzone(row["lat_min"], row["lon_min"], row["lat_max"], row["lon_max"], cenlat, cenlon, maxdist_deg), axis=1)
    cntyinzone_df = census_key.query('inzone == True')
    
    censusfile2use = {}    
    
    # Find all blocks within the intersecting counties that intersect the modeling zone. Store them in modelblks.
    frames = []

    for index, row in cntyinzone_df.iterrows():
        #print("starting loop")
        
        state = "census/" + row['file_name'] + ".json"
        # Query state census file
        if state in censusfile2use:
            censusfile2use[state].append(str(row[fips]))
        else:
            censusfile2use[state] = [str(row[fips])]
            #print("done!")
       
    for state, FIPS in censusfile2use.items():
        locations = FIPS
        dtype_dict = '{"REC_NO":int, "FIPS":object, "IDMARPLOT":object, "POPULATION":int, "LAT":float, "LON":float, "ELEV":float, "HILL":float, "MOVED":object, "URBAN_POP":int}'
        state_pd = read_json_file(state, dtype_dict)
        state_pd.columns = [x.lower() for x in state_pd.columns]
#        state_pd = pd.DataFrame.from_dict(state_data['data'], orient='columns')
        
        
        check = state_pd[state_pd[fips].isin(locations)]
        frames.append(check)

    #combine dataframes to modelblks
    censusblks = pd.concat(frames)

    #lowercase column names
    #censusblks.columns = map(str.lower, censusblks.columns)
    #print(censusblks)

    #convert to utm if necessary
    censusblks[utms] = censusblks.apply(lambda row: UTM.ll2utm_alt(row[lat], row[lon], utmzone), axis=1)

    #split utms column into utmn, utme, utmz
    censusblks[[utmn, utme, utmz]] = pd.DataFrame(censusblks.utms.values.tolist(), index= censusblks.index)
    #clean up censusblks df
    del censusblks[utms]
    
    #coerce hill and elevation into floats
    censusblks[hill] = pd.to_numeric(censusblks[hill], errors='coerce').fillna(0)
    censusblks[elev] = pd.to_numeric(censusblks[elev], errors='coerce').fillna(0)

    #compute distance and bearing (angle) from the center of the facility
    censusblks['distance'] = np.sqrt((cenx - censusblks.utme)**2 + (ceny - censusblks.utmn)**2)
    censusblks['angle'] = censusblks.apply(lambda row: bearing(row[utme],row[utmn],cenx,ceny), axis=1)

    #subset the censusblks dataframe to blocks that are within the modeling distance of the facility 
    modelblks = censusblks.query('distance <= @maxdist')

    # Split modelblks into inner and outer block receptors
    innerblks, outerblks = in_box(modelblks, sourcelocs, modeldist, maxdist, overlap_dist)
        
    
    # convert utme, utmn, utmz, and population to integers
    innerblks[utme] = innerblks[utme].astype(int)
    innerblks[utmn] = innerblks[utmn].astype(int)
    innerblks[utmz] = innerblks[utmz].astype(int)
    innerblks[population] = pd.to_numeric(innerblks[population], errors='coerce').astype(int)
    outerblks[utme] = outerblks[utme].astype(int)
    outerblks[utmn] = outerblks[utmn].astype(int)
    outerblks[utmz] = outerblks[utmz].astype(int)
    outerblks[population] = pd.to_numeric(outerblks[population], errors='coerce').astype(int)
    
    return innerblks, outerblks







