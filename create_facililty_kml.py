# -*- coding: utf-8 -*-
"""
Spyder Editor

Create text file to be used to create kml file.
"""
import pandas as pd
import numpy as np
from operator import itemgetter
from collections import OrderedDict
from shutil import copyfile


class facility_kml():
    
    def __init__(self, facid, faccen_lat, faccen_lon, outdir):
        
        self.facid = facid
        self.faccen_lat = faccen_lat
        self.faccen_lon = faccen_lon
        self.outdir = outdir
        
#        self.srcmap = pd.read_excel(r"C:\python\HEM4\KML\Inputs\source_map_w_line.xlsx"
#                       , names=("utm_e","area","point","census","lat","lon","distance","min_dist"
#                               ,"bearing","elev","population","source_id","src_height","src_type","lat2","lon2")
#                       , converters={"utm_e":float,"area":float,"point":float,"census":float,"lat":float,"lon":float
#                               ,"distance":float,"min_dist":float,"bearing":float,"elev":float,"population":float
#                               ,"source_id":str,"src_height":float,"src_type":str,"lat2":float,"lon2":float})
    
        pxl = pd.ExcelFile(self.outdir + "polar_risk.xlsx") 
        self.allpolar = pd.read_excel(pxl)
#                               , names=("source_id", "risk","pollutant","distance","angle","sector","ring","lat","lon"
#                                        ,"toshi","total_hi","poll_hi")
#                               , converters={"source_id":str,"risk":float,"pollutant":str,"distance":float,"angle":float
#                                       ,"sector":float,"ring":float,"lat":float,"lon":float,"toshi":str
#                                       ,"total_hi":float,"poll_hi":float})
#            
        self.allpolar['toshi'] = np.nan
        self.allpolar['total_hi'] = np.nan
        self.allpolar['pll_hi'] = np.nan
        
        #access innersik.xlxs for facility
        inxl = pd.ExcelFile(self.outdir + "inner_risk.xlsx")
        self.allinner = pd.read_excel(inxl)
        self.allinner['block'] = self.allinner['IDMARPLOT'][5:]
#                               , names=("utme","utmn","result","elev","hill","flag","avg_time","source_id","num_yrs","net_id"
#                                        ,"block","lat","lon","population","fac_id","pollutant","emis_tpy","conc","ure","rfc"
#                                        ,"resp","neuro","risk","resp_hi","neur_hi")
#                               , converters={"utme":float,"utmn":float,"result":float,"elev":float,"hill":float,"flag":float
#                                       ,"avg_time":str,"source_id":str,"num_yrs":float,"net_id":str,"block":str,"lat":float,"lon":float      
#                                       ,"population":float,"fac_id":str,"pollutant":str,"emis_tpy":float,"conc":float
#                                       ,"ure":float,"rfc":float,"resp":float,"neuro":float,"risk":float
#                                       ,"resp_hi":float,"neur_hi":float})    
#            
           
        
#        self.mir = pd.read_excel(r"C:\python\HEM4\KML\Inputs\maximum_indiv_risks.xlsx"
#                           , names=("parameter","value","population","distance","angle","elevation"
#                                   ,"fips","block","lat","lon","rec_type")
#                           , converters={"parameter":str,"value":float,"population":float,"distance":float,"angle":float
#                                   ,"elevation":float,"fips":str,"block":str,"lat":float,"lon":float,"rec_type":str})
#                                   

        #removed mir for now
        kmlfilename = self.write_kml()


#%%Create the KML file for a given facility

    def write_kml(self):

        # Get the source KML file for this facility and copy it to the output folder as the facility KML        
        srckml_fname = "working_kml/fac_" + str(self.facid) + "_source.kml"
        fackml_fname = self.outdir + "fac_" + str(self.facid) + "_srcrec.kml"
        copyfile(srckml_fname, fackml_fname)
        
        kmlfilename = "kml_file.txt"
        
        inp_file = open(r"kml_file.txt","w")
    
          
    
        # Read source map file to get source ids, source type and location parameters
        
        # create groups by source id and source type
        #src_df = srcmap.groupby(['source_id','src_type'])
        
   
         
    # facility center defined 
        
            
        k01 = "<Folder> \n"
        k02 = "  " + "<name>Domain center</name> \n"
        k03 = "  " + "<open>0</open> \n"
        k04 = "  " + "<Placemark> \n"
        k05 = "    " + "<name>Domain center</name> \n"
        k06 = "    " + "<snippet></snippet> \n" 
        k07 = "    " + "<description><![CDATA[<div align='center'>Plant center</div> ]]></description> \n" 
        k08 = "    " + "<styleUrl>#s100</styleUrl> \n"
        k09 = "    " + "<Point><altitudeMode>relativeToGround</altitudeMode> \n"
        k10 = "      " + "<coordinates>" + str(self.faccen_lon) + "," + str(self.faccen_lat) + ",0</coordinates></Point> \n"
        
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
        inp_file.write(k05)
        inp_file.write(k06)
        inp_file.write(k07)
        inp_file.write(k08)
        inp_file.write(k09)
        inp_file.write(k10)
        
        k01 = "  " + "</Placemark> \n"
        k02 = "</Folder> \n"
        k03 = " \n"
    
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
#        
    # end write facility center
    
    # Determine if there are any user receptors
        for block, group in self.allinner.groupby(["block"]):
            user_rcpt = block
            ublock = group.iloc[0]['block']
            ulat = group.iloc[0]['LAT']
            ulon = group.iloc[0]['LON']
            u = 0
            if user_rcpt == 'U' and u == 0:
                k01 = "<Folder> \n" 
                k02 = "  " + "<name>User receptor cancer risk</name> \n"
                k03 = "  " + "<open>0</open> \n"   
                k04 = " \n" 
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                    
            if user_rcpt == 'U':        
                k01 = "  " + "<Placemark> \n"
                k02 = "    " + "<name>User Receptor: " + ublock + " </name> \n"
                k03 = "    " + "<snippet></snippet> \n" 
                k04 = "    " + "<description><![CDATA[<div align='center'><B> Discrete Receptor</B> <br /> \n"
                k05 = "    " + "<B> ID: " + ublock + "</B> <br /> \n"
                k06 = "    " + "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n"
                urtot = group.iloc[0]['risk'] * 1000000
                urrnd = round(urtot,2)
                k07 = "    " + "Total = " + str(urrnd) + "<br /><br /> \n"
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                inp_file.write(k05)
                inp_file.write(k06)
                inp_file.write(k07)
    
                if urrnd > 0:
                    k08 = "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"
                    inp_file.write(k08)
                
    # create dictionary to hold summed risk of each pollutant        
                    urhap_sum = {}
                    for index, row in group.iterrows():
                
                    #keys = cbhap_sum.keys()
                        if row["pollutant"] not in urhap_sum:
                            urhap_sum[row["pollutant"]] = row["risk"]
                       #inp_file.write(row["pollutant"])
                        else:
                           pol = urhap_sum[row["pollutant"]]
                           risksum = row["risk"] + pol
                           urhap_sum[row["pollutant"]] = risksum  
                           
    #sort the dictionary by value 
                    sorted_urhap_sum = OrderedDict(sorted(urhap_sum.items(), key=itemgetter(1)))                       
    
     # check to make sure large enough value to keep
                    for k, x in sorted_urhap_sum.items():
                        z = x * 1000000     # risk in a million 0.005
                        if z > 0.005:
                            zrnd = round(z,2)
                            p01 = "    " + format(k) + " = " + format(zrnd) + "<br /> \n"
                            inp_file.write(p01)
                                    
                    k01 = "    " + "</div> ]]> </description> \n"    
                    k02 = "    " + "<styleUrl>#u20</styleUrl> \n"
                    k03 = "    " + "<Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" + str(ulon) + "," + str(ulat) + ",0.0000</coordinates></Point> \n"    
                    k04 = "  " + "</Placemark> \n"    
                    k05 = " \n" 
                    inp_file.write(k01)
                    inp_file.write(k02)
                    inp_file.write(k03)
                    inp_file.write(k04)
                    inp_file.write(k05)
                
    # First user receptor processed            
            u = u + 1
                
    # end  of user receptor folder 
            if u > 0 and user_rcpt != 'U':    
                k06 = "</Folder> \n"
                k07 = " \n"
                u = 0
                inp_file.write(k06) 
                inp_file.write(k07)              
                
    # Write inner receptors 
        k01 = "<Folder> \n"    
        k02 = "  " + "<name>Census block cancer risk</name> \n"
        k03 = "  " + "<open>0</open> \n" 
        k04 = " \n"
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
    
        for loc, group in self.allinner.groupby(["LAT","LON"]):
            slat = loc[0]
            slon = loc[1]
            sBlock = group.iloc[0]['block']
    #        sFips = group.iloc[0]['block':5]
            k01 = "  " + "<Placemark> \n"
            k02 = "    " + "<name>Block Receptor " + str(sBlock) + " </name> \n"
            k03 = "    " + "<snippet></snippet> \n" 
            k04 = "    " + "<description><![CDATA[<div align='center'><B> Census Block Receptor</B> <br /> \n"
    #        k05 = "    " + "<B> FIPS: " + sFips + " Block: " + str(group.iloc[0]['block']) + "</B> <br /> \n"
            k05 = "    " + "<B> Block: " + str(group.iloc[0]['block']) + "</B> <br /> \n"
            k06 = "    " + "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n"
            cbtot = group.iloc[0]['risk'] * 1000000
            cbrnd = round(cbtot,2)
            k07 = "    " + "Total = " + str(cbrnd) + "<br /><br /> \n"
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
            inp_file.write(k06)
            inp_file.write(k07)
            
            if cbrnd > 0:
                k08 = "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"
                inp_file.write(k08)
            
     # create dictionary to hold summed risk of each pollutant        
                cbhap_sum = {}
                for index, row in group.iterrows():
                
                    #keys = cbhap_sum.keys()
                    if row["pollutant"] not in cbhap_sum:
                       cbhap_sum[row["pollutant"]] = row["risk"]
                       #inp_file.write(row["pollutant"])
                    else:
                        pol = cbhap_sum[row["pollutant"]]
                        risksum = row["risk"] + pol
                        cbhap_sum[row["pollutant"]] = risksum
      
    #        inp_file.write(str(cbhap_sum))
    
    #sort the dictionary by value 
                sorted_cbhap_sum = OrderedDict(sorted(cbhap_sum.items(), key=itemgetter(1)))
           
     # check to make sure large enough value to keep
                for k, v in sorted_cbhap_sum.items():
                    w = v * 1000000     # risk in a million 0.005
                    if w > 0.005:
                        wrnd = round(w,2)
                        p01 = "    " + format(k) + " = " + format(wrnd) + "<br /> \n"
                        inp_file.write(p01)
                
            
            k01 = "    " + "</div> ]]> </description> \n"    
            k02 = "    " + "<styleUrl>#b20</styleUrl> \n"
            k03 = "    " + "<Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" + str(slon) + "," + str(slat) + ",0.0000</coordinates></Point> \n"    
            k04 = "  " + "</Placemark> \n"    
            k05 = " \n"    
                
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)    
            
    # end inner receptors        
        k00 = "</Folder> \n"
        inp_file.write(k00)
        
    # Write toshi for inner receptors   
        k01 = "<Folder> \n"    
        k02 = "  " + "<name>Census block TOSHI</name> \n"
        k03 = "  " + "<open>0</open> \n" 
        k04 = " \n"
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
    
        for loc, group in self.allinner.groupby(["LAT","LON"]):
            slat = loc[0]
            slon = loc[1]
            sBlock = group.iloc[0]['block']
    
            k00 = "  " + "<Placemark> \n"
            k01 = "    " + "<name>Block Receptor " + str(sBlock) + " </name> \n"
            k02 = "    " + "<visibility>0</visibility> \n"
            k03 = "    " + "<snippet></snippet> \n" 
            k04 = "    " + "<description><![CDATA[<div align='center'><B> Census Block Receptor</B> <br /> \n"
            k05 = "    " + "<B> Block: " + str(group.iloc[0]['block']) + "</B> <br /> \n"
            k06 = "    " + "<B> HEM4 Estimated Maximum TOSHI (Respiratory) </B> <br /> \n"
    #        k06 = "    " + "<B> HEM4 Estimated Maximum TOSHI (" + str(group.iloc[0]['resp_hi']) + ") </B> <br /> \n"
            hitot = group.iloc[0]['resp_hi']
            hirnd = round(hitot,2)
            k07 = "    " + "Total = " + str(hirnd) + "<br /><br /> \n"
            
            inp_file.write(k00)
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
            inp_file.write(k06)
            inp_file.write(k07)
            
            if hirnd > 0: 
                k08 = "    " + "<U> Top Pollutants Contributing to TOSHI </U> <br /> \n"
            
                inp_file.write(k08)
            
     # create dictionary to hold summed risk of each pollutant        
                cbhap_sum = {}
                for index, row in group.iterrows():
                
                    #keys = cbhap_sum.keys()
                    if row["pollutant"] not in cbhap_sum:
                       cbhap_sum[row["pollutant"]] = row["resp_hi"]
                       #inp_file.write(row["pollutant"])
                    else:
                        pol = cbhap_sum[row["pollutant"]]
                        risksum = row["resp_hi"] + pol
                        cbhap_sum[row["pollutant"]] = risksum
    
    #sort the dictionary by value 
                sorted_cbhap_sum = OrderedDict(sorted(cbhap_sum.items(), key=itemgetter(1)))  
    
    # check to make sure large enough value to keep
                for k, v in sorted_cbhap_sum.items():
                    w = v * 1000000     # risk in a million 0.005
                    if w > 0.005:
                       wrnd = round(w,2)
                       p01 = "    " + format(k) + " = " + format(wrnd) + "<br /> \n"
                       inp_file.write(p01)
                
            
            k01 = "    " + "</div> ]]> </description> \n"    
            k02 = "    " + "<styleUrl>#b20</styleUrl> \n"
            k03 = "    " + "<Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" + str(slon) + "," + str(slat) + ",0.0000</coordinates></Point> \n"    
            k04 = "  " + "</Placemark> \n"    
            k05 = " \n"    
                
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)    
            
        k00 = "</Folder> \n"
        
    # end TOSHI for inner receptors
      
    # start polar receptors cancer risk folder   
        k01 = "<Folder> \n"    
        k02 = "  " + "<name>Polar receptor cancer risk</name> \n"
        k03 = "  " + "<open>0</open> \n" 
        k04 = " \n"
        inp_file.write(k00)
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
        
    # Write polar grid rings for cancer risk
    #for name, group in srcmap.groupby(["source_id","src_type"]):
    
        for loc, group in self.allpolar.groupby(["lat","lon"]):
            slat = loc[0]
            slon = loc[1]
            pg_dist = str(round(group.iloc[0]['distance'],0))
            pg_angle = str(round(group.iloc[0]['angle'],0))
            
            k01 = "  " + "<Placemark> \n"
            k02 = "    " + "<name>Polar Receptor Distance: " + pg_dist + " Angle: " + str(group.iloc[0]['angle']) + " </name> \n"
            k03 = "    " + "<visibility>0</visibility> \n" 
            k04 = "    " + "<snippet></snippet> \n"
            k05 = "    " + "<description><![CDATA[<div align='center'><B> Polar Receptor</B> <br /> \n"
            k06 = "    " + "<B> Distance: " + pg_dist + " Angle: " + pg_angle + "</B> <br /> \n"
            k07 = "    " + "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n"
            pgtot = group.iloc[0]['risk'] * 1000000
            pgrnd = round(pgtot,2)
            k08 = "    " + "Total = " + str(pgrnd) + "<br /><br /> \n"
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
            inp_file.write(k06)
            inp_file.write(k07)
            inp_file.write(k08)
            
            if pgrnd > 0:
                k09 = "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"
                inp_file.write(k09)
    
     # create dictionary to hold summed risk of each pollutant        
                pghap_sum = {}        
                for index, row in group.iterrows():
                
                    #keys = pghap_sum.keys()
                    if row["pollutant"] not in pghap_sum:
                       pghap_sum[row["pollutant"]] = row["risk"]
                 
                    else:
                        pol = pghap_sum[row["pollutant"]]
                        risksum = row["risk"] + pol
                        pghap_sum[row["pollutant"]] = risksum    
    #sort the dictionary by value 
                    sorted_pghap_sum = OrderedDict(sorted(pghap_sum.items(), key=itemgetter(1)))  
                    
    # check to make sure large enough value to keep
                    for k, v in sorted_pghap_sum.items():
                        z = v * 1000000     # risk in a million 
                        if z > 0.005:
                            zrnd = round(v,2)
                            p01 = "    " + format(k) + " = " + format(zrnd) + "<br /> \n"
                            inp_file.write(p01)
                
            k01 = "    " + "</div> ]]> </description> \n"    
            k02 = "    " + "<styleUrl>#s20</styleUrl> \n"
            k03 = "    " + "<Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" + str(slon) + "," + str(slat) + ",0.0000</coordinates></Point> \n"    
            k04 = "  " + "</Placemark> \n"    
            k05 = " \n"    
                
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
    
    # end polar grid cancer risk folder outputs
        k00 = "</Folder> \n"
        k01 = " \n"
        inp_file.write(k00)
        inp_file.write(k01)
    
    # start polar receptors TOSHI outputs   
        k01 = "<Folder> \n"    
        k02 = "  " + "<name>Polar TOSHI</name> \n"
        k03 = "  " + "<open>0</open> \n" 
        k04 = " \n"
        
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
        
        for loc, group in self.allpolar.groupby(["lat","lon"]):
            slat = loc[0]
            slon = loc[1]
            pg_dist = str(round(group.iloc[0]['distance'],0))
            pg_angle = str(round(group.iloc[0]['angle'],0))
            
            k01 = "  " + "<Placemark> \n"
            k02 = "    " + "<name>Polar Receptor Distance: " + pg_dist + " Angle: " + pg_angle  + " </name> \n"
            k03 = "    " + "<visibility>0</visibility> \n" 
            k04 = "    " + "<snippet></snippet> \n"
            k05 = "    " + "<description><![CDATA[<div align='center'><B> Polar Receptor</B> <br /> \n"
            k06 = "    " + "<B> Distance: " + pg_dist + " Angle: " + pg_angle + "</B> <br /> \n"
    # May need to change with David's polar_risk.xlsx file inputs. Change 'toshi' to Respiratory?        
            k07 = "    " + "<B> HEM4 Estimated Max TOSHI (" + str(group.iloc[0]['toshi']) + ") </B> <br /> \n"
            
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
            inp_file.write(k06)
            inp_file.write(k07)
            
            
            pgtothi = group.iloc[0]['total_hi']
            pgrndhi = round(pgtothi,2)
            k08 = "    " + "Total = " + str(pgrndhi) + "<br /><br /> \n"
            inp_file.write(k08)
            if pgrndhi > 0: 
                k09 = "    " + "<U> Top Pollutants Contributing to TOSHI </U> <br /> \n"
                inp_file.write(k09)
            
    # create dictionary to hold summed toshi of each pollutant        
                pghi_sum = {}        
                for index, row in group.iterrows():
                
                    #keys = pghi_sum.keys()
                    if row["pollutant"] not in pghi_sum:
                       pghi_sum[row["pollutant"]] = row["poll_hi"]
                       #inp_file.write(row["pollutant"])
                    else:
                        pol = pghi_sum[row["pollutant"]]
                        toshisum = row["poll_hi"] + pol
                        pghi_sum[row["pollutant"]] = toshisum  
                        
    #sort the dictionary by value 
                    sorted_pghi_sum = OrderedDict(sorted(pghi_sum.items(), key=itemgetter(1)))  
                    
    # check to make sure large enough value to keep
                    for k, v in sorted_pghi_sum.items():
                        if v > 0.005:
                            vrnd = round(v,2)
                            p01 = "    " + format(k) + " = " + format(vrnd) + "<br /> \n"
                            inp_file.write(p01)
                
            k01 = "    " + "</div> ]]> </description> \n"    
            k02 = "    " + "<styleUrl>#s20</styleUrl> \n"
            k03 = "    " + "<Point><altitudeMode>clampedToGround</altitudeMode><coordinates>" + str(slon) + "," + str(slat) + ",0.0000</coordinates></Point> \n"    
            k04 = "  " + "</Placemark> \n"    
            k05 = " \n"    
                
            inp_file.write(k01)
            inp_file.write(k02)
            inp_file.write(k03)
            inp_file.write(k04)
            inp_file.write(k05)
    
        k01 = "</Folder> \n"
        k02 = " \n"
        inp_file.write(k01)
        inp_file.write(k02)            
            
    # end polar grid TOSHI folder outputs 
    
    # Write MIR location
#        for index, row in self.mir.iterrows():
#            slon = row["lon"]
#            slat = row["lat"]
#            stype = row["parameter"]
#            svalue = row["value"]  
#              
#            if stype == 'Cancer risk':
#                if svalue > 0:
#                    k01 = "<Folder> \n"    
#                    k02 = "  " + "<name>MIR</name> \n"
#                    k03 = "  " + "<open>0</open> \n" 
#                    k04 = "  " + "<Placemark> \n"
#                    k05 = "    " + "<name> MIR receptor </name> \n"
#                    k06 = "    " + "<snippet></snippet> \n"
#                    k07 = "    " + "<description><![CDATA[<div align='center'><B> MIR Receptor</B> <br /> \n"
#                    k08 = "    " + "<B> Receptor type: " + row["rec_type"] + "</B> <br /> \n"
#                    k09 = "    " + "<B> Distance from facility (m): " + str(round(row["distance"],0)) + "</B> <br /> \n"
#                    k10 = "    " + "MIR (in a million) =  " + str(round(row["value"],2)) + "<br /><br /> \n"
#        
#                    inp_file.write(k01)
#                    inp_file.write(k02)
#                    inp_file.write(k03)
#                    inp_file.write(k04)
#                    inp_file.write(k05)
#                    inp_file.write(k06)
#                    inp_file.write(k07)
#                    inp_file.write(k08)
#                    inp_file.write(k09)
#                    inp_file.write(k10)
#                    
#                    k01 = "    " + "</div> ]]> </description> \n"    
#                    k02 = "    " + "<styleUrl>#mir</styleUrl> \n"
#                    k03 = "    " + "<Point><altitudeMode>relativeToGround</altitudeMode><coordinates>" + str(slon) + "," + str(slat) + ",100.0000</coordinates></Point> \n"    
#                    k04 = "  " + "</Placemark> \n"
#                    k05 = "</Folder> \n"
#            
#                    inp_file.write(k01)
#                    inp_file.write(k02)
#                    inp_file.write(k03)
#                    inp_file.write(k04)
#                    inp_file.write(k05)
#    
#                else:
#                    k01 = "<Folder> \n"    
#                    k02 = "  " + "<name>MIR is 0</name> \n"
#                    k03 = "  " + "<open>0</open> \n" 
#                    k04 = "  " + "<visibility>0</visibility> \n"
#                    k05 = "</Folder> \n"
#                    
#                    inp_file.write(k01)
#                    inp_file.write(k02)
#                    inp_file.write(k03)
#                    inp_file.write(k04)
#                    inp_file.write(k05)
#                    
    # end of MIR                
                    
    # end of file - close folder and document            
        
        k03 = "</Document> \n" 
        k04 = "</kml> \n"      
        
        
        inp_file.write(k03)
        inp_file.write(k04)
        
        return kmlfilename
    
    
    ########################################################################################################
    # Test write_kml function
    ########################################################################################################
    
    #                 , names=("fac_id","source_id","location_type","lon","lat","utmzone","source_type"
    #                           ,"lengthx","lengthy","angle","horzdim","vertdim","areavolrelhgt","stkht"
    #                           ,"stkdia","stkvel","stktemp","elev","x2","y2")
    #                  , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float,"lat":float
    #                  ,"utmzone":float,"source_type":str,"lengthx":float,"lengthy":float,"angle":float
    #                  ,"horzdim":float,"vertdim":float,"areavolrelhgt":float,"stkht":float,"stkdia":float
    #                  ,"stkvel":float,"stktemp":float,"elev":float,"x2":float,"y2":float})
    #
    #kmlfilename = write_kml(emislocs)
    #    
    #######################################################################################################
    # use excel file to subsitute for dbf file created from emislocs and other input files
    #######################################################################################################
    
    
    





                       
