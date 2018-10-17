# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 12:43:52 2017

@author: dlindsey
"""
import sys
import time
import numpy as np
import pandas as pd

from log.Logger import Logger
from writer.csv.AllPolarReceptors import AllPolarReceptors
from writer.csv.AllInnerReceptors import AllInnerReceptors
from writer.csv.AllOuterReceptors import AllOuterReceptors
from writer.csv.RingSummaryChronic import RingSummaryChronic
from writer.excel.MaximumIndividualRisks import MaximumIndividualRisks
# from writer.excel.RiskBreakdown import RiskBreakdown
from writer.kml.KMLWriter import KMLWriter


class Process_outputs():
    
    def __init__(self, outdir, facid, model, prep, runstream):
        self.facid = facid
        self.haplib_m = model.haplib.dataframe.as_matrix()
        self.hapemis = runstream.hapemis
        self.outdir = outdir
        self.model = model
        self.runstream = runstream
        self.model.numsectors = self.model.polargrid["sector"].max()
        self.model.numrings = self.model.polargrid["ring"].max()
        self.model.innerblks_df = prep.innerblks
        self.model.outerblks_df = prep.outerblks
        self.model.runstream_hapemis = runstream.hapemis

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

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
        inner_sum = self.model.all_inner_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge risk factors (cancer and noncancer) by pollutant        
        inner_sum2 = pd.merge(inner_sum, self.model.riskfacs_df, left_on="Pollutant", right_on="pollutant", how="left")
#        inner_sum2 = pd.merge(inner_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if inner_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

#        #merge target organ endpoint values 
#        inner_sum3 = pd.merge(inner_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
#                                                                      "reprod","kidney","ocular","endoc","hemato",
#                                                                      "immune","skeletal","spleen","thyroid",
#                                                                      "wholebod"]],on="pollutant",how="left")
       
        #calculate risk and target organ specific HIs 
        inner_sum2["risk"] = inner_sum2["Conc_ug_m3"]*inner_sum2["ure"]
        inner_sum2["hi_resp"] = inner_sum2["Conc_ug_m3"]*inner_sum2["resp_fac"]/1000
        inner_sum2["hi_live"] = inner_sum2["Conc_ug_m3"]*inner_sum2["live_fac"]/1000
        inner_sum2["hi_neur"] = inner_sum2["Conc_ug_m3"]*inner_sum2["neur_fac"]/1000
        inner_sum2["hi_deve"] = inner_sum2["Conc_ug_m3"]*inner_sum2["deve_fac"]/1000
        inner_sum2["hi_repr"] = inner_sum2["Conc_ug_m3"]*inner_sum2["repr_fac"]/1000
        inner_sum2["hi_kidn"] = inner_sum2["Conc_ug_m3"]*inner_sum2["kidn_fac"]/1000
        inner_sum2["hi_ocul"] = inner_sum2["Conc_ug_m3"]*inner_sum2["ocul_fac"]/1000
        inner_sum2["hi_endo"] = inner_sum2["Conc_ug_m3"]*inner_sum2["endo_fac"]/1000
        inner_sum2["hi_hema"] = inner_sum2["Conc_ug_m3"]*inner_sum2["hema_fac"]/1000
        inner_sum2["hi_immu"] = inner_sum2["Conc_ug_m3"]*inner_sum2["immu_fac"]/1000
        inner_sum2["hi_skel"] = inner_sum2["Conc_ug_m3"]*inner_sum2["skel_fac"]/1000
        inner_sum2["hi_sple"] = inner_sum2["Conc_ug_m3"]*inner_sum2["sple_fac"]/1000
        inner_sum2["hi_thyr"] = inner_sum2["Conc_ug_m3"]*inner_sum2["thyr_fac"]/1000
        inner_sum2["hi_whol"] = inner_sum2["Conc_ug_m3"]*inner_sum2["whol_fac"]/1000
        
#        inner_sum3["risk"] = inner_sum3["Conc_ug_m3"]*inner_sum3["ure"]
#        inner_sum3["hi_resp"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["resp"]/1000
#        inner_sum3["hi_live"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["liver"]/1000
#        inner_sum3["hi_neur"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["neuro"]/1000
#        inner_sum3["hi_deve"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["dev"]/1000
#        inner_sum3["hi_repr"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["reprod"]/1000
#        inner_sum3["hi_kidn"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["kidney"]/1000
#        inner_sum3["hi_ocul"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["ocular"]/1000
#        inner_sum3["hi_endo"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["endoc"]/1000
#        inner_sum3["hi_hema"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["hemato"]/1000
#        inner_sum3["hi_immu"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["immune"]/1000
#        inner_sum3["hi_skel"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["skeletal"]/1000
#        inner_sum3["hi_sple"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["spleen"]/1000
#        inner_sum3["hi_thyr"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["thyroid"]/1000
#        inner_sum3["hi_whol"] = self.nodivby0(inner_sum3["Conc_ug_m3"],inner_sum3["rfc"])*inner_sum3["wholebod"]/1000
        
        #sum risk and HI to lat, lon and assign a receptor type
        inner_riskhi_by_latlon = inner_sum2.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        inner_riskhi_by_latlon["rectype"] = "I"


        #--------- second - outer receptor risk by lat/lon ----------------
        
        #sum conc to lat, Lon, pollutant
        outer_sum = self.model.all_outer_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge risk factors (cancer and noncancer) by pollutant        
        outer_sum2 = pd.merge(outer_sum, self.model.riskfacs_df, left_on="Pollutant", right_on="pollutant", how="left")
#        outer_sum2 = pd.merge(outer_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if outer_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

        #calculate risk and target organ specific HIs 
        outer_sum2["risk"] = outer_sum2["Conc_ug_m3"]*outer_sum2["ure"]
        outer_sum2["hi_resp"] = outer_sum2["Conc_ug_m3"]*outer_sum2["resp_fac"]/1000
        outer_sum2["hi_live"] = outer_sum2["Conc_ug_m3"]*outer_sum2["live_fac"]/1000
        outer_sum2["hi_neur"] = outer_sum2["Conc_ug_m3"]*outer_sum2["neur_fac"]/1000
        outer_sum2["hi_deve"] = outer_sum2["Conc_ug_m3"]*outer_sum2["deve_fac"]/1000
        outer_sum2["hi_repr"] = outer_sum2["Conc_ug_m3"]*outer_sum2["repr_fac"]/1000
        outer_sum2["hi_kidn"] = outer_sum2["Conc_ug_m3"]*outer_sum2["kidn_fac"]/1000
        outer_sum2["hi_ocul"] = outer_sum2["Conc_ug_m3"]*outer_sum2["ocul_fac"]/1000
        outer_sum2["hi_endo"] = outer_sum2["Conc_ug_m3"]*outer_sum2["endo_fac"]/1000
        outer_sum2["hi_hema"] = outer_sum2["Conc_ug_m3"]*outer_sum2["hema_fac"]/1000
        outer_sum2["hi_immu"] = outer_sum2["Conc_ug_m3"]*outer_sum2["immu_fac"]/1000
        outer_sum2["hi_skel"] = outer_sum2["Conc_ug_m3"]*outer_sum2["skel_fac"]/1000
        outer_sum2["hi_sple"] = outer_sum2["Conc_ug_m3"]*outer_sum2["sple_fac"]/1000
        outer_sum2["hi_thyr"] = outer_sum2["Conc_ug_m3"]*outer_sum2["thyr_fac"]/1000
        outer_sum2["hi_whol"] = outer_sum2["Conc_ug_m3"]*outer_sum2["whol_fac"]/1000

#        #merge target organ endpoint values
#        outer_sum3 = pd.merge(outer_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
#                                                                      "reprod","kidney","ocular","endoc","hemato",
#                                                                      "immune","skeletal","spleen","thyroid",
#                                                                      "wholebod"]],on="pollutant",how="left")

#        #calculate risk and HI
#        outer_sum3["risk"] = outer_sum3["Conc_ug_m3"]*outer_sum3["ure"]
#        outer_sum3["hi_resp"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["resp"]/1000
#        outer_sum3["hi_live"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["liver"]/1000
#        outer_sum3["hi_neur"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["neuro"]/1000
#        outer_sum3["hi_deve"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["dev"]/1000
#        outer_sum3["hi_repr"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["reprod"]/1000
#        outer_sum3["hi_kidn"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["kidney"]/1000
#        outer_sum3["hi_ocul"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["ocular"]/1000
#        outer_sum3["hi_endo"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["endoc"]/1000
#        outer_sum3["hi_hema"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["hemato"]/1000
#        outer_sum3["hi_immu"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["immune"]/1000
#        outer_sum3["hi_skel"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["skeletal"]/1000
#        outer_sum3["hi_sple"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["spleen"]/1000
#        outer_sum3["hi_thyr"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["thyroid"]/1000
#        outer_sum3["hi_whol"] = self.nodivby0(outer_sum3["Conc_ug_m3"],outer_sum3["rfc"])*outer_sum3["wholebod"]/1000
          
        #sum risk and HI to lat, lon and assign receptor type
        outer_riskhi_by_latlon = outer_sum2.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        outer_riskhi_by_latlon["rectype"] = "O"


        #---------- third - polar receptor risk by lat/lon --------------
        
        #sum conc to lat, lon, pollutant
        polar_sum = self.model.all_polar_receptors_df.groupby(['Lat','Lon','Pollutant','Overlap'], as_index=False)['Conc_ug_m3'].sum()
        
        #merge risk factors (cancer and noncancer) by pollutant        
        polar_sum2 = pd.merge(polar_sum, self.model.riskfacs_df, left_on="Pollutant", right_on="pollutant", how="left")
#        polar_sum2 = pd.merge(polar_sum,self.model.haplib.dataframe[["pollutant","ure","rfc"]],left_on="Pollutant",right_on="pollutant",how="left")
        if polar_sum2["ure"].isnull().sum() > 0:
            #TODO
            #THIS IS AN ERROR TO BE HANDLED
            print("Error!")

        #calculate risk and target organ specific HIs 
        polar_sum2["risk"] = polar_sum2["Conc_ug_m3"]*polar_sum2["ure"]
        polar_sum2["hi_resp"] = polar_sum2["Conc_ug_m3"]*polar_sum2["resp_fac"]/1000
        polar_sum2["hi_live"] = polar_sum2["Conc_ug_m3"]*polar_sum2["live_fac"]/1000
        polar_sum2["hi_neur"] = polar_sum2["Conc_ug_m3"]*polar_sum2["neur_fac"]/1000
        polar_sum2["hi_deve"] = polar_sum2["Conc_ug_m3"]*polar_sum2["deve_fac"]/1000
        polar_sum2["hi_repr"] = polar_sum2["Conc_ug_m3"]*polar_sum2["repr_fac"]/1000
        polar_sum2["hi_kidn"] = polar_sum2["Conc_ug_m3"]*polar_sum2["kidn_fac"]/1000
        polar_sum2["hi_ocul"] = polar_sum2["Conc_ug_m3"]*polar_sum2["ocul_fac"]/1000
        polar_sum2["hi_endo"] = polar_sum2["Conc_ug_m3"]*polar_sum2["endo_fac"]/1000
        polar_sum2["hi_hema"] = polar_sum2["Conc_ug_m3"]*polar_sum2["hema_fac"]/1000
        polar_sum2["hi_immu"] = polar_sum2["Conc_ug_m3"]*polar_sum2["immu_fac"]/1000
        polar_sum2["hi_skel"] = polar_sum2["Conc_ug_m3"]*polar_sum2["skel_fac"]/1000
        polar_sum2["hi_sple"] = polar_sum2["Conc_ug_m3"]*polar_sum2["sple_fac"]/1000
        polar_sum2["hi_thyr"] = polar_sum2["Conc_ug_m3"]*polar_sum2["thyr_fac"]/1000
        polar_sum2["hi_whol"] = polar_sum2["Conc_ug_m3"]*polar_sum2["whol_fac"]/1000

#        #merge target organ endpoint values
#        polar_sum3 = pd.merge(polar_sum2,self.model.organs.dataframe[["pollutant","resp","liver","neuro","dev",
#                                                                      "reprod","kidney","ocular","endoc","hemato",
#                                                                      "immune","skeletal","spleen","thyroid",
#                                                                      "wholebod"]],on="pollutant",how="left")

#        #calculate risk and HI
#        polar_sum3["risk"] = polar_sum3["Conc_ug_m3"]*polar_sum3["ure"]
#        polar_sum3["hi_resp"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["resp"]/1000
#        polar_sum3["hi_live"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["liver"]/1000
#        polar_sum3["hi_neur"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["neuro"]/1000
#        polar_sum3["hi_deve"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["dev"]/1000
#        polar_sum3["hi_repr"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["reprod"]/1000
#        polar_sum3["hi_kidn"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["kidney"]/1000
#        polar_sum3["hi_ocul"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["ocular"]/1000
#        polar_sum3["hi_endo"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["endoc"]/1000
#        polar_sum3["hi_hema"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["hemato"]/1000
#        polar_sum3["hi_immu"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["immune"]/1000
#        polar_sum3["hi_skel"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["skeletal"]/1000
#        polar_sum3["hi_sple"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["spleen"]/1000
#        polar_sum3["hi_thyr"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["thyroid"]/1000
#        polar_sum3["hi_whol"] = self.nodivby0(polar_sum3["Conc_ug_m3"],polar_sum3["rfc"])*polar_sum3["wholebod"]/1000
        
        #sum risk and HI to lat, lon and assign receptor type
        polar_riskhi_by_latlon = polar_sum2.groupby(['Lat','Lon','Overlap'], as_index=False)["risk","hi_resp","hi_live",
                                                  "hi_neur","hi_deve","hi_repr","hi_kidn","hi_ocul","hi_endo",
                                                  "hi_hema","hi_immu","hi_skel","hi_sple","hi_thyr","hi_whol"].sum()
        polar_riskhi_by_latlon["rectype"] = "P"

        # Combine inner, outer, and polar riskhq
        combined_riskhi = pd.concat([inner_riskhi_by_latlon, outer_riskhi_by_latlon, polar_riskhi_by_latlon], ignore_index=True, axis=0)

        return combined_riskhi
    
    
    def create_riskfacs(self):
        """
        Combine the dose response and target organ tables into one dataframe. Also create noncancer endpoint
        specific factors (multipliers) that are defined as (endpoint factor)/rfc.
        """
        
        riskfacs_df = pd.merge(self.model.haplib.dataframe[["pollutant","ure","rfc"]], self.model.organs.dataframe[["pollutant",
                          "resp","liver","neuro","dev","reprod","kidney","ocular","endoc","hemato","immune",
                          "skeletal","spleen","thyroid","wholebod"]], on="pollutant", how="inner")
        riskfacs_df["resp_fac"] = self.nodivby0(riskfacs_df["resp"], riskfacs_df["rfc"])
        riskfacs_df["live_fac"] = self.nodivby0(riskfacs_df["liver"], riskfacs_df["rfc"])
        riskfacs_df["neur_fac"] = self.nodivby0(riskfacs_df["neuro"], riskfacs_df["rfc"])
        riskfacs_df["deve_fac"] = self.nodivby0(riskfacs_df["dev"], riskfacs_df["rfc"])
        riskfacs_df["repr_fac"] = self.nodivby0(riskfacs_df["reprod"], riskfacs_df["rfc"])
        riskfacs_df["kidn_fac"] = self.nodivby0(riskfacs_df["kidney"], riskfacs_df["rfc"])
        riskfacs_df["ocul_fac"] = self.nodivby0(riskfacs_df["ocular"], riskfacs_df["rfc"])
        riskfacs_df["endo_fac"] = self.nodivby0(riskfacs_df["endoc"], riskfacs_df["rfc"])
        riskfacs_df["hema_fac"] = self.nodivby0(riskfacs_df["hemato"], riskfacs_df["rfc"])
        riskfacs_df["immu_fac"] = self.nodivby0(riskfacs_df["immune"], riskfacs_df["rfc"])
        riskfacs_df["skel_fac"] = self.nodivby0(riskfacs_df["skeletal"], riskfacs_df["rfc"])
        riskfacs_df["sple_fac"] = self.nodivby0(riskfacs_df["spleen"], riskfacs_df["rfc"])
        riskfacs_df["thyr_fac"] = self.nodivby0(riskfacs_df["thyroid"], riskfacs_df["rfc"])
        riskfacs_df["whol_fac"] = self.nodivby0(riskfacs_df["wholebod"], riskfacs_df["rfc"])
        riskfacs_df.drop(["resp","liver","neuro","dev","reprod","kidney","ocular","endoc","hemato","immune",
                          "skeletal","spleen","thyroid","wholebod"], axis=1, inplace=True)
               
        return riskfacs_df
    

    def process(self):

        # Read plotfile and put into dataframe
        with open("resources/plotfile.plt", "r") as pfile:
            plot_df = pd.read_table(pfile, delim_whitespace=True, header=None,
                names=['utme','utmn','result','elev','hill','flag','avg_time','source_id','num_yrs','net_id'],
                usecols=[0,1,2,3,4,5,6,7,8,9],
                converters={'utme':np.float64,'utmn':np.float64,'result':np.float64,'elev':np.float64,'hill':np.float64
                       ,'flag':np.float64,'avg_time':np.str,'source_id':np.str,'num_yrs':np.int64,'net_id':np.str},
                comment='*')

        # Combine the dose response and target organ tables into one and create noncancer factors (multipliers)
        self.model.riskfacs_df = self.create_riskfacs()
        
        #----------- create All_Polar_Receptor output file -----------------
        all_polar_receptors = AllPolarReceptors(self.outdir, self.facid, self.model, plot_df)
        all_polar_receptors.write()
        self.model.all_polar_receptors_df = pd.DataFrame(data=all_polar_receptors.data, columns=all_polar_receptors.headers)
 
        #----------- create All_Inner_Receptor output file -----------------
        all_inner_receptors = AllInnerReceptors(self.outdir, self.facid, self.model, plot_df)
        all_inner_receptors.write()
        self.model.all_inner_receptors_df = pd.DataFrame(data=all_inner_receptors.data, columns=all_inner_receptors.headers)

        #----------- create All_Outer_Receptor output file -----------------
        all_outer_receptors = AllOuterReceptors(self.outdir, self.facid, self.model, plot_df)
        all_outer_receptors.write()
        self.model.all_outer_receptors_df = pd.DataFrame(data=all_outer_receptors.data, columns=all_outer_receptors.headers)

        # Generate a dataframe of inner/outer/polar risk and HIs by lat, lon
        self.model.risk_by_latlon = self.compute_risk_by_latlon(self.model)

        #----------- create Maximum_Individual_Risk output file ---------------
        max_indiv_risk = MaximumIndividualRisks(self.outdir, self.facid, self.model, plot_df)
        max_indiv_risk.write()
        self.model.max_indiv_risk_df = pd.DataFrame(data=max_indiv_risk.data, columns=max_indiv_risk.headers)

        #----------- create Ring_Summary_Chronic output file -----------------
        ring_summary_chronic = RingSummaryChronic(self.outdir, self.facid, self.model, plot_df)
        ring_summary_chronic.write()

#        #----------- create Risk Breakdown output file ------------------------
#        risk_breakdown = RiskBreakdown(self.outdir, self.facid, self.model, plot_df)
#        risk_breakdown.write()
     
        

#        #create facility kml
#        Logger.logMessage("Writing KML file for " + self.facid)
#        kmlWriter = KMLWriter()
#        kmlWriter.write_facility_kml(self.facid, self.runstream.cenlat, self.runstream.cenlon, self.outdir)

#        return local_vars
    
    
    