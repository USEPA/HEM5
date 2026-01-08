# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:56:59 2017
@author: sfudge, cstolte
"""
import pandas as pd
import numpy as np
from fastkml import kml, SchemaData, Data, SimpleField, Placemark
import fastkml
# from fastkml.kml import KML, Document, Placemark, Schema, SimpleField
# from fastkml.geometry import Geometry, Point, Polygon
from pygeoif import geometry
from fastkml import ExtendedData
from fastkml.enums import AltitudeMode
from fastkml.styles import LineStyle, PolyStyle, IconStyle, LabelStyle, BalloonStyle, StyleUrl, Style
from fastkml.geometry import create_kml_geometry
from shapely.geometry import LineString, LinearRing
from xml.sax.saxutils import unescape
from operator import itemgetter
from collections import OrderedDict
import zipfile
from os.path import basename
import math
import os
from itertools import combinations
import traceback


from com.sca.hem4.support.UTM import UTM


class KMLWriter_for_Merger():
    """
    Creates KMZ files suitable for viewing in Google Earth.
    """

    def __init__(self, rundir, faclist_df, buoyant_df, emisloc_df, polygon_df):
        self.ns = "{http://www.opengis.net/kml/2.2}"
        self.rundir = rundir
        self.faclist_df = faclist_df
        self.buoyant_df = buoyant_df
        self.emisloc_df = emisloc_df
        self.polygon_df = polygon_df

    def write_kml_emis_loc(self):
        """
        Create KMZ of all sources from all facilities. 
        """            
 
        try:
            
            # Define the name of the output kml file
            allkml_fname = os.path.join(self.rundir, "AllFacility_source_locations.kml")
            
            # Create a dataframe of emission source locations for all facilities being modeled
            srcmap = self.create_sourcemap()
            
            # Define kml object
            kml_source_loc = kml.KML()
    
            document = kml.Document(ns=self.ns, id='emisloc', name='srcmap', description='Exported from HEM')
            document.isopen = 1
    
            # Schema
            schema = fastkml.data.Schema(id="srcmap_schema", name="srcmap")
            schema.fields.append(SimpleField(name="Sourceid", type="string"))
                    
            # schema = fastkml.data.Schema(ns=self.ns, id="srcmap_schema", name="srcmap")
            # schema.append("string", "Source_id", "Sourceid")
             
            document.append(schema)
    
            # Areasrc style...
            document.append(self.getAreaSrcStyle())
    
            # Ptsrc style...
            document.append(self.getPtSrcStyle())
    
            # center style...
            document.append(self.getCenterStyle())
            
            # Iterate over srcmap DF to get facility id, source ids, source type and location parameters
            for facid, group in srcmap.groupby("fac_id"):
                
                # Subset srcmap to this facility
                sub_map = srcmap.loc[srcmap.fac_id==facid]
    
                # Determine the center of the facility. If provided by the user, use it. Otherwise compute an
                # average from the emission source locations (lat/lons)
                fcenter = str(self.faclist_df[self.faclist_df['fac_id']==facid]['fac_center'].iloc[0])
                if fcenter != "" and fcenter != "nan":
                                        
                    # User supplied
                    components = fcenter.split(',')
                    if components[0] == "L":
                        avglat = float(components[1])
                        avglon = float(components[2])
                    else:
                        ceny = int(float(components[1]))
                        cenx = int(float(components[2]))   
                        zone = components[3].strip()
                        avglat, avglon = UTM.utm2ll(ceny, cenx, zone)
    
                else:
    
                    # Not supplied, compute average                
                    faclatlons = sub_map[['lat', 'lon']].values.tolist()
                    latlon_array = np.array(faclatlons)
                    lats = latlon_array[:,0:1]
                    lons = latlon_array[:,1:2]
                    if (len(np.unique(lats)) > 1) or (len(np.unique(lons)) > 1): #more than one source location
                        maxdist = 0.0
                        for pair in combinations(faclatlons, 2):
                            firstpair = tuple(pair[0])
                            secondpair = tuple(pair[1])
                            d = self.distance(firstpair, secondpair)
                            if d > maxdist:
                                maxdist = d
                                maxpair = pair
                        avglat, avglon = self.midpoint(maxpair[0], maxpair[1])
                                        
                    else:
                        avglat = latlon_array[0,0]
                        avglon = latlon_array[0,1]
                
                # Setup an Emission Sources folder for this facility
                name_str = "Facility " + facid + " Emission sources"
                es_folder = kml.Folder(ns=self.ns, name=name_str)
    
                # Facility center placemark
                point = geometry.Point(avglon, avglat, 0.0)
                kml_geometry = create_kml_geometry(
                        geometry=point,
                        altitude_mode=AltitudeMode.relative_to_ground,
                    )
                style_url_ref = StyleUrl(url="#center")
                
                placemark = kml.Placemark(ns=self.ns, name="Facility center",
                                          description=("<div align='center'>Center of facility " +
                                                            facid + " </div>"),
                                          style_url=style_url_ref, 
                                          kml_geometry=kml_geometry)
                es_folder.append(placemark)
     
                         
                for name, group in sub_map.groupby(["source_id","source_type"]):
                    sname = name[0]
                    stype = name[1]
    
                    # Emission sources  Point, Capped, Horizontal
                    if stype == 'P' or stype == 'C' or stype == 'H':
    
                        point = geometry.Point(group.iloc[0]['lon'], group.iloc[0]['lat'], 0.0)
                        kml_geometry = create_kml_geometry(
                                geometry=point,
                                altitude_mode=AltitudeMode.relative_to_ground,
                            )
                        style_url_ref = StyleUrl(url="#Ptsrc")
    
                        placemark = kml.Placemark(ns=self.ns, name=sname,
                                                  description=("<div align='center'>" + sname + "</div>"),
                                                  style_url=style_url_ref, 
                                                  kml_geometry=kml_geometry)
                        es_folder.append(placemark)
    
                    # Area, Volume or Polygon
                    elif stype == 'A' or stype == 'V' or stype == 'I':
                                                                
                        simpleData = Data(name="SourceId", value=sname)
                        data = [simpleData]
                        schemaData = SchemaData(ns=self.ns, schema_url="#Source_map_schema", data=data)
                        elements = [schemaData]
                        extended_data = ExtendedData(ns=self.ns, elements=elements)
    
                        latlons = []
                        for index, row in group.iterrows():
                            coord = (row["lon"], row["lat"], 0)
                            latlons.append(coord)
    
                        linearRing = LinearRing(coordinates=latlons)
                        polygon = geometry.Polygon(shell=linearRing.coords)
                        kml_geometry = create_kml_geometry(
                                geometry=polygon,
                                altitude_mode=AltitudeMode.clamp_to_ground,
                            )
                        style_url_ref = StyleUrl(url="#Areasrc")
                        
                        placemark = kml.Placemark(ns=self.ns, name=sname,
                                                  description=("<div align='center'>" + sname + "</div>"),
                                                  style_url=style_url_ref, 
                                                  kml_geometry=kml_geometry,
                                                  extended_data=extended_data)
                        es_folder.append(placemark)
    
                    # Line or Bouyant Line
                    elif stype == 'N' or stype == 'B':
     
                        ls_style = Style(ns=self.ns, id='linesrc',
                                    styles = 
                                    [LineStyle(ns=self.ns, width=group.iloc[0]['line_width'], color="7c8080ff")])
     
                        # line string style...
                        document.append(ls_style)
                        
                        lineString = LineString([(group.iloc[0]['lon'], group.iloc[0]['lat']), (group.iloc[0]['lon_x2'],
                                                group.iloc[0]['lat_y2'])])
                        kml_geometry = create_kml_geometry(
                                geometry=lineString,
                                altitude_mode=AltitudeMode.clamp_to_ground,
                            )
                        style_url_ref = StyleUrl(url="#Linesrc")
    
                        placemark = kml.Placemark(ns=self.ns, name=sname,
                                                  description=("<div align='center'>" + sname + "</div>"),
                                                  style_url=style_url_ref, 
                                                  kml_geometry=kml_geometry)
                        es_folder.append(placemark)
    
                # Append emission source folder for this facility
                document.append(es_folder)
            
    
            # Finished
            kml_source_loc.append(document)
            # Write the KML file
            self.writeToFile(allkml_fname, kml_source_loc)
            
            # Create KMZ file
            kmztype = 'allsources'
            allkmz_fname = allkml_fname.replace('.kml', '.kmz')
            self.createKMZ(kmztype, allkml_fname, allkmz_fname)

        except Exception as e:
            print("An error occurred:")
            traceback.print_exc()
            raise ValueError(str(e))
        
    def writeToFile(self, filename, kml):
        """
        Write a KML instance to a file.
        :param filename:
        :param kml: a fastKml KML instance
        """
        file = open(filename, "w")
        
        pretty = kml.to_string(prettyprint=True)
        usingPhysicalWidth = self.usePhysicalWidth(pretty)
        file.write(unescape(usingPhysicalWidth))
        file.close()

    # Currently fastkml does not implement the gx extension types, but we want to specify a physical width
    # instead of a pixel width. Therefore we are falling back on some hackery to replace the generated
    # <width> tags with <gx:physicalWidth> tags.
    def usePhysicalWidth(self, input):

        # First add the gx namespace to the KML element
        defaultNS = 'xmlns="http://www.opengis.net/kml/2.2"'
        gxNS = 'xmlns:gx="http://www.google.com/kml/ext/2.2"'

        # ...then, replace widths with physicalWidths
        input = input.replace(defaultNS, defaultNS + " " + gxNS)
        input = input.replace('<width>', '<gx:physicalWidth>')
        input = input.replace('</width>', '</gx:physicalWidth>')

        return input

    def createKMZ(self, ftype, kmlfname, kmzfname):
        """
        Zip a KML file into a KMZ file.
        :param ftype: type of KML to zip, either all sources or facility risk
        :param kmlname: KML filename
        :param kmzname: KMZ filename
        """
        if ftype == 'allsources':
            zf = zipfile.ZipFile(kmzfname, mode='w')
            zf.write(kmlfname, basename(kmlfname))
            zf.write('resources/drawCircle.png', 'drawCircle.png')
            zf.write('resources/drawCenter.png', 'drawCenter.png')
            zf.close()
        else:
            zf = zipfile.ZipFile(kmzfname, mode='w')
            zf.write(kmlfname, basename(kmlfname))
            zf.write('resources/drawCircle.png', 'drawCircle.png')
            zf.write('resources/drawRectangle.png', 'drawRectangle.png')
            zf.write('resources/drawRectangle_ur.png', 'drawRectangle_ur.png')
            zf.write('resources/drawCenter.png', 'drawCenter.png')
            zf.write('resources/drawCross.png', 'drawCross.png')
            zf.close()
        
        # Delete the KML file
        os.remove(kmlfname)
            
            
    def set_width(self, row, buoy_linwid):
        """
        Set the width of a line or buoyant line source.
        :param row:
        :param buoy_linwid:
        :return: line width
        """
        if row["source_type"] == "N":
            linwid = row["lengthx"]
        elif row["source_type"] == "B":
            linwid = buoy_linwid["avglin_wid"].iloc[0]
        else:
            linwid = 0

        return linwid

    def distance(self, origin, destination):
        """
        Compute the distance in km between two pairs of lat/lons
        :param origin: first pair of lat/lon (tuple)
        :param destination: second pair of lat/lon (tuple)
        :return: distance in km
        """
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371 # earth radius in km

        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
        
        return d

    def midpoint(self, p1, p2):
        """
        Compute the midpoint between two pairs of lat/lons
        :param p1: first lat/lon
        :param p2: second lat/lon
        :return: lat/lon of midpoint
        """
        lat1, lon1 = p1
        lat2, lon2 = p2
        lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
        dlon = lon2 - lon1
        dx = math.cos(lat2) * math.cos(dlon)
        dy = math.cos(lat2) * math.sin(dlon)
        lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), math.sqrt((math.cos(lat1) + dx) * (math.cos(lat1) + dx) + dy * dy))
        lon3 = lon1 + math.atan2(dy, math.cos(lat1) + dx)
        return(math.degrees(lat3), math.degrees(lon3))

    def create_sourcemap(self):
        """
        Create the source map dataframe needed for the source location KML.
        :return: dataframe of emission locations
        """
        # Create an array of all facility ids being modeled
        faclist = self.faclist_df['fac_id'].values

        # Loop over all facility ids and populate the sourcemap dataframe
        source_map = pd.DataFrame()

        for row in faclist:

            # Emission location info for one facility. Keep certain columns.
            emislocs = self.emisloc_df.loc[self.emisloc_df['fac_id'] == row]
            [["fac_id","source_id","source_type","lon","lat","utmzone","x2","y2",
              "location_type","lengthx","lengthy","angle"]].copy()
            
            # If facility has a polygon source, get the vertices for this facility and append to emislocs
            if any(emislocs.source_type == "I") == True:
                polyver = self.polygon_df.loc[self.polygon_df['fac_id'] == row]
                [["fac_id","source_id","lon","lat","utmzone","location_type"]].copy()
                # Assign source_type
                polyver["source_type"] = "I"
                # remove the I source_type rows from emislocs before appending polyver to avoid duplicate rows
                emislocs = emislocs[emislocs.source_type != "I"].copy()
                # Append polyver to emislocs
                emislocs = pd.concat([emislocs, polyver])

            # If facility has a buoyant line source, get the line width
            if any(emislocs.source_type == "B") == True:
                buoy_linwid = self.buoyant_df.loc[self.buoyant_df['fac_id'] == row][['fac_id','avglin_wid']]
            else:
                buoy_linwid = pd.DataFrame()

            # Create a line width column for line and buoyant line sources
            emislocs["line_width"] = emislocs.apply(lambda row: self.set_width(row,buoy_linwid), axis=1)

            # Replace NaN with blank or 0 in emislocs. Default utmzone to 0N.
            emislocs = emislocs.fillna({"utmzone":'0N', "source_type":"", "x2":0, "y2":0})

            # Determine the common utm zone to use for this facility and the hemisphere
            facutmzonenum, hemi = UTM.zone2use(emislocs)
            facutmzonestr = str(facutmzonenum) + hemi


            # Compute lat/lon of any user supplied UTM coordinates
            emislocs[["lat", "lon"]] = emislocs.apply(lambda row: UTM.utm2ll(row["lat"],row["lon"],row["utmzone"]) 
                               if row['location_type']=='U' else [row["lat"],row["lon"]], result_type="expand", axis=1)

            # Next compute UTM coordinates using the common zone
            emislocs[["utmn", "utme"]] = emislocs.apply(lambda row: UTM.ll2utm_alt(row["lat"],row["lon"],facutmzonenum,hemi)
                               , result_type="expand", axis=1)

            # Compute lat/lon of any x2 and y2 coordinates that were supplied as UTM
            emislocs[['lat_y2', 'lon_x2']] = emislocs.apply(lambda row: UTM.utm2ll(row["y2"],row["x2"],row["utmzone"]) 
                              if row['location_type']=='U' else [row["y2"],row["x2"]], result_type="expand", axis=1)
            
            # Compute UTM coordinates of lat_x2 and lon_y2 using the common zone
            emislocs[['utmn_y2', 'utme_x2']] = emislocs.apply(lambda row: UTM.ll2utm_alt(row["lat_y2"],row["lon_x2"],facutmzonenum,hemi)
                              , result_type="expand", axis=1)

            # Pull out any area/volume sources and create vertices of each corner
            areavol = emislocs[(emislocs.source_type=="A") | (emislocs.source_type=="V")]

            if areavol.empty == False:
                new_rows = []
                for index, row in areavol.iterrows():                    
                    newrow = row.copy()
                    if row["source_type"] == "A":
                        # Area sources
                        radangle = np.radians(row["angle"])
                        new_rows.append(newrow.tolist())  # vertex 1
                        newrow["utme"] = row["utme"] + row["lengthx"] * np.cos(radangle)
                        newrow["utmn"] = row["utmn"] - row["lengthx"] * np.sin(radangle)
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 2
                        newrow["utme"] = row["utme"] + row["lengthx"] * np.cos(radangle) \
                                                        + row["lengthy"] * np.sin(radangle)
                        newrow["utmn"] = row["utmn"] - row["lengthx"] * np.sin(radangle) \
                                                        + row["lengthy"] * np.cos(radangle)
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 3
                        newrow["utme"] = row["utme"] + row["lengthy"] * np.sin(radangle)
                        newrow["utmn"] = row["utmn"] + row["lengthy"] * np.cos(radangle)
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 4
                        newrow["utme"] = row["utme"]
                        newrow["utmn"] = row["utmn"]
                        newrow["lat"] = row["lat"]
                        newrow["lon"] = row["lon"]
                        new_rows.append(newrow.tolist())  # repeat vertex 1
                    else:
                        # Volume sources
                        newrow["utme"] = row["utme"] - row["horzdim"]/2
                        newrow["utmn"] = row["utmn"] - row["horzdim"]/2
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 1
                        newrow["utme"] = row["utme"] + row["horzdim"]/2
                        newrow["utmn"] = row["utmn"] - row["horzdim"]/2
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 2
                        newrow["utme"] = row["utme"] + row["horzdim"]/2
                        newrow["utmn"] = row["utmn"] + row["horzdim"]/2
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 3
                        newrow["utme"] = row["utme"] - row["horzdim"]/2
                        newrow["utmn"] = row["utmn"] + row["horzdim"]/2
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # vertex 4
                        newrow["utme"] = row["utme"] - row["horzdim"]/2
                        newrow["utmn"] = row["utmn"] - row["horzdim"]/2
                        latitude, longitude = UTM.utm2ll(newrow["utmn"],newrow["utme"],facutmzonestr)
                        newrow["lat"] = latitude
                        newrow["lon"] = longitude
                        new_rows.append(newrow.tolist())  # repeat vertex 1
                
                # Remove the area/volume rows from emislocs and append the area/volume vertices list
                emislocs = emislocs[(emislocs.source_type != "A") & (emislocs.source_type != "V")]
                newrows_df = pd.DataFrame(new_rows, columns=emislocs.columns)
                emislocs = pd.concat([emislocs, newrows_df]).reset_index()
                            
            # Append to source_map
            source_map = pd.concat([source_map, emislocs])

        return source_map


    
    def createDocumentWithHeader(self):
        """
        Create a KML Document object with preset styles and schema.
        :return: the Document instance
        """
        document = kml.Document(ns=self.ns, name='srcmap', description='Exported from HEM')
        document.isopen = 1

        # Schema
        schema = fastkml.data.Schema(ns=self.ns, id="srcmap_schema", name="srcmap")
        schema.fields.append(SimpleField(name="Sourceid", type="string"))
        document.append(schema)

        # Areasrc style...
        document.styles.append(self.getAreaSrcStyle())

        # Ptsrc style...
        document.styles.append(self.getPtSrcStyle())

        # center style...
        document.styles.append(self.getCenterStyle())

        # s20 style...
        document.styles.append(self.getS20Style())

        # s20to100 style...
        label_style, balloon_style = self.getBaseStyle(id="s20to100")
        iconstyle = IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawCircle.png")
        s20to100_style = fastkml.styles.Style(ns=self.ns, id="s20to100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(s20to100_style)

        # s100 style...
        label_style, balloon_style = self.getBaseStyle(id="s100")
        iconstyle = IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawCircle.png")
        s100_style = fastkml.styles.Style(ns=self.ns, id="s100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(s100_style)

        # b20 style...
        document.styles.append(self.getB20Style())

        # b20to100 style...
        label_style, balloon_style = self.getBaseStyle(id="b20to100")
        iconstyle = IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawRectangle.png")
        b20to100_style = fastkml.styles.Style(ns=self.ns, id="b20to100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(b20to100_style)

        # b100 style...
        label_style, balloon_style = self.getBaseStyle(id="b100")
        iconstyle = IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawRectangle.png")
        b100_style = fastkml.styles.Style(ns=self.ns, id="b100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(b100_style)

        # u20 style...
        label_style, balloon_style = self.getBaseStyle(id="u20")
        iconstyle = IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawRectangle_ur.png")
        u20_style = fastkml.styles.Style(ns=self.ns, id="u20",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(u20_style)

        # u20to100 style...
        label_style, balloon_style = self.getBaseStyle(id="u20to100")
        iconstyle = IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawRectangle_ur.png")
        u20to100_style = fastkml.styles.Style(ns=self.ns, id="u20to100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(u20to100_style)

        # u100 style...
        label_style, balloon_style = self.getBaseStyle(id="u100")
        iconstyle = IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawRectangle_ur.png")
        u100_style = fastkml.styles.Style(ns=self.ns, id="u100",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(u100_style)

        # mir style...
        label_style, balloon_style = self.getBaseStyle(id="mir")
        iconstyle = IconStyle(ns=self.ns, icon_href="drawCross.png")
        mir_style = fastkml.styles.Style(ns=self.ns, id="mir",
                            styles=[label_style, balloon_style, iconstyle])        
        document.styles.append(mir_style)

        return document

    def copyUTMColumns(self, utmn, utme):
        return [utmn, utme]

    def getAreaSrcStyle(self):        
        # as_style.append_style(LineStyle(ns=self.ns, color="ff000000"))
        linestyle = LineStyle(ns=self.ns, color="ff000000")
        polystyle = PolyStyle(ns=self.ns, color="7c8080ff")
        balloonstyle = BalloonStyle(ns=self.ns, bgColor="ffffffff", text="$[description]")

        as_style = fastkml.styles.Style(ns=self.ns, id="Areasrc",
                                        styles=[linestyle, polystyle, balloonstyle])

        return as_style

    def getPtSrcStyle(self):
        label_style, balloon_style = self.getBaseStyle(id="Ptsrc")
        ps_style = fastkml.styles.Style(ns=self.ns, id="Ptsrc",
                            styles=[label_style, balloon_style,
                                IconStyle(ns=self.ns, color="ff8080ff", icon_href="drawCircle.png")])

        return ps_style

    def getCenterStyle(self):
        label_style, balloon_style = self.getBaseStyle(id="center")
        
        center_style = fastkml.styles.Style(ns=self.ns, id="center",
                                styles=[label_style, balloon_style,
                                        IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawCenter.png")])

        return center_style

    def getS20Style(self):
        label_style, balloon_style = self.getBaseStyle(id="s20")
        iconstyle = IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawCircle.png")
        s20_style = fastkml.styles.Style(ns=self.ns, id="s20",
                                         styles=[label_style, balloon_style, iconstyle])
        return s20_style

    def getB20Style(self):
        label_style, balloon_style = self.getBaseStyle(id="b20")
        iconstyle = IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawRectangle.png")
        b20_style = fastkml.styles.Style(ns=self.ns, id="b20",
                                         styles=[label_style, balloon_style, iconstyle])
        return b20_style

    def getBaseStyle(self, id):
        base_style = fastkml.styles.Style(ns=self.ns, id=id)
        
        labelstyle = LabelStyle(ns=self.ns, color="00000000")
        balloonstyle = BalloonStyle(ns=self.ns, bgColor="ffffffff", text="$[description]")

        base_style.labelstyle = labelstyle
        base_style.balloonstyle = balloonstyle 
        
        return labelstyle, balloonstyle