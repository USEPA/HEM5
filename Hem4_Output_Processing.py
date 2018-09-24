# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 12:43:52 2017

@author: dlindsey
"""
import time
import numpy as np
import pandas as pd

from log.Logger import Logger
from writer.csv.AllPolarReceptors import AllPolarReceptors
from writer.csv.AllInnerReceptors import AllInnerReceptors
from writer.csv.AllOuterReceptors import AllOuterReceptors
from writer.excel.MaximumIndividualRisks import MaximumIndividualRisks
from writer.excel.RiskBreakdown import RiskBreakdown
from writer.kml.KMLWriter import KMLWriter
import sys

class Process_outputs():
    
    def __init__(self, outdir, facid, model, prep, runstream):
        self.facid = facid
        self.haplib_m = model.haplib.dataframe.as_matrix()
        self.hapemis = runstream.hapemis
        self.outdir = outdir
        self.polar_recs = runstream.polar_df
        self.model = model
        self.runstream = runstream
        self.model.numsectors = self.polar_recs["sector"].max()
        self.model.numrings = self.polar_recs["ring"].max()
        self.model.polarrecs_df = runstream.polar_df
        self.model.innerblks_df = prep.innerblks
        self.model.outerblks_df = prep.outerblks
        self.model.runstream_hapemis = runstream.hapemis

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760
#        #first check for facilities folder, if not create as output directory
#        if not os.path.exists(self.outdir):
#            os.makedirs(self.outdir)
        


    def nodivby0(self, n, d):
        quotient = np.zeros(len(n))
        for i in np.arange(len(n)):
            if d[i] != 0:
                quotient[i] = n[i]/d[i]
            else:
                quotient[i] = 0
        return quotient
    
    
    def compute_risk_by_latlon(self, model):

        #------ first - inner receptor risk by lat/lon --------------------
        
        #sum conc to Lat, Lon, pollutant
#        inner_cols = ['Fips', 'Block', 'Lat', 'Lon', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m2',
#                        'Elevation', 'Ddp_g_m2', 'Wdp_g_m2', 'Population', 'Overlap']        
#        inner_df = pd.DataFrame(data=self.model.all_inner_receptors, columns=inner_cols)
        inner_sum = self.model.all_inner_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge ure and rfc by pollutant        
        inner_sum2 = pd.merge(inner_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if inner_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

        #merge target organ endpoint values 
        inner_sum3 = pd.merge(inner_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
                                                                      "reprod","kidney","ocular","endoc","hemato",
                                                                      "immune","skeletal","spleen","thyroid",
                                                                      "wholebod"]],on="pollutant",how="left")
       
        #calculate risk and target organ specific HIs 
        inner_sum3["risk"] = inner_sum3["Conc_ug_m3"]*inner_sum3["ure"]
        inner_sum3["hi_resp"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["resp"]/1000
        inner_sum3["hi_live"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["liver"]/1000
        inner_sum3["hi_neur"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["neuro"]/1000
        inner_sum3["hi_deve"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["dev"]/1000
        inner_sum3["hi_repr"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["reprod"]/1000
        inner_sum3["hi_kidn"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["kidney"]/1000
        inner_sum3["hi_ocul"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["ocular"]/1000
        inner_sum3["hi_endo"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["endoc"]/1000
        inner_sum3["hi_hema"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["hemato"]/1000
        inner_sum3["hi_immu"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["immune"]/1000
        inner_sum3["hi_skel"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["skeletal"]/1000
        inner_sum3["hi_sple"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["spleen"]/1000
        inner_sum3["hi_thyr"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["thyroid"]/1000
        inner_sum3["hi_whol"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["wholebod"]/1000
        
        #sum risk and HI to lat, lon and assign a receptor type
        inner_riskhi_by_latlon = inner_sum3.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        inner_riskhi_by_latlon["rectype"] = "I"


        #--------- second - outer receptor risk by lat/lon ----------------
        
        #sum conc to lat, Lon, pollutant
#        outer_cols = ['Fips', 'Block', 'Lat', 'Lon', 'Source_id', 'Emis_type', 'Pollutant', 'Conc_ug_m3', 'Acon_ug_m2',
#                        'Elevation', 'Population', 'Overlap']        
#        outer_df = pd.DataFrame(data=self.model.all_outer_receptors, columns=outer_cols)
        outer_sum = self.model.all_outer_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge ure and rfc by pollutant        
        outer_sum2 = pd.merge(outer_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if outer_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

        #merge target organ endpoint values
        outer_sum3 = pd.merge(outer_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
                                                                      "reprod","kidney","ocular","endoc","hemato",
                                                                      "immune","skeletal","spleen","thyroid",
                                                                      "wholebod"]],on="pollutant",how="left")

        #calculate risk and HI
        outer_sum3["risk"] = outer_sum3["Conc_ug_m3"]*outer_sum3["ure"]
        outer_sum3["hi_resp"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["resp"]/1000
        outer_sum3["hi_live"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["liver"]/1000
        outer_sum3["hi_neur"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["neuro"]/1000
        outer_sum3["hi_deve"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["dev"]/1000
        outer_sum3["hi_repr"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["reprod"]/1000
        outer_sum3["hi_kidn"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["kidney"]/1000
        outer_sum3["hi_ocul"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["ocular"]/1000
        outer_sum3["hi_endo"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["endoc"]/1000
        outer_sum3["hi_hema"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["hemato"]/1000
        outer_sum3["hi_immu"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["immune"]/1000
        outer_sum3["hi_skel"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["skeletal"]/1000
        outer_sum3["hi_sple"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["spleen"]/1000
        outer_sum3["hi_thyr"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["thyroid"]/1000
        outer_sum3["hi_whol"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["wholebod"]/1000
          
        #sum risk and HI to lat, lon and assign receptor type
        outer_riskhi_by_latlon = outer_sum3.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        outer_riskhi_by_latlon["rectype"] = "O"


        #---------- third - polar receptor risk by lat/lon --------------
        
        #sum conc to lat, lon, pollutant
#        polar_cols = ["Source_id", "Emis_type", "Pollutant", "Conc_ug_m3",
#                      "Distance_m", "Angle", "Sector_num", "Ring_num", "Elev_m", 
#                      "Lat", "Lon", "Overlap", "Wdp_g_m2_y", "Ddp_g_m2_y",]        
#        polar_df = pd.DataFrame(data=self.model.all_polar_receptors, columns=polar_cols)
        polar_sum = self.model.all_polar_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge ure and rfc by pollutant        
        polar_sum2 = pd.merge(polar_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if polar_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

        #merge target organ endpoint values
        polar_sum3 = pd.merge(polar_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
                                                                      "reprod","kidney","ocular","endoc","hemato",
                                                                      "immune","skeletal","spleen","thyroid",
                                                                      "wholebod"]],on="pollutant",how="left")

        #calculate risk and HI
        polar_sum3["risk"] = polar_sum3["Conc_ug_m3"]*polar_sum3["ure"]
        polar_sum3["hi_resp"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["resp"]/1000
        polar_sum3["hi_live"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["liver"]/1000
        polar_sum3["hi_neur"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["neuro"]/1000
        polar_sum3["hi_deve"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["dev"]/1000
        polar_sum3["hi_repr"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["reprod"]/1000
        polar_sum3["hi_kidn"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["kidney"]/1000
        polar_sum3["hi_ocul"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["ocular"]/1000
        polar_sum3["hi_endo"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["endoc"]/1000
        polar_sum3["hi_hema"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["hemato"]/1000
        polar_sum3["hi_immu"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["immune"]/1000
        polar_sum3["hi_skel"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["skeletal"]/1000
        polar_sum3["hi_sple"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["spleen"]/1000
        polar_sum3["hi_thyr"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["thyroid"]/1000
        polar_sum3["hi_whol"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["wholebod"]/1000
        
        #sum risk and HI to lat, lon and assign receptor type
        polar_riskhi_by_latlon = polar_sum3.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        polar_riskhi_by_latlon["rectype"] = "P"

        # Combine inner, outer, and polar riskhq
        combined_riskhi = pd.concat([inner_riskhi_by_latlon, outer_riskhi_by_latlon, polar_riskhi_by_latlon], ignore_index=True, axis=0)

        return combined_riskhi
    
    

    def process(self):

        
        start = time.time()
    
        # Read plotfile and put into dataframe
        pfile = open("resources/plotfile.plt", "r")
        plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
            names=['utme','utmn','result','elev','hill','flag','avg_time','source_id','num_yrs','net_id'],
            usecols=[0,1,2,3,4,5,6,7,8,9], 
            converters={'utme':np.float64,'utmn':np.float64,'result':np.float64,'elev':np.float64,'hill':np.float64
                   ,'flag':np.float64,'avg_time':np.str,'source_id':np.str,'num_yrs':np.int64,'net_id':np.str},
            comment='*')


        #----------- create All_Polar_Receptor output file -----------------
        all_polar_receptors = AllPolarReceptors(self.cf, self.outdir, self.facid, self.model, plot_df)
        all_polar_receptors.write()
        self.model.all_polar_receptors_df = pd.DataFrame(data=all_polar_receptors.data, columns=all_polar_receptors.headers)

 
        #----------- create All_Inner_Receptor output file -----------------
        all_inner_receptors = AllInnerReceptors(self.cf, self.outdir, self.facid, self.model, plot_df)
        all_inner_receptors.write()
        self.model.all_inner_receptors_df = pd.DataFrame(data=all_inner_receptors.data, columns=all_inner_receptors.headers)
        
        #----------- create All_Outer_Receptor output file -----------------
        all_outer_receptors = AllOuterReceptors(self.outdir, self.facid, self.model, plot_df)
        all_outer_receptors.write()
        self.model.all_outer_receptors_df = pd.DataFrame(data=all_outer_receptors.data, columns=all_outer_receptors.headers)


        # Generate a dataframe of inner/outer/polar risk and HIs by lat, lon
        self.model.risk_by_latlon = self.compute_risk_by_latlon(self. model)
        
        
        #----------- create Maximum_Individual_Risk output file ---------------
        max_indiv_risk = MaximumIndividualRisks(self.outdir, self.facid, self.model, plot_df)
        max_indiv_risk.write()
        self.model.max_indiv_risk_df = pd.DataFrame(data=max_indiv_risk.data, columns=max_indiv_risk.headers)
        
        
        #----------- create Risk Breakdown output file ------------------------
        risk_breakdown = RiskBreakdown(self.outdir, self.facid, self.model, plot_df)
        risk_breakdown.write()
 
        #debug
        import pdb; pdb.set_trace()
       
        #debug
        sys.exit()
  
      
        

        #create facility kml
        Logger.logMessage("Writing KML file for " + self.facid)
        kmlWriter = KMLWriter()
        kmlWriter.write_facility_kml(self.facid, self.runstream.cenlat, self.runstream.cenlon, self.outdir)

        return local_vars
    
    
    