from model.Model import *
from upload.InputFile import InputFile

met_station = 'met_station';
rural_urban = 'rural_urban';
max_dist = 'max_dist';
model_dist = 'model_dist';
radial = 'radial';
circles = 'circles';
overlap_dist = 'overlap_dist';
acute = 'acute';
hours = 'hours';
elev = 'elev';
multiplier = 'multiplier';
ring1 = 'ring1';
dep = 'dep';
depl = 'depl';
phase = 'phase';
pdep = 'pdep';
pdepl = 'pdepl';
vdep = 'vdep';
vdepl = 'vdepl';
all_rcpts = 'all_rcpts';
user_rcpt = 'user_rcpt';
bldg_dw = 'bldg_dw';
urban_pop = 'urban_pop';
fastall = 'fastall';

class FacilityList(InputFile):
    
    def __init__(self, path):
        InputFile.__init__(self, path)
    
    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [max_dist,model_dist,radial,circles,overlap_dist,hours,multiplier,ring1,urban_pop]
        self.strColumns = [fac_id,met_station,rural_urban,acute,elev,dep,depl,phase,pdep,pdepl,
                           vdep,vdepl,all_rcpts,user_rcpt,bldg_dw,fastall]

        # FACILITIES LIST excel to dataframe
        # HEADER----------------------
        # FacilityID|met_station|rural_urban|max_dist|model_dist|radials|circles|overlap_dist|acute|hours|elev|
        # multiplier|ring1|dep|depl|phase|pdep|pdepl|vdep|vdepl|All_rcpts|user_rcpt|bldg_dw|urban_pop|fastall
        faclist_df = self.readFromPath(
            (fac_id,met_station,rural_urban,max_dist,model_dist,radial,circles,overlap_dist, acute,
             hours,elev,multiplier,ring1,dep,depl,phase,pdep,pdepl,vdep,vdepl,all_rcpts,
             user_rcpt,bldg_dw,urban_pop,fastall)
        )

        facilityCount = faclist_df[fac_id].count()
        facilities = "facility" if facilityCount == 1 else "facilities"
        self.log.append("Uploaded facilities options list file for " + str(facilityCount) + " " + facilities + "\n")
        self.dataframe = faclist_df