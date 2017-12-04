# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 12:43:52 2017

@author: dlindsey
"""

import os
import pandas as pd
import numpy as np
import inspect


class Process_outputs():
    
    def __init__(self, facid, haplib_df, hapemis, outdir, innerblks, polar):
        self.facid = facid
        self.haplib_df = haplib_df
        self.hapemis_df = hapemis
        self.outdir = outdir
        self.innerblks_df = innerblks
        self.polar_df = polar
        
        #first check for facilities folder, if not create as output directory
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
            
            
            
    def process(self):

        # Units conversion factor
        cf = 2000*0.4536/3600/8760
    
    
        # Read plotfile and put into dataframe
        pfile = open("resources/plotfile.plt", "r")
        plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
            names=['utme','utmn','result','elev','hill','flag','avg_time','source_id','num_yrs','net_id'],
            usecols=[0,1,2,3,4,5,6,7,8,9], 
            converters={'utme':np.float64,'utmn':np.float64,'result':np.float64,'elev':np.float64,'hill':np.float64
                   ,'flag':np.float64,'avg_time':np.str,'source_id':np.str,'num_yrs':np.int64,'net_id':np.str},
            comment='*')


         #get dose response library dataframe
        haplib_df = pd.read_excel(r"resources/Dose_response_library.xlsx"
            , names=("pollutant","group","cas_no","ure","rfc","aegl_1_1h","aegl_1_8h","aegl_2_1h"
                     ,"aegl_2_8h","erpg_1","erpg_2","mrl","rel","idlh_10","teel_0","teel_1","comments"
                     ,"drvalues","group_ure","tef","acute_con")
            , converters={"pollutant":str,"group":str,"cas_no":str,"ure":float,"rfc":float,"aegl_1_1h":float,"aegl_1_8h":float
            ,"aegl_2_1h":float,"aegl_2_8h":float,"erpg_1":float,"erpg_2":float,"mrl":float,"rel":float,"idlh_10":float
            ,"teel_0":float,"teel_1":float,"comments":str,"drvalues":float,"group_ure":float,"tef":float,"acute_con":float})
        
        
        #get target organ endpoint dataframe
        targetendpt_df = pd.read_excel(r"resources/target_organ_endpoints.xlsx"
                 , names=("pollutant","epa_woe","resp","liver","neuro","dev","reprod","kidney","ocular","endoc"
                          ,"hemato","immune","skeletal","spleen","thyroid","wholebod")
                 , converters={"pollutant":str,"epa_woe":str,"resp":float,"liver":float,"neuro":float,"dev":float
                               ,"reprod":float,"kidney":float,"ocular":float,"endoc":float,"hemato":float,"immune":float
                               ,"skeletal":float,"spleen":float,"thyroid":float,"wholebod":float})

        
        
        
        # Get hapemis data for this facility
        #hapemis_df = rei.multihapemis_df.loc[rei.multihapemis_df.fac_id == facil_id]


        #------------------ Inner Receptors --------------------------------------
    
        # Pull out inner receptors and merge Inner Block blockid, angle, distance, lat, lon, and population
        ## 'angle', 'distance' need to be added back into innerblks_df - should be computed in get census blocks file
        inner_df = pd.merge(plot_df, self.innerblks_df[['IDMARPLOT', 'utme', 'utmn', 'LAT', 'LON', 'POPULATION']], on=["utme", "utmn"], how="inner")
        
        # Compute pollutant specific air concentrations 
        innerconc_df = pd.merge(inner_df, self.hapemis_df[['fac_id','source_id','pollutant','emis_tpy']], on="source_id", how="inner")
        innerconc_df.loc[:, 'conc'] = innerconc_df.result * innerconc_df.emis_tpy * cf
    
        #write to excel
        pol_con_path = self.outdir + "pollutant_concentration.xlsx"
        pol_con = pd.ExcelWriter(pol_con_path)
        innerconc_df.to_excel(pol_con,'Sheet1')
        pol_con.save()
    
    
        # Compute risk
        innerrisk0_df = pd.merge(innerconc_df, self.haplib_df[['pollutant', 'ure', 'rfc']], on="pollutant", how="inner")
        innerrisk_df = pd.merge(innerrisk0_df, targetendpt_df[['pollutant', 'resp', 'neuro', 'liver', 'dev', 'reprod', 'kidney', 'ocular', 'endoc', 'hemato', 'immune', 'skeletal', 'spleen', 'thyroid', 'wholebod']], on="pollutant", how="inner")
        print(innerrisk_df)
        innerrisk_df.loc[:, 'risk'] = innerrisk_df.conc * innerrisk_df.ure
        innerrisk_df.loc[:,'resp_hi'] = np.divide(innerrisk_df["resp"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["resp"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'live_hi'] = np.divide(innerrisk_df["liver"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["liver"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'neur_hi'] = np.divide(innerrisk_df["neuro"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["neuro"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'deve_hi'] = np.divide(innerrisk_df["dev"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["dev"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'repr_hi'] = np.divide(innerrisk_df["reprod"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["reprod"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'kidn_hi'] = np.divide(innerrisk_df["kidney"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["kidney"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'ocul_hi'] = np.divide(innerrisk_df["ocular"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["ocular"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'endo_hi'] = np.divide(innerrisk_df["endoc"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["endoc"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'hema_hi'] = np.divide(innerrisk_df["hemato"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["hemato"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'immu_hi'] = np.divide(innerrisk_df["immune"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["immune"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'skel_hi'] = np.divide(innerrisk_df["skeletal"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["skeletal"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'sple_hi'] = np.divide(innerrisk_df["spleen"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["spleen"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'thyr_hi'] = np.divide(innerrisk_df["thyroid"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["thyroid"]), where=innerrisk_df["rfc"]!=0)
        innerrisk_df.loc[:,'whol_hi'] = np.divide(innerrisk_df["wholebod"] * innerrisk_df["conc"], innerrisk_df["rfc"], out=np.zeros_like(innerrisk_df["wholebod"]), where=innerrisk_df["rfc"]!=0)

        
        #-------- Maximum Individual Risk and HI Summary -----------------
        #no angle or distance in the dataframe is it required for these computations?
        indivrisk1 = innerrisk_df[["fac_id","elev","hill","IDMARPLOT","utme","utmn","LAT","LON",
                                   "risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                   "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"]].copy()
        indivrisk2 = indivrisk1.groupby(["fac_id","elev","hill","IDMARPLOT","utme","utmn","LAT","LON"], as_index=False).sum()
        
        
        maxrisk = indivrisk2.loc[[indivrisk2.risk.idxmax()]].drop(["resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)
        
        maxresp = indivrisk2.loc[[indivrisk2.resp_hi.idxmax()]].drop(["risk","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)
        
        maxlive = indivrisk2.loc[[indivrisk2.live_hi.idxmax()]].drop(["risk","resp_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)
        
        maxneur = indivrisk2.loc[[indivrisk2.neur_hi.idxmax()]].drop(["risk","resp_hi","live_hi","deve_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)
        
        maxdeve = indivrisk2.loc[[indivrisk2.deve_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","repr_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxrepr = indivrisk2.loc[[indivrisk2.repr_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","kidn_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxkidn = indivrisk2.loc[[indivrisk2.kidn_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","ocul_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxocul = indivrisk2.loc[[indivrisk2.ocul_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","endo_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxendo = indivrisk2.loc[[indivrisk2.endo_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxhema = indivrisk2.loc[[indivrisk2.hema_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","immu_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maximmu = indivrisk2.loc[[indivrisk2.immu_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","hema_hi","skel_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxskel = indivrisk2.loc[[indivrisk2.skel_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","hema_hi","immu_hi","sple_hi","thyr_hi","whol_hi"],axis=1)

        maxsple = indivrisk2.loc[[indivrisk2.sple_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","hema_hi","immu_hi","skel_hi","thyr_hi","whol_hi"],axis=1)

        maxthyr = indivrisk2.loc[[indivrisk2.thyr_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","hema_hi","immu_hi","skel_hi","sple_hi","whol_hi"],axis=1)

        maxwhol = indivrisk2.loc[[indivrisk2.whol_hi.idxmax()]].drop(["risk","resp_hi","live_hi","neur_hi","deve_hi","repr_hi","kidn_hi","ocul_hi",
                                  "endo_hi","hema_hi","immu_hi","skel_hi","sple_hi","thyr_hi"],axis=1)

        #list of dataframes
        dfs = [maxrisk, maxresp, maxlive, maxneur, maxdeve, maxrepr, maxkidn, maxocul, maxendo,
               maxhema, maximmu, maxskel, maxsple, maxthyr, maxwhol]
        
        #concatenate the list
        max_riskhi = pd.concat(dfs)
        
        #debug
        risk_path = self.outdir + "maximum_indiv_risk.xlsx"
        risk = pd.ExcelWriter(risk_path)
        max_riskhi.to_excel(risk,'Sheet1')
        risk.save()
        
       
        #write to excel
        risk_path = self.outdir + "inner_risk.xlsx"
        risk = pd.ExcelWriter(risk_path)
        innerrisk_df.to_excel(risk,'Sheet1')
        risk.save()
        

        #------------------ Polar Receptors --------------------------------------

        polar_df = plot_df.query("net_id == 'POLGRID1'")

        # Compute pollutant specific air concentrations 
        polarconc_df = pd.merge(polar_df, self.hapemis_df[['fac_id','source_id','pollutant','emis_tpy']], on="source_id", how="inner")
        polarconc_df.loc[:, 'conc'] = polarconc_df.result * polarconc_df.emis_tpy * cf
        
        #write to excel
        polar_con_path = self.outdir + "polar_pollutant_concentration.xlsx"
        polar_con = pd.ExcelWriter(polar_con_path)
        polarconc_df.to_excel(polar_con,'Sheet1')
        polar_con.save()
        
        # Compute risk
        polarrisk_df = pd.merge(polarconc_df, self.haplib_df[['pollutant', 'ure', 'rfc']], on="pollutant", how="inner")
        polarrisk_df.loc[:, 'resp'] = targetendpt_df['resp']
        polarrisk_df.loc[:, 'neuro'] = targetendpt_df['neuro']
        polarrisk_df.loc[:, 'risk'] = polarrisk_df.conc * polarrisk_df.ure
        polarrisk_df.loc[:,'resp_hi'] = np.divide(polarrisk_df["resp"] * polarrisk_df["conc"], polarrisk_df["rfc"], out=np.zeros_like(polarrisk_df["resp"]), where=polarrisk_df["rfc"]!=0)
        polarrisk_df.loc[:,'neur_hi'] = np.divide(polarrisk_df["neuro"] * polarrisk_df["conc"], polarrisk_df["rfc"], out=np.zeros_like(polarrisk_df["neuro"]), where=polarrisk_df["rfc"]!=0)

        #write to excel
        polarrisk_path = self.outdir + "polar_risk.xlsx"
        polarrisk = pd.ExcelWriter(polarrisk_path)
        polarrisk_df.to_excel(polarrisk,'Sheet1')
        polarrisk.save()
    
    
        local_vars = inspect.currentframe().f_locals    
    
        print("Done!")

        return local_vars
    
# output_dir = r"C:\Temp\Python_lessons\HEM3 Outputs"
# proc_output(output_dir)

    
    # Put the plot dataframe into a Firebird table
#    con = fdb.connect(dsn='c:/HEM3_python/DB/hem3.fdb', user='SYSDBA', password='masterkey')
#    bytesInUse = con.database_info(fdb.isc_info_current_memory, 'i')
#    print ('The server is currently using %d bytes of memory.' % bytesInUse)
#
#    cur = con.cursor()
 #   cur.execute("insert into test (x, y) values (1.5, 2.5)")
 #   cur.execute("select x, y from test")
 #   for (x) in cur:
 #       str_x = str(x)
 #       print ("x value is %s" % str_x)
#    cur.execute("create table test2 (i integer, j integer)")
#    con.commit()
#    con.close()
    
 #   cur.execute("insert into test2 (i, j) values (9, 10)")
 #   cur.execute("select i, j from test2")
 #   for (i) in cur:
 #       str_i = str(i)
 #       print ("i value is %s" % str_i)

    
    