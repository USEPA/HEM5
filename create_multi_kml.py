# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:56:59 2017

@author: sfudge
"""

import pandas as pd
import numpy as np
#import os
from shutil import copyfile
import ll2utm
import utm2ll

class multi_kml():
    
    def __init__(self, multiemisloc_df, multipoly_df, multibuoy_df):
        
        self.multiemisloc_df = multiemisloc_df
        self.multipoly_df = multipoly_df
        self.multibuoy_df = multibuoy_df
  
      
#%% zone2use function

    def zone2use(self,el_df):
    
    # Set a common zone
    #    utmzone = np.nan_to_num(el_df["utmzone"].min(axis=0))
        min_utmzu = np.nan_to_num(el_df["utmzone"].loc[el_df["location_type"] == "U"].min(axis=0))
        utmzl_df = el_df[["lon"]].loc[el_df["location_type"] == "L"]
        utmzl_df["z"] = ((utmzl_df["lon"]+180)/6 + 1).astype(int)
        min_utmzl = np.nan_to_num(utmzl_df["z"].min(axis=0))
        if min_utmzu == 0:
            utmzone = min_utmzl
        else:
            utmzone = min(min_utmzu, min_utmzl)
    
        return utmzone


#%% function to set the width of a line or buoyant line source

    def set_width(self, row, buoy_linwid):
        if row["source_type"] == "N":
            linwid = row["lengthx"]
        elif row["source_type"] == "B":
            linwid = buoy_linwid["avglin_wid"].iloc[0]
        else:
            linwid = 0
        
        return linwid



#%% create the source map dataframe needed for the source location KML

    def create_sourcemap(self):
    
        # Create an array of all facility ids
        faclist = self.multiemisloc_df.fac_id.unique()
        
        # Loop over all facility ids and populate the sourcemap dataframe
        
        source_map = pd.DataFrame()
        
        for row in faclist:
                
            # Emission location info for one facility. Keep certain columns.
            emislocs = self.multiemisloc_df.loc[self.multiemisloc_df.fac_id == row][["fac_id","source_id","source_type",
                                         "lon","lat","utmzone","x2","y2","location_type","lengthx"]]
             
            
            # If facility has a polygon source, get the vertices for this facility and append to emislocs
            if any(emislocs.source_type == "I") == True:        
                polyver = self.multipoly_df.loc[self.multipoly_df.fac_id == row][["fac_id","source_id",
                                         "lon","lat","utmzone","location_type"]]     
                # Assign source_type
                polyver["source_type"] = "I"
                # remove the I source_type rows from emislocs before appending polyver to avoid duplicate rows
                emislocs = emislocs[emislocs.source_type != "I"]
                # Append polyver to emislocs
                emislocs = emislocs.append(polyver)
              
            # If facility has a buoyant line source, get the line width
            if any(emislocs.source_type == "B") == True:
                buoy_linwid = self.multibuoy_df.loc[self.multibuoy_df.fac_id == row][["fac_id","avglin_wid"]]
            else:
                buoy_linwid = pd.DataFrame()
            
            # Create a line width column for line and buoyant line sources
            emislocs["line_width"] = emislocs.apply(lambda row: self.set_width(row,buoy_linwid), axis=1)
            
            
            # Replace NaN with blank or 0 in emislocs
            emislocs = emislocs.fillna({"utmzone":0, "source_type":"", "x2":0, "y2":0})
        
            # Determine the common utm zone to use for this facility
            facutmzone = self.zone2use(emislocs)
            
            # Convert all lat/lon coordinates to UTM and UTM coordinates to lat/lon
        
            slat = emislocs["lat"].values
            slon = emislocs["lon"].values
            sutmzone = emislocs["utmzone"].values
         
            # First compute lat/lon coors using whatever zone was provided
            alat, alon = utm2ll.utm2ll(slat, slon, sutmzone)
            emislocs["lat"] = alat.tolist()
            emislocs["lon"] = alon.tolist()
        
            # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
            autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
            emislocs["utme"] = autme.tolist()
            emislocs["utmn"] = autmn.tolist()
            emislocs["utmzone"] = autmz.tolist()
        
        
            # Compute UTM of any x2 and y2 coordinates and add to emislocs
            slat = emislocs["y2"].values
            slon = emislocs["x2"].values
            sutmzone = emislocs["utmzone"].values
        
            alat, alon = utm2ll.utm2ll(slat, slon, sutmzone)
            emislocs["lat_y2"] = alat.tolist()
            emislocs["lon_x2"] = alon.tolist()
            
            sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
            autmn, autme, autmz = ll2utm.ll2utm(slat, slon, sutmzone)
            emislocs["utme_x2"] = autme.tolist()
            emislocs["utmn_y2"] = autmn.tolist()
            
            # Append to source_map
            source_map = source_map.append(emislocs)
            
        return source_map
    
#%% Create KML of all sources

    def write_kml_emis_loc(self, srcmap):
        
        kmlfilename = "category_source_loc.kml"
        facidfilename = "facid_kml_source_loc.txt"
        headerfilename = "working_kml/Header_kml_file.kml"
        inp_file = open(r"kml_source_loc.txt","w")
#        fac_file = open(r"facid_kml_source_loc.txt","w")
        
        k01 = "<?xml version='1.0' encoding='UTF-8'?>  \n"
        k02 = '<kml xmlns="http://earth.google.com/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"> \n'
        k03 = "<Document> /n"
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
        
        k01 = "    " + "<SimpleField type='string' name='Source_id'>  \n"
        k02 = "      " + "<displayName><![CDATA[Sourceid]]></displayName>  \n"
        k03 = "    " + "</SimpleField> \n"
        k04 = "  " + "</Schema> \n"
        inp_file.write(k01)
        inp_file.write(k02)
        inp_file.write(k03)
        inp_file.write(k04)
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
        
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
#        fac_file.write(k08)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
#        fac_file.write(k08)
        
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
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
#        fac_file.write(k08)
        
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
        
#  u20 - user receptor style
        k01 = " \n"
        k02 = "<Style id='u20'> \n"
        k03 = "  " + "<IconStyle> \n"
        k04 = "    " + "<color>ff00ff00</color>  \n"
        k05 = "    " + "<Icon>  \n"
        k06 = "      " + "<href>drawRectangle_ur.png</href>  \n"
        k07 = "    " + "</Icon>  \n"
        k08 = "  " + "</IconStyle> \n"
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
#        fac_file.write(k08)
        
        k01 = "  " + "<LabelStyle> \n"
        k02 = "    " + "<color>00000000</color> \n"
        k03 = "  " + "</LabelStyle>  \n"
        k04 = "  " + "<BalloonStyle> \n"
        k05 = "    " + "<bgColor>ffffffff</bgColor>  \n"
        k06 = "    " + "<text>$[description]</text>  \n"
        k07 = "  " + "</BalloonStyle>  \n"
        k08 = "</Style> \n" 
        
#        fac_file.write(k01)
#        fac_file.write(k02)
#        fac_file.write(k03)
#        fac_file.write(k04)
#        fac_file.write(k05)
#        fac_file.write(k06)
#        fac_file.write(k07)
#        fac_file.write(k08)
                

# Fac_id - create source file for each facility         
        # Read array to get facility id, source ids, source type and location parameters
        for facid, group in srcmap.groupby(["fac_id"]):
            fname = str(facid)
            singlefacidfilename = "working_kml/fac_" + fname + "_source.kml"
            copyfile(headerfilename,singlefacidfilename)
            fac_file = open(singlefacidfilename,"a")
            
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
            
        # Emission sources for single facility kmz files
            f01 = " \n"
            f02 = "  " + "<Folder> \n"
            f03 = "    " + "<name>Emission sources</name> \n"
            f04 = "    " + "<open>0</open> \n"
            f05 = " \n"
            fac_file.write(f01)
            fac_file.write(f02)
            fac_file.write(f03)
            fac_file.write(f04)
            fac_file.write(f05)
            
        # create groups by source id and source type
        #src_df = srcmap.groupby(['source_id','src_type'])
            sub_map = srcmap.loc[srcmap.fac_id==facid]
            
            for name, group in sub_map.groupby(["source_id","source_type"]):
                sname = name[0]
                stype = name[1]
     
                     
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
            
            fac_file.write(k01)
            
          
     # end of file - close folder and document            
            k03 = "</Document> \n" 
            k04 = "</kml> \n"      
#            inp_file.write(k03)
#            inp_file.write(k04)

# rename kml with single facility and place in working folder
        
            fac_file.write(k03)
            fac_file.write(k04)
 
# example of assigning a directory to a file
#  singlefacidfilename = os.path.join("working_kml", "fac1_source_loc.kml")        
#        os.rename(facidfilename,singlefacidfilename)
# change save       
            fac_file.close()  
#        close() 

        k03 = "</Document> \n" 
        k04 = "</kml> \n"      
        inp_file.write(k03)
        inp_file.write(k04)
        
        return kmlfilename, facidfilename    