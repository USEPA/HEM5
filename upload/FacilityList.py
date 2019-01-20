from math import isnan

from model.Model import *
from upload.InputFile import InputFile
from tkinter import messagebox

met_station = 'met_station';
rural_urban = 'rural_urban';
max_dist = 'max_dist';
model_dist = 'model_dist';
radial = 'radial';
circles = 'circles';
overlap_dist = 'overlap_dist';
acute = 'acute';
hours = 'hours';
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
        self.skiprows = 1
        InputFile.__init__(self, path)

    def createDataframe(self):

        self.skiprows = 1

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
            
        
        #checkif urban_rural has a u and if it does if there is a urban pop 
        #value greater than zero
        urban = faclist_df[faclist_df[rural_urban] == 'U']
        missing_pop = [] 
        for row in urban.iterrows():
            if row[urban_pop][0] >= 0 or isnan(row[urban_pop][0]):
                missing_pop.append(row[fac_id][0])
                
    
        if len(missing_pop) == 0: 

            facilityCount = faclist_df[fac_id].count()
            facilities = "facility" if facilityCount == 1 else "facilities"
            self.log.append("Uploaded facilities options list file for " + str(facilityCount) + " " + facilities + "\n")
            self.dataframe = faclist_df
            
        elif len(missing_pop) > 0:
             messagebox.showinfo("Missing Urban Population Values", "The urban" + 
                                 " urban population values for: " + 
                                 ", ".join(missing_pop))          