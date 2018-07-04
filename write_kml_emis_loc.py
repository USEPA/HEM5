# -*- coding: utf-8 -*-
"""
Spyder Editor

Create text file to be used to create kml file.
@author: cgaertner
"""
#import pandas as pd

def write_kml_emis_loc(srcmap):
    
    kmlfilename = "kml_source_loc.txt"
    facidfilename = "facid_kml_source_loc.txt"
    inp_file = open(r"kml_source_loc.txt","w")
    fac_file = open(r"facid_kml_source_loc.txt","w")
    
    k01 = "<?xml version='1.0' encoding='UTF-8'?>  \n"
    k02 = '<kml xmlns="http://earth.google.com/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"> \n'
    k03 = "<Document> /n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    
# Documents section
    k01 = "  " + "<name><![CDATA[srcmap]]></name>  \n"
    k02 = "  " + "<open>1</open>  \n"
    k03 = "  " + "<Snippet maxLines='2'></Snippet> \n"
    k04 = "  " + "<description><![CDATA[Exported from HEM4]]></description> \n"
    k05 = "  " + "<Schema name='srcmap' id='srcmap_schema'> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    
    k01 = "    " + "<SimpleField type='string' name='Source_id'>  \n"
    k02 = "      " + "<displayName><![CDATA[Sourceid]]></displayName>  \n"
    k03 = "    " + "</SimpleField> \n"
    k04 = "  " + "</Schema> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    
    
    k01 = " \n"
    k02 = "  " + "<Style id='Areasrc'> \n"
    k03 = "    " + "<LineStyle> \n"
    k04 = "      " + "<color>ff000000</color>  \n"
    k05 = "      " + "<width>1</width>  \n" 
    k06 = "    " + "</LineStyle> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    
    k01 = "    " + "<PolyStyle> \n"
    k02 = "      " + "<outline>1</outline>  \n"
    k03 = "      " + "<fill>1</fill>  \n"
    k04 = "      " + "<color>7c8080ff</color>  \n"
    k05 = "    " + "</PolyStyle> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    
    k01 = "    " + "<BalloonStyle> \n"
    k02 = "      " + "<bgColor>ffffffff</bgColor>  \n"
    k03 = "      " + "<text>$[description]</text>  \n"
    k04 = "    " + "</BalloonStyle> \n"
    k05 = "  " + "</Style> \n"
    k06 = " \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    
    k01 = "<Style id='Ptsrc'> \n"
    k02 = "  " + "<IconStyle> \n"
    k03 = "    " + "<color>ff8080ff</color>  \n"
    k04 = "    " + "<Icon>  \n"
    k05 = "      " + "<href>drawCircle.png</href>  \n"
    k06 = "    " + "</Icon>  \n"
    k07 = "  " + "</IconStyle> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    
    k01 = "  " + "<LabelStyle> \n"
    k02 = "    " + "<color>00000000</color> \n"
    k03 = "  " + "</LabelStyle>  \n"
    k04 = "  " + "<BalloonStyle> \n"
    k05 = "    " + "<bgColor>ffffffff</bgColor>  \n"
    k06 = "    " + "<text>$[description]</text>  \n"
    k07 = "  " + "</BalloonStyle>  \n"
    k08 = "</Style> \n" 
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    inp_file.write(k08) 
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    fac_file.write(k08)
    
    # s20
    k01 = " \n"
    k02 = "<Style id='s20'> \n"
    k03 = "  " + "<IconStyle> \n"
    k04 = "    " + "<color>ff00ff00</color>  \n"
    k05 = "    " + "<Icon>  \n"
    k06 = "      " + "<href>drawCircle.png</href>  \n"
    k07 = "    " + "</Icon>  \n"
    k08 = "  " + "</IconStyle> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    inp_file.write(k08)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    fac_file.write(k08)
    
    k01 = "  " + "<LabelStyle> \n"
    k02 = "    " + "<color>00000000</color> \n"
    k03 = "  " + "</LabelStyle>  \n"
    k04 = "  " + "<BalloonStyle> \n"
    k05 = "    " + "<bgColor>ffffffff</bgColor>  \n"
    k06 = "    " + "<text>$[description]</text>  \n"
    k07 = "  " + "</BalloonStyle>  \n"
    k08 = "</Style> \n" 
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    inp_file.write(k08)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    fac_file.write(k08)
    
    # b20
    k01 = " \n"
    k02 = "<Style id='b20'> \n"
    k03 = "  " + "<IconStyle> \n"
    k04 = "    " + "<color>ff00ff00</color>  \n"
    k05 = "    " + "<Icon>  \n"
    k06 = "      " + "<href>drawRectangle.png</href>  \n"
    k07 = "    " + "</Icon>  \n"
    k08 = "  " + "</IconStyle> \n"
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    inp_file.write(k08)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    fac_file.write(k08)
    
    k01 = "  " + "<LabelStyle> \n"
    k02 = "    " + "<color>00000000</color> \n"
    k03 = "  " + "</LabelStyle>  \n"
    k04 = "  " + "<BalloonStyle> \n"
    k05 = "    " + "<bgColor>ffffffff</bgColor>  \n"
    k06 = "    " + "<text>$[description]</text>  \n"
    k07 = "  " + "</BalloonStyle>  \n"
    k08 = "</Style> \n" 
    inp_file.write(k01)
    inp_file.write(k02)
    inp_file.write(k03)
    inp_file.write(k04)
    inp_file.write(k05)
    inp_file.write(k06)
    inp_file.write(k07)
    inp_file.write(k08)
    
    fac_file.write(k01)
    fac_file.write(k02)
    fac_file.write(k03)
    fac_file.write(k04)
    fac_file.write(k05)
    fac_file.write(k06)
    fac_file.write(k07)
    fac_file.write(k08)
    
    # Read array to get facility id, source ids, source type and location parameters
    for facid, group in srcmap.groupby(["fac_id"]):
        fname = facid
        singlefacidfilename = fname + "_kml_source_loc.txt"
        
        # Facility ID
        k01 = " \n"
        k02 = "  " + "<Folder> \n"
        k03 = "    " + "<name>Facility " + fname + "</name> \n"
        k04 = "    " + "<open>0</open> \n"
        k05 = " \n"
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
        inp_file.write(k05)
        
        fac_file.write(k01)
        fac_file.write(k02)
        fac_file.write(k03)
        fac_file.write(k04)
        fac_file.write(k05)
        
    # create groups by source id and source type
    #src_df = srcmap.groupby(['source_id','src_type'])
        sub_map = srcmap.loc[srcmap.fac_id==facid]
        
        for name, group in sub_map.groupby(["source_id","source_type"]):
            sname = name[0]
            stype = name[1]
 
                # Emission sources
#                k01 = " \n"
#                k02 = "  " + "<Folder> \n"
#                k03 = "    " + "<name>Emission sources</name> \n"
#                k04 = "    " + "<open>0</open> \n"
#                k05 = " \n"
#                inp_file.write(k01)
#                inp_file.write(k02)
#                inp_file.write(k03)
#                inp_file.write(k04)
#                inp_file.write(k05)
                
    # Emission sources  Point, Capped, Horizontal 
    #        sstyle = "Ptsrc"     
            if stype == 'P' or stype == 'C' or stype == 'H':

                k01 = "  " + "<Placemark> \n"
                k02 = "    " + "<name><![CDATA[" + sname + "]]></name> \n"
                k03 = "    " + "<snippet></snippet> \n"   
                k04 = "    " + "<description><![CDATA[<div align='center'>" + sname + "</div>]]></description> \n"
                k05 = "    " + "<styleUrl>#Ptsrc</styleUrl> \n"
                k06 = "    " + "<Point><altitudeMode>relativeToGround</altitudeMode> \n"
                k07 = "      " + "<coordinates>" + str(group.iloc[0]['lon']) + "," + str(group.iloc[0]['lat']) + ",0.0</coordinates></Point> \n"
                k08 = "  " + "</Placemark> \n"
                k09 = " \n"
            
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                inp_file.write(k05)
                inp_file.write(k06)
                inp_file.write(k07)
                inp_file.write(k08)
                inp_file.write(k09)
                
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
                fac_file.write(k06)
                fac_file.write(k07)
                fac_file.write(k08)
                fac_file.write(k09)
        
        # Area, Volume or Polygon 
        #   sstyle = "Areasrc"                
            elif stype == 'A' or stype == 'V' or stype == 'I':
            
                k01 = "  " + "<Placemark> \n"
                k02 = "    " + "<name><![CDATA[" + sname + "]]></name> \n"
                k03 = "    " + "<snippet maxLines='2'></snippet> \n"   
                k04 = "    " + "<description><![CDATA[<div align='center'>" + sname + "</div>]]></description> \n"        
                k05 = "    " + "<styleUrl>#Areasrc</styleUrl> \n"
                k06 = "      " + "<ExtendedData> \n"
                k07 = "      " + "<SchemaData schemaUrl='#Source_map_schema'> \n"
                k08 = "        " + "<SimpleData name='Sourceid'><![CDATA[" + sname + "]]></SimpleData> \n"
                k09 = "      " + "</SchemaData> \n"
                k10 = "      " + "</ExtendedData> \n"
            
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
            
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
                fac_file.write(k06)
                fac_file.write(k07)
                fac_file.write(k08)
                fac_file.write(k09)
                fac_file.write(k10)
            
                # Polygon
                k01 = "    " + "<Polygon> \n"
                k02 = "      " + "<extrude>0</extrude> \n"
                k03 = "      " + "<altitudeMode>clampedToGround</altitudeMode> \n"
                k04 = "      " + "<outerBoundaryIs> \n"
                k05 = "      " + "<LinearRing> \n"
                k06 = "        " + "<altitudeMode>clampedToGround</altitudeMode> \n"
                k07 = "        " + "<tessellate>1</tessellate> \n"
                k08 = "        " + "<coordinates> \n"
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                inp_file.write(k05)
                inp_file.write(k06)
                inp_file.write(k07)
                inp_file.write(k08)
            
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
                fac_file.write(k06)
                fac_file.write(k07)
                fac_file.write(k08)
            
            # lon, lat loop
            # for sname == row["source_id"]
 # Write area source coordinates 
 #          sname = name
  
                for index, row in group.iterrows():    
                
                    co1 = "          " + str(row["lon"]) + "," + str(row["lat"]) + ",0 \n"
                    inp_file.write(co1)
                # go to next record
                k01 = "        " + "</coordinates> \n"
                k02 = "      " + "</LinearRing> \n"
                k03 = "      " + "</outerBoundaryIs> \n"
                k04 = "    " + "</Polygon> \n"
                k05 = "  " + "</Placemark> \n"
                k06 = " \n"
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                inp_file.write(k05)
                inp_file.write(k06)
            
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
            
        # Line or Bouyant Line                
            elif stype == 'N' or stype == 'B':
            
                k01 = "  " + "<Placemark> \n"
                k02 = "    " + "<name><![CDATA[" + sname + "]]></name> \n"
                k03 = "    " + "<snippet></snippet> \n"   
                k04 = "    " + "<description><![CDATA[<div align='center'>" + sname + "</div>]]></description> \n"        
                k05 = "    " + "<styleUrl>#Linesrc</styleUrl> \n"
                k06 = "    " + "<Style> \n"
                k07 = "      " + "<LineStyle> \n"
        # Find correct column for length of line - area 8/23/17   
                k08 = "        " + "<gx:physicalWidth>" + str(group.iloc[0]['line_width']) + "</gx:physicalWidth> \n"
                k09 = "      " + "<outline>1</outline> \n"
                inp_file.write(k01)
                inp_file.write(k02)
                inp_file.write(k03)
                inp_file.write(k04)
                inp_file.write(k05)
                inp_file.write(k06)
                inp_file.write(k07)
                inp_file.write(k08)
                inp_file.write(k09)
                
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
                fac_file.write(k06)
                fac_file.write(k07)
                fac_file.write(k08)
                fac_file.write(k09)
                
                k01 = "      " + "<fill>1</fill> \n" 
                k02 = "      " + "<color>7c8080ff</color> \n" 
                k03 = "      " + "</LineStyle> \n" 
                k04 = "    " + "</Style> \n"
                k05 = "    " + "<LineString> \n"
                k06 = "      " + "<altitudeMode>clampedToGround</altitudeMode> \n"
                k07 = "        " + "<coordinates>" + str(group.iloc[0]['lon']) + "," + str(group.iloc[0]['lat']) + str(group.iloc[0]['lon_x2']) + "," + str(group.iloc[0]['lat_y2']) + "</coordinates> \n"
                k08 = "    " + "</LineString> \n"
                k09 = "  " + "</Placemark> \n"
                k10 = "  \n"
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
                
                fac_file.write(k01)
                fac_file.write(k02)
                fac_file.write(k03)
                fac_file.write(k04)
                fac_file.write(k05)
                fac_file.write(k06)
                fac_file.write(k07)
                fac_file.write(k08)
                fac_file.write(k09)
                fac_file.write(k10)
                
        k01 = "  " + "</Folder> \n"
        inp_file.write(k01)

# Rename single facility source locations to have facid as prefix for name        
        

        
 # end of file - close folder and document            
    k03 = "</Document> \n" 
    k04 = "</kml> \n"      
    inp_file.write(k03)
    inp_file.write(k04)
    
    fac_file.write(k03)
    fac_file.write(k04)
    
    fac_file.rename(singlefacidfilename)  
    close() 
    
    return kmlfilename, facidfilename


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

#srcmap = pd.read_excel(r"C:\python\HEM4\Inputs\source_map_w_line.xlsx"
#                   , names=("utm_e","area","point","census","lat","lon","distance","min_dist"
#                           ,"bearing","elev","population","source_id","src_height","src_type","lat2","lon2")
#                   , converters={"utm_e":float,"area":float,"point":float,"census":float,"lat":float,"lon":float
#                           ,"distance":float,"min_dist":float,"bearing":float,"elev":float,"population":float
#                           ,"source_id":str,"src_height":float,"src_type":str,"lat2":float,"lon2":float})
#
#     
#fac_center = pd.read_excel(r"C:\python\HEM4\Inputs\plant_cen.xlsx"
#                       , names=("lat","lon")
#                       , converters={"lat":float,"lon":float})
#                       
#
##ringdist = pd.read_excel(r"C:\python\HEM4\Inputs\ringdist.xlsx"
##                       , names=("distance","angle","lat","lon","conc_tot","pollutant","poll_conc")
##                       , converters={"distance":float,"angle":float,"lat":float,"lon":float
##                                ,"conc_tot":float,"pollutant":str,"poll_conc":float})
#
#allpolar = pd.read_excel(r"C:\python\HEM4\Inputs\all_polar_receptors2.xlsx"
#                       , names=("source_id", "risk","pollutant","distance","angle","sector","ring","lat","lon"
#                                ,"toshi","total_hi","poll_hi")
#                       , converters={"source_id":str,"risk":float,"pollutant":str,"distance":float,"angle":float
#                               ,"sector":float,"ring":float,"lat":float,"lon":float,"toshi":str
#                               ,"total_hi":float,"poll_hi":float})
#    
#allinner = pd.read_excel(r"C:\python\HEM4\Inputs\all_inner_receptors.xlsx"
#                       , names=("lat","lon","source_id", "risk","pollutant","population","fips","block","block_risk"
#                                ,"toshi","total_hi","poll_hi")
#                       , converters={"lat":float,"lon":float,"source_id":str,"risk":float,"pollutant":str
#                               ,"population":float,"fips":str,"block":str,"block_risk":float,"toshi":str
#                               ,"total_hi":float,"poll_hi":float})
#
#mir = pd.read_excel(r"C:\python\HEM4\Inputs\maximum_indiv_risks.xlsx"
#                   , names=("parameter","value","population","distance","angle","elevation"
#                           ,"fips","block","lat","lon","rec_type")
#                   , converters={"parameter":str,"value":float,"population":float,"distance":float,"angle":float
#                           ,"elevation":float,"fips":str,"block":str,"lat":float,"lon":float,"rec_type":str})
#                           
#kmlfilename = write_kml(srcmap)






                       
