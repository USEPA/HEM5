from upload.InputFile import InputFile

class FacilityList(InputFile):
    
    def __init__(self, path):
        InputFile.__init__(self, path)
    
    def createDataframe(self):
        
        # FACILITIES LIST excel to dataframe
        # HEADER----------------------
        # FacilityID|met_station|rural_urban|max_dist|model_dist|radials|circles|overlap_dist|acute|hours|elev|
        # multiplier|ring1|dep|depl|phase|pdep|pdepl|vdep|vdepl|All_rcpts|user_rcpt|bldg_dw|urban_pop|fastall
        faclist_df = self.readFromPath(
            ("fac_id","met_station","rural_urban","max_dist","model_dist","radial","circles","overlap_dist", "acute",
             "hours","elev","multiplier","ring1","dep","depl","phase","pdep","pdepl","vdep","vdepl","all_rcpts",
             "user_rcpt","bldg_dw","urban_pop","fastall"),
            {0:str,1:str,2:str,8:str,10:str,13:str,14:str,15:str,16:str,17:str,18:str,19:str,20:str,21:str,22:str,24:str})

        # TODO why manually convert fac_list to numeric? converters?
        faclist_df["model_dist"] = self.to_numeric(faclist_df["model_dist"])
        faclist_df["radial"] = self.to_numeric(faclist_df["radial"])
        faclist_df["circles"] = self.to_numeric(faclist_df["circles"])
        faclist_df["overlap_dist"] = self.to_numeric(faclist_df["overlap_dist"])
        faclist_df["hours"] = self.to_numeric(faclist_df["hours"])
        faclist_df["multiplier"] = self.to_numeric(faclist_df["multiplier"])
        faclist_df["ring1"] = self.to_numeric(faclist_df["ring1"])
        faclist_df["urban_pop"] = self.to_numeric(faclist_df["urban_pop"])
        faclist_df["max_dist"] = self.to_numeric(faclist_df["max_dist"])

        facilityCount = faclist_df['fac_id'].count()
        facilities = "facility" if facilityCount == 1 else "facilities"
        self.log.append("Uploaded facilities options list file for " + str(facilityCount) + " " + facilities + "\n")
        self.dataframe = faclist_df