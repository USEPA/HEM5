import os
import numpy as np
import math
import pandas as pd

from writer.csv.CsvWriter import CsvWriter
from log import Logger

class AllOuterReceptors(CsvWriter):
    """
    Provides the annual average concentration interpolated at every census block beyond the modeling cutoff distance but
    within the modeling domain, specific to each source ID and pollutant, along with receptor information, and acute
    concentration (if modeled) and wet and dry deposition flux (if modeled).
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_all_outer_receptors.csv")

    def calculateOutputs(self):
        """
        Interpolate polar pollutant concs to outer receptors.
        """

        self.headers = ['Fips', 'Block', 'Lat', 'Lon', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m2',
                        'Elevation', 'Population', 'Overlap']
        
        #list of unique source ids/pollutants from polar concs
        uniqsrcpol = self.model.all_polar_receptors_df[["Source_id","Pollutant"]].drop_duplicates().as_matrix()
#        uniqsrcpol = [list(x) for x in set(tuple(x) for x in srcpol)]
        
        #convert outer blocks dataframe to matrix
        outerblks_m = self.model.outerblks_df.as_matrix()
        
        #convert all polar receptors dataframe to matrix
        all_polar_receptors_m = self.model.all_polar_receptors_df.as_matrix()


        dlist = []
        
        #process each outer block
        for row in outerblks_m:
                        
            d_fips = row[1]
            d_block = row[3][6:]
            d_lat = row[4]
            d_lon = row[5]
            d_elev = row[0]
            d_population = row[7]
            d_emistype = "C"
            d_aconc = 0.0
            d_overlap = row[15]

            #ring and sector of this outer block
            ring_loc = row[19]
            cs = row[17]
            
            #define the four surrounding polar sector/rings for this outer block
            s = ((row[14] * self.model.numsectors)/360.0 % self.model.numsectors) + 1
            if int(s) == self.model.numsectors:
                s1 = self.model.numsectors
                s2 = 1
            else:
                s1 = int(s)
                s2 = int(s) + 1
            r1 = int(row[19])
            if r1 == self.model.numrings:
                r1 = r1 - 1
            r2 = int(row[19]) + 1
            if r2 > self.model.numrings:
               r2 = self.model.numrings
            
            s1r1 = np.logical_and(all_polar_receptors_m[:, 6] == s1, all_polar_receptors_m[:,7] == r1 )
            s1r2 = np.logical_and(all_polar_receptors_m[:, 6] == s1, all_polar_receptors_m[:,7] == r2 )
            s2r1 = np.logical_and(all_polar_receptors_m[:, 6] == s2, all_polar_receptors_m[:,7] == r1 )
            s2r2 = np.logical_and(all_polar_receptors_m[:, 6] == s2, all_polar_receptors_m[:,7] == r2 )
            
            co1 = all_polar_receptors_m[s1r1]
            co2 = all_polar_receptors_m[s1r2]
            co3 = all_polar_receptors_m[s2r1]
            co4 = all_polar_receptors_m[s2r2]
            
            #full has polar conc records for the 4 surrounding polar receptors
            full = np.concatenate((co1, co2, co3, co4), axis=0)
            
            
            #work on one source/pollutant at a time
            for srcpolrow in uniqsrcpol:
                                
                #subset to specific source id and pollutant
                sub = full[(full[:,0] == srcpolrow[0]) & (full[:,2] == srcpolrow[1])]
                
                #polar concs of 4 surrounding polar receptors                
                conc = sub[:, 3]
                
                d_sourceid = srcpolrow[0]
                d_pollutant = srcpolrow[1]
                
                #interpolate
                if conc[0] == 0 or conc[1] == 0:
                    R_s12 = max(conc[0], conc[1])
                else:
                    Lnr_s12 = (math.log(conc[0]) * (int(ring_loc)+1-ring_loc)) + (math.log(conc[1]) * (ring_loc-int(ring_loc)))
                    R_s12 = math.exp(Lnr_s12)
            
                if conc[2] == 0 or conc[3] == 0:
                    R_s34 = max(conc[2], conc[3] )
                else:
                    Lnr_s34 = (math.log(conc[2]) * (int(ring_loc)+1-ring_loc)) + (math.log(conc[3] ) * (ring_loc-int(ring_loc)))
                    R_s34 = math.exp(Lnr_s34)
                
                d_conc = R_s12*(int(cs)+1-cs) + R_s34*(cs-int(cs))
                
                datalist = [d_fips, d_block, d_lat, d_lon, d_sourceid, d_emistype, d_pollutant, d_conc, 
                            d_aconc, d_elev, d_population, d_overlap]
                dlist.append(datalist)

        outerconc_df = pd.DataFrame(dlist, columns=self.headers)
        
        # dataframe to array
        self.data = outerconc_df.values