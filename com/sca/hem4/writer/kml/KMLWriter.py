# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:56:59 2017
@author: sfudge, cstolte
"""
import pandas as pd
import numpy as np
from fastkml import kml, SchemaData, Data
from fastkml.geometry import Geometry, Point, Polygon
from fastkml import ExtendedData
from fastkml.styles import LineStyle, PolyStyle, IconStyle, LabelStyle, BalloonStyle
from lxml.etree import CDATA
from pygeoif import LinearRing, LineString
from xml.sax.saxutils import unescape
from operator import itemgetter
from collections import OrderedDict
from shutil import copyfile

from com.sca.hem4.support.UTM import UTM


class KMLWriter():
    """
    Creates KML files suitable for viewing in Google Earth.
    """

    def __init__(self):
        self.ns = "{http://www.opengis.net/kml/2.2}"

    def write_kml_emis_loc(self, model):
        """
        Create KML of all sources. This method creates multiple files - one for the entire
        application run and one for each facility that is processed.
        """
        srcmap = self.create_sourcemap(model)

        kml_source_loc = kml.KML()

        document = kml.Document(ns=self.ns, id='emisloc', name='srcmap', description='Exported from HEM4')
        document.isopen = 1

        # Schema
        schema = kml.Schema(ns=self.ns, id="srcmap_schema", name="srcmap")
        schema.append("string", "Source_id", "Sourceid")
        document.append_schema(schema)

        # Areasrc style...
        document.append_style(self.getAreaSrcStyle())

        # Ptsrc style...
        document.append_style(self.getPtSrcStyle())

        # s20 style...
        document.append_style(self.getS20Style())

        # b20 style...
        document.append_style(self.getB20Style())

        kml_source_loc.append(document)

        # Fac_id - create source file for each facility
        # Read array to get facility id, source ids, source type and location parameters
        for facid, group in srcmap.groupby(["fac_id"]):
            fname = str(facid)

            fac_source_loc = kml.KML()
            docWithHeader = self.createDocumentWithHeader()

            es_folder = kml.Folder(ns=self.ns, name="Emission sources")
            fac_folder = kml.Folder(ns=self.ns, name="Facility " + fname)

            # create groups by source id and source type
            # src_df = srcmap.groupby(['source_id','src_type'])
            sub_map = srcmap.loc[srcmap.fac_id==facid]

            for name, group in sub_map.groupby(["source_id","source_type"]):
                sname = name[0]
                stype = name[1]

                # Emission sources  Point, Capped, Horizontal
                if stype == 'P' or stype == 'C' or stype == 'H':

                    placemark = kml.Placemark(ns=self.ns, name=sname,
                                              description=CDATA("<div align='center'>" + sname + "</div>"),
                                              styleUrl="#Ptsrc")

                    point = Point(group.iloc[0]['lon'], group.iloc[0]['lat'], 0.0)
                    placemark.geometry = Geometry(ns=self.ns, altitude_mode="relativeToGround", geometry=point)

                    es_folder.append(placemark)
                    fac_folder.append(placemark)

                # Area, Volume or Polygon
                elif stype == 'A' or stype == 'V' or stype == 'I':

                    placemark = kml.Placemark(ns=self.ns, name=sname,
                                              description=CDATA("<div align='center'>" + sname + "</div>"),
                                              styleUrl="#Areasrc")

                    simpleData = Data(name="SourceId", value=sname)
                    data = [simpleData]
                    schemaData = SchemaData(ns=self.ns, schema_url="#Source_map_schema", data=data)
                    elements = [schemaData]
                    placemark.extended_data = ExtendedData(ns=self.ns, elements=elements)

                    coords = []
                    for index, row in group.iterrows():
                        coord = (row["lon"], row["lat"], 0)
                        coords.append(coord)

                    linearRing = LinearRing(coordinates=coords)
                    polygon = Polygon(shell=linearRing)
                    placemark.geometry = Geometry(ns=self.ns, extrude=0, altitude_mode="clampToGround", tessellate=1,
                                                  geometry=polygon)

                    es_folder.append(placemark)
                    fac_folder.append(placemark)


                # Line or Bouyant Line
                elif stype == 'N' or stype == 'B':

                    placemark = kml.Placemark(ns=self.ns, name=sname,
                                              description=CDATA("<div align='center'>" + sname + "</div>"),
                                              styleUrl="#Linesrc")

                    ps_style = kml.Style(ns=self.ns)
                    style = LineStyle(ns=self.ns, width=group.iloc[0]['line_width'], color="7c8080ff")
                    ps_style.append_style(style)
                    placemark.append_style(ps_style)

                    lineString = LineString(group.iloc[0]['lon'], group.iloc[0]['lat'] + group.iloc[0]['lon_x2'],
                                            group.iloc[0]['lat_y2'])
                    placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=lineString)

                    es_folder.append(placemark)
                    fac_folder.append(placemark)


            kml_source_loc.append(fac_folder)

            # This will get appended to the facility specific file(s)
            docWithHeader.append(es_folder)

            fac_source_loc.append(docWithHeader)

            self.writeToFile("working_kml/fac_" + fname + "_source.kml", fac_source_loc)

        self.writeToFile("kml_source_loc.kml", kml_source_loc)

    def write_facility_kml(self, facid, faccen_lat, faccen_lon, outdir):
        """
        Create the KML file for a given facility
        """

        pxl = pd.ExcelFile(outdir + "polar_risk.xlsx")
        allpolar = pd.read_excel(pxl)
        allpolar['toshi'] = np.nan
        allpolar['total_hi'] = np.nan
        allpolar['pll_hi'] = np.nan

        # access inner_risk.xlxs for facility
        inxl = pd.ExcelFile(outdir + "inner_risk.xlsx")
        allinner = pd.read_excel(inxl)
        allinner['block'] = allinner['IDMARPLOT'][5:]

        # Get the source KML file for this facility and copy it to the output folder as the facility KML
        srckml_fname = "working_kml/fac_" + str(facid) + "_source.kml"
        fackml_fname = outdir + "fac_" + str(facid) + "_srcrec.kml"
        copyfile(srckml_fname, fackml_fname)

        inp_file = open("risks.kml","w")

        fac_kml = kml.KML()

        document = kml.Document(ns=self.ns)
        document.isopen = 1

        # facility center defined
        folder = kml.Folder(ns=self.ns, name="Domain center")
        folder.isopen = 0

        placemark = kml.Placemark(ns=self.ns, name="Domain center",
                                  description=CDATA("<div align='center'>Plant center</div>"),
                                  styleUrl="#s100")
        point = Point(faccen_lon, faccen_lat, 0.0)
        placemark.geometry = Geometry(ns=self.ns, altitude_mode="relativeToGround", geometry=point)
        folder.append(placemark)
        document.append(folder)

        # Determine if there are any user receptors
        urcr_folder = None
        for block, group in allinner.groupby(["block"]):
            user_rcpt = block
            ublock = group.iloc[0]['block']
            ulat = group.iloc[0]['LAT']
            ulon = group.iloc[0]['LON']
            u = 0
            if user_rcpt == 'U':

                if urcr_folder is None:
                    urcr_folder = kml.Folder(ns=self.ns, name="User receptor cancer risk")
                    urcr_folder.isopen = 0

                urtot = group.iloc[0]['risk'] * 1000000
                urrnd = round(urtot,2)

                description = "<div align='center'><B> Discrete Receptor</B> <br />" + \
                              "<B> ID: " + ublock + "</B> <br /> \n" + \
                              "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n" + \
                              "    " + "Total = " + str(urrnd) + "<br /><br /> \n"

                if urrnd > 0:
                    description += "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"

                    # create dictionary to hold summed risk of each pollutant
                    urhap_sum = {}
                    for index, row in group.iterrows():

                        if row["pollutant"] not in urhap_sum:
                            urhap_sum[row["pollutant"]] = row["risk"]
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
                            description = description + "    " + format(k) + " = " + format(zrnd) + "<br /> \n"

                description += "</div>"
                ur_placemark = kml.Placemark(ns=self.ns, name="User Receptor: " + ublock,
                                             description=CDATA(description),
                                             styleUrl="#u20")
                point = Point(ulon, ulat, 0.000)
                ur_placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=point)
                urcr_folder.append(ur_placemark)

            # First user receptor processed
            u += 1

            if user_rcpt != 'U':
                if urcr_folder is not None:
                    document.append(urcr_folder)
                break

        # Write inner receptors
        ir_folder = kml.Folder(ns=self.ns, name="Census block cancer risk")
        ir_folder.isopen = 0

        for loc, group in allinner.groupby(["LAT","LON"]):
            slat = loc[0]
            slon = loc[1]
            sBlock = group.iloc[0]['block']

            cbtot = group.iloc[0]['risk'] * 1000000
            cbrnd = round(cbtot,2)

            description = "<div align='center'><B> Census Block Receptor</B> <br /> \n" + \
                          "    " + "<B> Block: " + str(group.iloc[0]['block']) + "</B> <br /> \n" + \
                          "    " + "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n" + \
                          "    " + "Total = " + str(cbrnd) + "<br /><br /> \n"

            if cbrnd > 0:
                description += "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"

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

                #sort the dictionary by value
                sorted_cbhap_sum = OrderedDict(sorted(cbhap_sum.items(), key=itemgetter(1)))

                # check to make sure large enough value to keep
                for k, v in sorted_cbhap_sum.items():
                    w = v * 1000000     # risk in a million 0.005
                    if w > 0.005:
                        wrnd = round(w,2)
                        p01 = "    " + format(k) + " = " + format(wrnd) + "<br /> \n"
                        inp_file.write(p01)

            description += "</div>"

            point = Point(slon, slat, 0.0000)
            placemark = kml.Placemark(ns=self.ns, name="Block Receptor " + str(sBlock),
                                      description=CDATA(description),
                                      styleUrl="#b20")

            placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=point)
            ir_folder.append(placemark)

        document.append(ir_folder)

        # Write toshi for inner receptors
        irt_folder = kml.Folder(ns=self.ns, name="Census block TOSHI")
        irt_folder.isopen = 0

        for loc, group in allinner.groupby(["LAT","LON"]):
            slat = loc[0]
            slon = loc[1]
            sBlock = group.iloc[0]['block']

            hitot = group.iloc[0]['resp_hi']
            hirnd = round(hitot,2)
            description = "<div align='center'><B> Census Block Receptor</B> <br /> \n" + \
                          "    " + "<B> Block: " + str(group.iloc[0]['block']) + "</B> <br /> \n" + \
                          "    " + "<B> HEM4 Estimated Maximum TOSHI (Respiratory) </B> <br /> \n" + \
                          "    " + "Total = " + str(hirnd) + "<br /><br /> \n"

            if hirnd > 0:
                description += "    " + "<U> Top Pollutants Contributing to TOSHI </U> <br /> \n"

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
                        description += "    " + format(k) + " = " + format(wrnd) + "<br /> \n"

            description += "</div>"

            point = Point(slon, slat, 0.0000)
            placemark = kml.Placemark(ns=self.ns, name="Block Receptor " + str(sBlock),
                                      description=CDATA(description),
                                      styleUrl="#b20")
            placemark.visibility = 0
            placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=point)
            irt_folder.append(placemark)

        document.append(irt_folder)

        # start polar receptors cancer risk folder
        pr_folder = kml.Folder(ns=self.ns, name="Polar receptor cancer risk")
        pr_folder.isopen = 0

        # Write polar grid rings for cancer risk
        for loc, group in allpolar.groupby(["lat","lon"]):
            slat = loc[0]
            slon = loc[1]
            pg_dist = str(round(group.iloc[0]['distance'],0))
            pg_angle = str(round(group.iloc[0]['angle'],0))

            pgtot = group.iloc[0]['risk'] * 1000000
            pgrnd = round(pgtot,2)

            description = "<div align='center'><B> Polar Receptor</B> <br />" + \
                          "    " + "<B> Distance: " + pg_dist + " Angle: " + pg_angle + "</B> <br /> \n" + \
                          "    " + "<B> HEM4 Estimated Cancer Risk (in a million) </B> <br /> \n" + \
                          "    " + "Total = " + str(pgrnd) + "<br /><br /> \n"

            if pgrnd > 0:
                description += "    " + "<U> Top Pollutants Contributing to Total Cancer Risk </U> <br /> \n"

                # create dictionary to hold summed risk of each pollutant
                pghap_sum = {}
                for index, row in group.iterrows():

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
                            description += "    " + format(k) + " = " + format(zrnd) + "<br /> \n"

            description += "</div>"

            point = Point(slon, slat, 0.0000)
            placemark = kml.Placemark(ns=self.ns, name="Polar Receptor Distance: " + pg_dist + " Angle: " + str(group.iloc[0]['angle']),
                                      description=CDATA(description),
                                      styleUrl="#s20")
            placemark.visibility = 0
            placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=point)
            pr_folder.append(placemark)

        document.append(pr_folder)

        # start polar receptors TOSHI outputs
        prt_folder = kml.Folder(ns=self.ns, name="Polar TOSHI")
        prt_folder.isopen = 0

        for loc, group in allpolar.groupby(["lat","lon"]):
            slat = loc[0]
            slon = loc[1]
            pg_dist = str(round(group.iloc[0]['distance'],0))
            pg_angle = str(round(group.iloc[0]['angle'],0))

            pgtothi = group.iloc[0]['total_hi']
            pgrndhi = round(pgtothi,2)

            description = "<div align='center'><B> Polar Receptor</B> <br /> \n" + \
                          "    " + "<B> Distance: " + pg_dist + " Angle: " + pg_angle + "</B> <br /> \n" + \
                          "    " + "<B> HEM4 Estimated Max TOSHI (" + str(group.iloc[0]['toshi']) + ") </B> <br /> \n" + \
                          "    " + "Total = " + str(pgrndhi) + "<br /><br /> \n"

            if pgrndhi > 0:
                description += "    " + "<U> Top Pollutants Contributing to TOSHI </U> <br /> \n"

                # create dictionary to hold summed toshi of each pollutant
                pghi_sum = {}
                for index, row in group.iterrows():

                    if row["pollutant"] not in pghi_sum:
                        pghi_sum[row["pollutant"]] = row["poll_hi"]
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
                            description += "    " + format(k) + " = " + format(vrnd) + "<br /> \n"

            description += "</div>"

            point = Point(slon, slat, 0.0000)
            placemark = kml.Placemark(ns=self.ns, name="Polar Receptor Distance: " + pg_dist + " Angle: " + pg_angle,
                                      description=CDATA(description),
                                      styleUrl="#s20")
            placemark.visibility = 0
            placemark.geometry = Geometry(ns=self.ns, altitude_mode="clampToGround", geometry=point)
            prt_folder.append(placemark)

        document.append(prt_folder)
        fac_kml.append(document)
        self.writeToFile("risks.kml", fac_kml)

    def writeToFile(self, filename, kml):
        """
        Write a KML instance to a file.
        :param filename:
        :param kml: a fastKml KML instance
        """
        file = open(filename, "w")
        file.write(unescape(kml.to_string(prettyprint=True)))
        file.close()

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

    def create_sourcemap(self, model):
        """
        Create the source map dataframe needed for the source location KML.
        :return: dataframe of emission locations
        """

        # Create an array of all facility ids
        faclist = model.emisloc.dataframe.fac_id.unique()

        # Loop over all facility ids and populate the sourcemap dataframe

        source_map = pd.DataFrame()

        for row in faclist:

            # Emission location info for one facility. Keep certain columns.
            emislocs = model.emisloc.dataframe.loc[model.emisloc.dataframe.fac_id == row]
            [["fac_id","source_id","source_type","lon","lat","utmzone","x2","y2","location_type","lengthx"]]

            # If facility has a polygon source, get the vertices for this facility and append to emislocs
            if any(emislocs.source_type == "I") == True:
                polyver = model.multipoly.dataframe.loc[model.multipoly.dataframe.fac_id == row]
                [["fac_id","source_id","lon","lat","utmzone","location_type"]]
                # Assign source_type
                polyver["source_type"] = "I"
                # remove the I source_type rows from emislocs before appending polyver to avoid duplicate rows
                emislocs = emislocs[emislocs.source_type != "I"]
                # Append polyver to emislocs
                emislocs = emislocs.append(polyver)

            # If facility has a buoyant line source, get the line width
            if any(emislocs.source_type == "B") == True:
                buoy_linwid = model.multibuoy.dataframe.loc[model.multibuoy.dataframe.fac_id == row]
                [["fac_id","avglin_wid"]]
            else:
                buoy_linwid = pd.DataFrame()

            # Create a line width column for line and buoyant line sources
            emislocs["line_width"] = emislocs.apply(lambda row: self.set_width(row,buoy_linwid), axis=1)

            # Replace NaN with blank or 0 in emislocs
            emislocs = emislocs.fillna({"utmzone":0, "source_type":"", "x2":0, "y2":0})

            # Determine the common utm zone to use for this facility
            facutmzone = UTM.zone2use(emislocs)

            # Convert all lat/lon coordinates to UTM and UTM coordinates to lat/lon

            slat = emislocs["lat"].values
            slon = emislocs["lon"].values
            sutmzone = emislocs["utmzone"].values

            # First compute lat/lon coors using whatever zone was provided
            alat, alon = UTM.utm2ll(slat, slon, sutmzone)
            emislocs["lat"] = alat.tolist()
            emislocs["lon"] = alon.tolist()

            # Next compute UTM coors using the common zone
            sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
            autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
            emislocs["utme"] = autme.tolist()
            emislocs["utmn"] = autmn.tolist()
            emislocs["utmzone"] = autmz.tolist()

            # Compute UTM of any x2 and y2 coordinates and add to emislocs
            slat = emislocs["y2"].values
            slon = emislocs["x2"].values
            sutmzone = emislocs["utmzone"].values

            alat, alon = UTM.utm2ll(slat, slon, sutmzone)
            emislocs["lat_y2"] = alat.tolist()
            emislocs["lon_x2"] = alon.tolist()

            sutmzone = facutmzone*np.ones(len(emislocs["lat"]))
            autmn, autme, autmz = UTM.ll2utm(slat, slon, sutmzone)
            emislocs["utme_x2"] = autme.tolist()
            emislocs["utmn_y2"] = autmn.tolist()

            # Append to source_map
            source_map = source_map.append(emislocs)

        return source_map

    def createDocumentWithHeader(self):
        """
        Create a KML Document object with preset styles and schema.
        :return: the Document instance
        """
        document = kml.Document(ns=self.ns, name='srcmap', description='Exported from HEM4')
        document.isopen = 1

        # Schema
        schema = kml.Schema(ns=self.ns, id="srcmap_schema", name="srcmap")
        schema.append("string", "Source_id", "Sourceid")
        document.append_schema(schema)

        # Areasrc style...
        document.append_style(self.getAreaSrcStyle())

        # Ptsrc style...
        document.append_style(self.getPtSrcStyle())

        # s20 style...
        document.append_style(self.getS20Style())

        # s20to100 style...
        s20to100_style = self.getBaseStyle(id="s20to100")
        s20to100_style.append_style(IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawcircle.png"))
        document.append_style(s20to100_style)

        # s100 style...
        s100_style = self.getBaseStyle(id="s100")
        s100_style.append_style(IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawcircle.png"))
        document.append_style(s100_style)

        # b20 style...
        document.append_style(self.getB20Style())

        # b20to100 style...
        b20to100_style = self.getBaseStyle(id="b20to100")
        b20to100_style.append_style(IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawRectangle.png"))
        document.append_style(b20to100_style)

        # b100 style...
        b100_style = self.getBaseStyle(id="b100")
        b100_style.append_style(IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawRectangle.png"))
        document.append_style(b100_style)

        # u20 style...
        u20_style = self.getBaseStyle(id="u20")
        u20_style.append_style(IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawRectangle_ur.png"))
        document.append_style(u20_style)

        # u20to100 style...
        u20to100_style = self.getBaseStyle(id="u20to100")
        u20to100_style.append_style(IconStyle(ns=self.ns, color="ff00ffff", icon_href="drawRectangle_ur.png"))
        document.append_style(u20to100_style)

        # b100 style...
        u100_style = self.getBaseStyle(id="u100")
        u100_style.append_style(IconStyle(ns=self.ns, color="ff0000ff", icon_href="drawRectangle_ur.png"))
        document.append_style(u100_style)

        # mir style...
        mir_style = self.getBaseStyle(id="mir")
        mir_style.append_style(IconStyle(ns=self.ns, icon_href="cross.png"))
        document.append_style(mir_style)

        return document

    def getAreaSrcStyle(self):
        as_style = kml.Style(ns=self.ns, id="Areasrc")
        as_style.append_style(LineStyle(ns=self.ns, color="ff000000"))
        as_style.append_style(PolyStyle(ns=self.ns, color="7c8080ff"))
        as_style.append_style(BalloonStyle(ns=self.ns, bgColor="ffffffff", text="$[description]"))
        return as_style

    def getPtSrcStyle(self):
        ps_style = self.getBaseStyle(id="Ptsrc")
        ps_style.append_style(IconStyle(ns=self.ns, color="ff8080ff", icon_href="drawcircle.png"))
        return ps_style

    def getS20Style(self):
        s20_style = self.getBaseStyle(id="s20")
        s20_style.append_style(IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawcircle.png"))
        return s20_style

    def getB20Style(self):
        b20_style = self.getBaseStyle(id="b20")
        b20_style.append_style(IconStyle(ns=self.ns, color="ff00ff00", icon_href="drawRectangle.png"))
        return b20_style

    def getBaseStyle(self, id):
        base_style = kml.Style(ns=self.ns, id=id)
        base_style.append_style(LabelStyle(ns=self.ns, color="00000000"))
        base_style.append_style(BalloonStyle(ns=self.ns, bgColor="ffffffff", text="$[description]"))
        return base_style