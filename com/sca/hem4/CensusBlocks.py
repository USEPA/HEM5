import math

from com.sca.hem4.support.UTM import *
from com.sca.hem4.model.Model import *
from com.sca.hem4.log.Logger import Logger
import sys
import polars as pl

rec_id = 'rec_id';
fips = 'fips';
population = 'population';
moved = 'moved';
urban_pop = 'urban_pop';
rec_type = 'rec_type';
distance = 'distance';
angle = 'angle';


#%%
def haversineDistance(blkcoors, faclon, faclat):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    
    blkcoors - numpy array of census block coordinates (lon, lat)
    faclon - longitude of facility center
    faclat - latitude of facility center
    """
    
    # convert decimal degrees to radians
    blkcoors_rad = np.deg2rad(blkcoors)
    faclon_rad = np.deg2rad(faclon)
    faclat_rad = np.deg2rad(faclat)
#    lon1, lat1, lon2, lat2 = map(np.deg2rad, [lon1, lat1, lon2, lat2])
    
    # haversine formula 
    dlon = blkcoors_rad[:,0] - faclon_rad 
    dlat = blkcoors_rad[:,1] - faclat_rad 
    a = np.sin(dlat/2)**2 + np.cos(blkcoors_rad[:,1]) * np.cos(faclat_rad) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r * 1000       

def simpleUTMDistance(blkcoors, cenx, ceny):
    """
    Calculate the "simple" distance in meters between two points
    on the earth (specified in UTM coordinates)

    blkcoors - numpy array of census block coordinates (utme, utmn)
    cenx - longitude of facility center
    ceny - latitude of facility center
    """
    return np.sqrt((cenx - blkcoors[0])**2 + (ceny - blkcoors[1])**2)

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

    # Determines whether a rececptor point (xt,yt) is within a fringe around a box
    #	with southwest corner (box_x,box_y), dimensions (Len_x,Len_y), and oriented at a given
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
			                   and fringe < math.sqrt((box_x+len_x*math.cos(A_rad) - xt)**2
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

def in_box(modelblks, sourcelocs, modeldist, maxdist, overlap_dist, model):
    
    ## This function determines if a block within modelblks is within a fringe of any source ##
    
    outerblks = modelblks.copy()
    # Initialize overlap
    outerblks['overlap'] = 'N'

    # Create empty inner blocks data frame
    # colnames = list(modelblks.columns)
    # innerblks = pd.DataFrame([], columns=colnames)
    
    inner_list = []
    
    #...... Find blocks within modeldist of point sources.........        
    ptsources = sourcelocs.query("source_type in ('P','C','H','V','N','B')")
    for index, row in ptsources.iterrows():
        src_x = row[utme]
        src_y = row[utmn]
        indist = outerblks.query('sqrt((@src_x - utme)**2 + (@src_y - utmn)**2) <= @modeldist')

        # Determine overlap
        indist['overlap'] = np.where(np.sqrt(np.double((indist[utme]-src_x)**2 +
                                       (indist[utmn]-src_y)**2)) <= overlap_dist, "Y", "N")
              
        if len(indist) > 0:
            # Export indist DF to a list of dicts, append to inner_list, and shrink outerblks
            inner_list.extend(indist.to_dict('records'))
            # innerblks = innerblks.append(indist).reset_index(drop=True)
            # innerblks = innerblks[~innerblks['blockid'].duplicated()]
            outerblks = outerblks[~outerblks['blockid'].isin(indist['blockid'])].copy()


    #....... Find blocks within modeldist of area sources ..........
    if not outerblks.empty:
                
        areasources = sourcelocs.query("source_type in ('A')")
        for index, row in areasources.iterrows():
            box_x = row[utme]
            box_y = row[utmn]
            len_x = row["lengthx"]
            len_y = row["lengthy"]
            angle_val = row["angle"]
            fringe = modeldist
            outerblks["inbox"], outerblks['overlap'] = zip(*outerblks.apply(lambda row1: rotatedbox(row1[utme],
                     row1[utmn], box_x, box_y, len_x, len_y, angle_val, fringe, overlap_dist), axis=1))
            indist = outerblks.query('inbox == True')
            if len(indist) > 0:
                # Export indist DF to a list of dicts, append to inner_list, and shrink outerblks
                inner_list.extend(indist.to_dict('records'))
                # innerblks = innerblks.append(indist).reset_index(drop=True)
                # innerblks = innerblks[~innerblks['blockid'].duplicated()]
                outerblks = outerblks[~outerblks['blockid'].isin(indist['blockid'])]
            
            if outerblks.empty:
                # Break for loop if no more outer blocks
                break
                  

    #....... If there are polygon sources, find blocks within modeldist of any polygon side ..........   
    if not outerblks.empty:
        polyvertices = sourcelocs.query("source_type in ('I')")
        if len(polyvertices) > 1:
                
            # If this polygon is a census tract (e.g. NATA application), then any outer receptor within tract will be
            # considered an inner receptor. Do not perform this check for Alternate Receptors.
            if not model.altRec_optns["altrec"]:
                outerblks.loc[:, "tract"] = outerblks['blockid'].str[1:11]
                polyvertices.loc[:, "tract"] = polyvertices[fac_id].str[0:10]
                intract = pd.merge(outerblks, polyvertices, how='inner', on='tract')
                if len(intract) > 0:
                    inner_list.extend(intract.to_dict('records'))
                    # innerblks = innerblks.append(intract).reset_index(drop=True)
                    # innerblks = innerblks[~innerblks['blockid'].duplicated()]
                    outerblks = outerblks[~outerblks['blockid'].isin(intract['blockid'])]
            
            # Are any blocks within the modeldist of any polygon side?
            # Process each source_id
            if not outerblks.empty:
                for grp,df in polyvertices.groupby(source_id):
                    # loop over each row of the source_id specific dataframe (df)
                    for i in range(0, df.shape[0]-1):
                        v1 = np.array([df.iloc[i][utme], df.iloc[i][utmn]])
                        v2 = np.array([df.iloc[i+1][utme], df.iloc[i+1][utmn]])
                        outerblks["nearpoly"] = (outerblks.apply(lambda row: polygonbox(v1, v2, 
                             np.array([row[utme],row[utmn]]), modeldist), axis=1))
                        polyblks = outerblks.query('nearpoly == True')
                        if len(polyblks) > 0:
                            inner_list.extend(polyblks.to_dict('records'))
                            # innerblks = innerblks.append(polyblks).reset_index(drop=True)
                            # innerblks = innerblks[~innerblks['blockid'].duplicated()]
                            outerblks = outerblks[~outerblks['blockid'].isin(polyblks['blockid'])]
                    if outerblks.empty:
                        # Break for loop if no more outer blocks
                        break
                    
    # Create innerblks DF from inner_list and remove duplicate block ids
    innerblks = pd.DataFrame.from_records(inner_list)
    innerblks = innerblks[~innerblks['blockid'].duplicated()]
        
    return innerblks, outerblks


#%%
def in_box_NonCensus(modelblks, sourcelocs, modeldist, maxdist, overlap_dist, model):

    ## This function determines if a block within modelblks is within a fringe of any source ##
    
    outerblks = modelblks.copy()
    # Initialize overlap
    outerblks['overlap'] = 'N'

    # Create empty inner blocks data frame
    # colnames = list(modelblks.columns)
    # innerblks = pd.DataFrame([], columns=colnames)
    
    inner_list = []
    
    #...... Find blocks within modeldist of point sources.........       
    ptsources = sourcelocs.query("source_type in ('P','C','H','V','N','B')")
    for index, row in ptsources.iterrows():
        src_x = row[utme]
        src_y = row[utmn]
        indist = outerblks.query('sqrt((@src_x - utme)**2 + (@src_y - utmn)**2) <= @modeldist')

        # Determine overlap
        indist['overlap'] = np.where(np.sqrt(np.double((indist[utme]-src_x)**2 +
                                       (indist[utmn]-src_y)**2)) <= overlap_dist, "Y", "N")
      
        if len(indist) > 0:
            # Export indist DF to a list of dicts, append to inner_list, and shrink outerblks
            inner_list.extend(indist.to_dict('records'))
            # innerblks = innerblks.append(indist).reset_index(drop=True)
            # innerblks = innerblks[~innerblks[rec_id].duplicated()]
            outerblks = outerblks[~outerblks[rec_id].isin(indist[rec_id])].copy()

    #....... Find blocks within modeldist of area sources ..........
    if not outerblks.empty:
                
        areasources = sourcelocs.query("source_type in ('A')")
        for index, row in areasources.iterrows():
            box_x = row[utme]
            box_y = row[utmn]
            len_x = row["lengthx"]
            len_y = row["lengthy"]
            angle_val = row["angle"]
            fringe = modeldist
            outerblks["inbox"], outerblks['overlap'] = zip(*outerblks.apply(lambda row1: rotatedbox(row1[utme],
                     row1[utmn], box_x, box_y, len_x, len_y, angle_val, fringe, overlap_dist), axis=1))
            indist = outerblks.query('inbox == True')
            if len(indist) > 0:
                # Export indist DF to a list of dicts, append to inner_list, and shrink outerblks
                inner_list.extend(indist.to_dict('records'))
                # innerblks = innerblks.append(indist).reset_index(drop=True)
                # innerblks = innerblks[~innerblks[rec_id].duplicated()]
                outerblks = outerblks[~outerblks[rec_id].isin(indist[rec_id])]
            
            if outerblks.empty:
                # Break for loop if no more outer blocks
                break
                  

    #....... If there are polygon sources, find blocks within modeldist of any polygon side ..........
    
    if not outerblks.empty:
        polyvertices = sourcelocs.query("source_type in ('I')")
        if len(polyvertices) > 1:
                            
            # Are any blocks within the modeldist of any polygon side?
            # Process each source_id
            if not outerblks.empty:
                for grp,df in polyvertices.groupby(source_id):
                    # loop over each row of the source_id specific dataframe (df)
                    for i in range(0, df.shape[0]-1):
                        v1 = np.array([df.iloc[i][utme], df.iloc[i][utmn]])
                        v2 = np.array([df.iloc[i+1][utme], df.iloc[i+1][utmn]])
                        outerblks["nearpoly"] = (outerblks.apply(lambda row: polygonbox(v1, v2, 
                             np.array([row[utme],row[utmn]]), modeldist), axis=1))
                        polyblks = outerblks.query('nearpoly == True')
                        if len(polyblks) > 0:
                            inner_list.extend(polyblks.to_dict('records'))
                            # innerblks = innerblks.append(polyblks).reset_index(drop=True)
                            # innerblks = innerblks[~innerblks[rec_id].duplicated()]
                            outerblks = outerblks[~outerblks[rec_id].isin(polyblks[rec_id])]
                    if outerblks.empty:
                        # Break for loop if no more outer blocks
                        break

    # Create innerblks DF from inner_list and remove duplicate block ids
    innerblks = pd.DataFrame.from_records(inner_list)
    innerblks = innerblks[~innerblks['blockid'].duplicated()]
        
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
def getblocks(cenx, ceny, cenlon, cenlat, utmzone, hemi, maxdist, modeldist, sourcelocs, overlap_dist, model):
        
    # Convert max outer ring distance from meters to degrees latitude
    # Note: if user has not selected urban/rural, then defaulting happens and that requires
    #       at least 20km for the max modeling distance. If user supplied max modeling distance
    #       is less than 20km, then compute maxdist_deg using 20km. Blocks are subset to the real
    #       max distance later.
    if model.facops.iloc[0]['rural_urban'] == '' and model.facops.iloc[0]['max_dist'] < 20000:
        maxdist_deg = 20000*39.36/36/2000/60
    else:
        maxdist_deg = maxdist*39.36/36/2000/60

    # Subset the national census blocks to blocks within one lat/lon of the facility center.
    # This creates a smaller dataframe that is more efficient.
    censusblks = model.census.dataframe.filter(
        (pl.col('lat') <= cenlat+1) & (pl.col('lat') >= cenlat-1) 
        & (pl.col('lon') <= cenlon+1) & (pl.col('lon') >= cenlon-1)).collect().to_pandas()

    if len(censusblks) == 0:
        Logger.logMessage("There are no discrete receptors within the max distance of this facility. " +
                          "Aborting processing of this facility.")
        raise ValueError("No discrete receptors selected within max distance")

    # Compute a distance (in meters) between each block and the facility center
    blkcoors = np.array(tuple(zip(censusblks.lon, censusblks.lat)))
    censusblks[distance] = haversineDistance(blkcoors, cenlon, cenlat)
    
    # # Using the national census DF, compute the distance from the facility center to each block
    # censusblks = model.census.dataframe.copy()
    # blkcoors = np.array(tuple(zip(censusblks.lon, censusblks.lat)))
    # censusblks[distance] = haversineDistance(blkcoors, cenlon, cenlat)

    # If the user has not selected Urban or Rural dispersion, then compute default
    # by taking all blocks within 3km of facility and compute the population density.
    # If > 750 people/square km, then urban. Compute urban population by summing all
    # block population within 20km.
    if model.facops.iloc[0]['rural_urban'] == '':
        pop3km_sum = censusblks[censusblks['distance'] <= 3000]['population'].sum()
        if pop3km_sum/28.27433388 > 750:
            pop20km_sum = censusblks[censusblks['distance'] <= 20000]['population'].sum()
            model.facops['rural_urban'] = 'U'
            model.facops['urban_pop'] = pop20km_sum
        else:
            model.facops['rural_urban'] = 'R'
            model.facops['urban_pop'] = 0

    #subset the censusblks dataframe to blocks that are within the max distance of the facility 
    modelblks = censusblks.query('distance <= @maxdist').copy()
    
    # Check again. If no blocks within max distance, then this facility cannot be modeled; skip it.
    if len(modelblks) == 0:
        Logger.logMessage("There are no discrete receptors within the max distance of this facility. " +
                          "Aborting processing of this facility.")
        raise ValueError("No discrete receptors selected within max distance")
        
    # Confirm the dataframe does not contain duplicates
    modelblksduplicates = modelblks[modelblks.duplicated(['lat', 'lon'])]
    if len(modelblksduplicates) > 0:
        emessage = "Error! Census blocks contain duplicate lat/long values."
        Logger.logMessage(emessage)
        raise Exception(emessage)
        
    modelblksduplicates = modelblks[modelblks.duplicated(['blockid'])]
    if len(modelblksduplicates) > 0:
        emessage = "Error! Census blocks contain duplicate block IDs."
        Logger.logMessage(emessage)
        raise Exception(emessage)

    # Add overlap column and default to N
    modelblks[overlap] = 'N'

    #compute UTMs from lat/lon using the common zone       
    modelblks[[utmn, utme]] = modelblks.apply(lambda row: UTM.ll2utm_alt(row[lat],row[lon],utmzone,hemi), 
                                               result_type="expand", axis=1)

    #set utmz as the common zone
    modelblks[utmz] = utmzone

    # Compute the bearing (angle) from the facility center to each modeling block
    modelblks[angle] = modelblks.apply(lambda row: bearing(row[utme],row[utmn],cenx,ceny), axis=1)
      
    # #coerce hill and elevation into floats
    # modelblks[hill] = pd.to_numeric(modelblks[hill], errors='coerce').fillna(0)
    # modelblks[elev] = pd.to_numeric(modelblks[elev], errors='coerce').fillna(0)
    
    
    # Split modelblks into inner and outer block receptors
    innerblks, outerblks = in_box(modelblks, sourcelocs, modeldist, maxdist, overlap_dist, model)
        
    # For inner blocks, convert utme, utmn, utmz, and population to appropriate numeric types
    innerblks[utme] = innerblks[utme].astype(np.float64)
    innerblks[utmn] = innerblks[utmn].astype(np.float64)
    innerblks[utmz] = innerblks[utmz].astype(int)
    innerblks[population] = pd.to_numeric(innerblks[population], errors='coerce').astype(int)
    innerblks[rec_type] = 'C'

    if not outerblks.empty:
        # For outer blocks, convert utme, utmn, utmz, and population to appropriate numeric types
        outerblks[utme] = outerblks[utme].astype(np.float64)
        outerblks[utmn] = outerblks[utmn].astype(np.float64)
        outerblks[utmz] = outerblks[utmz].astype(int)
        outerblks[population] = pd.to_numeric(outerblks[population], errors='coerce').astype(int)
        outerblks[rec_type] = 'C'
    
    return innerblks, outerblks


#%%
# Determine inner and outer receptors from the set of alternate receptors.
def getBlocksFromAltRecs(facid, cenx, ceny, cenlon, cenlat, utmZone, hemi, maxdist, modeldist
                         , sourcelocs, overlap_dist, model):
    
    # convert max outer ring distance from meters to degrees latitude
    maxdist_deg = maxdist*39.36/36/2000/60
    
    altrecs = model.altreceptr.dataframe.copy()

    # If any population values are missing, we cannot create an Incidence report
    model.altRec_optns['altrec_nopop'] = altrecs.isnull().any()[population]
    altrecs[population] = pd.to_numeric(altrecs[population], errors='coerce').fillna(0)

    # If any elevation or hill height values are missing, we must run in FLAT mode.
    model.altRec_optns['altrec_flat'] = altrecs.isnull().any()[elev] or altrecs.isnull().any()[hill]
    altrecs[elev] = pd.to_numeric(altrecs[elev], errors='coerce').fillna(0)
    altrecs[hill] = pd.to_numeric(altrecs[hill], errors='coerce').fillna(0)

    # Compute distance from the center of the facility to each alternate receptor
    reccoors = np.array(tuple(zip(altrecs.lon, altrecs.lat)))
    altrecs[distance] = haversineDistance(reccoors, cenlon, cenlat)

    #subset the altrecs dataframe to blocks that are within the max distance of the facility
    modelblks = altrecs.query('distance <= @maxdist')

    # If no blocks within max distance, then this facility cannot be modeled; skip it.
    if modelblks.empty == True:
        Logger.logMessage("There are no discrete receptors within the max distance of this facility. " +
                          "Aborting processing of this facility.")
        raise RuntimeError("No discrete receptors")

    # Which location type is being used? If lat/lon, convert to UTM. Otherwise, just copy over
    # the relevant values.
    ltype = modelblks.iloc[0]['location_type']
    if ltype == 'L':
        modelblks[[utmn, utme]] = modelblks.apply(lambda row: UTM.ll2utm_alt(row[lat],row[lon],utmZone,hemi), 
                                result_type="expand", axis=1)
    else:
        modelblks[[utmn, utme]] = modelblks.apply(lambda row: self.copyUTMColumns(row[lat],row[lon]), 
                                result_type="expand", axis=1)

    # Set utmzone as the common zone
    modelblks[utmz] = utmZone

    #coerce hill and elevation into floats
    modelblks[hill] = pd.to_numeric(modelblks[hill], errors='coerce').fillna(0)
    modelblks[elev] = pd.to_numeric(modelblks[elev], errors='coerce').fillna(0)

    # Compute bearing (angle) from the center of the facility to each receptor
    modelblks['angle'] = modelblks.apply(lambda row: bearing(row[utme],row[utmn],cenx,ceny), axis=1)

    # No urban pop value for alternate receptors
    modelblks['urban_pop'] = 0
            
    # Split modelblks into inner and outer block receptors
    innerblks, outerblks = in_box_NonCensus(modelblks, sourcelocs, modeldist, maxdist, overlap_dist, model)

#        Logger.log("OUTERBLOCKS", outerblks, False)

    # convert utme, utmn, utmz, and population to appropriate numeric types
    innerblks[utme] = innerblks[utme].astype(np.float64)
    innerblks[utmn] = innerblks[utmn].astype(np.float64)
    innerblks[utmz] = innerblks[utmz].astype(int)
    innerblks[population] = pd.to_numeric(innerblks[population], errors='coerce').astype(int)
    
    if not outerblks.empty:
        outerblks[utme] = outerblks[utme].astype(np.float64)
        outerblks[utmn] = outerblks[utmn].astype(np.float64)
        outerblks[utmz] = outerblks[utmz].astype(int)
        outerblks[population] = pd.to_numeric(outerblks[population], errors='coerce').astype(int)

    return innerblks, outerblks





