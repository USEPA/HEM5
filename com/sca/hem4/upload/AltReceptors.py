from com.sca.hem4.CensusBlocks import population
from com.sca.hem4.upload.InputFile import InputFile
from tkinter import messagebox
from com.sca.hem4.upload.EmissionsLocations import *
from com.sca.hem4.upload.FacilityList import *

from tkinter import messagebox
import math
import polars as pl


rec_type = 'rec_type';
rec_id = 'rec_id';

class AltReceptors(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):
        
        # Specify dtypes for all fields
        # self.numericColumns = [lon, lat, elev, hill, population]
        # self.strColumns = [location_type, utmzone, rec_type, rec_id]
        self.colnames = [rec_id, rec_type, location_type, lon, lat
                          , utmzone, elev, hill, population]
        self.datatypes = {rec_id:pl.Utf8, rec_type:pl.Utf8, location_type:pl.Utf8
                          , lon:pl.Float64, lat:pl.Float64
                          , utmzone:pl.Int64, elev:pl.Float64, hill:pl.Float64
                          , population:pl.Int64}
                
        self.dataframe = self.readFromPathCsvPolarsDF()

        
    def clean(self, df):
        cleaned = df
        # cleaned.select([pl.exclude(rec_id), pl.col(rec_id).fill_null('')])
        cleaned.select([pl.exclude(location_type), pl.col(location_type).str.to_uppercase()])
        cleaned.select([pl.exclude(rec_type), pl.col(rec_type).str.to_uppercase()])
        
        # cleaned.replace(to_replace={rec_id:{"nan":""}}, inplace=True)
        # cleaned = cleaned.reset_index(drop = True)

        # upper case of selected fields
        # cleaned[location_type] = cleaned[location_type].str.upper()
        # cleaned[rec_type] = cleaned[rec_type].str.upper()

        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if df.select(pl.col(rec_id).is_null().sum())[0, rec_id] > 0:
            Logger.logMessage("One or more Receptor IDs are missing in the Alternate User Receptors List.")
            messagebox.showinfo("Missing Receptor IDs", "One or more Receptor IDs are missing in the Alternate User Receptors List.")
            return None

        if len(df.filter((pl.col(location_type) != 'L') & (pl.col(location_type) != 'U'))) > 0 :
            Logger.logMessage("One or more receptors are missing a Location Type in the Alternate User Receptors List.")
            messagebox.showinfo("Missing Location Type", "One or more receptors are missing a Location Type in the Alternate User Receptors List.")
            return None
        
        # Check for duplicate receptors
        uniqcols = df.select(pl.col([rec_id, lat, lon]))
        uniq = uniqcols.filter(pl.lit(~uniqcols.is_duplicated()))
        if uniq.shape[0] != df.shape[0]:
            Logger.logMessage("One or more records are duplicated in the Alternate User Receptors List (key=rec_id, lon, lat):")
            messagebox.showinfo("Duplicates", "One or more records are duplicated in the Alternate User Receptors List (key=rec_id, lon, lat):")
            return None

        # Check for missing population values
        if len(df.filter((pl.col(population).isnull()) & (pl.col(rec_type) == 'P'))) > 0 :
        # if len(df.loc[(df[population].isnull()) & (df[rec_type] == 'P')]) > 0:
            Logger.logMessage("Some 'P' receptors are missing population values in Alternate User Receptor List.")
            messagebox.showinfo("Missing Population Values", "Some 'P' receptors are missing population values in Alternate User Receptor List.")
            return None


        #------ Check that coordinates make sense ----------------
        
        # check lat/lons
        latlon_rows = df.filter(pl.col(loc_type)=='L')
        if len(latlon_rows) > 0:
            maxlon = 180
            minlon = -180
            maxlat = 85
            minlat = -80
            outlier_lon = latlon_rows.filter((pl.col(lon)<minlon) | (pl.col(lon)>maxlon) 
                                       | (pl.col(lon).isnull()))
            outlier_lat = latlon_rows.filter((pl.col(lat)<minlat) | (pl.col(lat)>maxlat) 
                                       | (pl.col(lat).isnull()))
            if len(outlier_lon) > 0:
                Logger.logMessage("There are longitudes in the Alternate Receptors file "
                                  + "that are < -180 or > 180. Please correct these values.")
                messagebox.showinfo("There are longitudes in the Alternate Receptors file "
                                  + "that are < -180 or > 180. Please correct these values.")
                return None

            if len(outlier_lat) > 0:
                Logger.logMessage("There are latitudes in the Alternate Receptors file "
                                  + "that are < -80 or > 85. Please correct these values.")
                messagebox.showinfo("There are longitudes in the Alternate Receptors file "
                                  + "that are < -80 or > 85. Please correct these values.")
                return None
                
        # check UTM coordinates
        utm_rows = df.filter(pl.col(loc_type)=='U')
        if len(utm_rows) > 0:
            maxlon = 850000
            minlon = 160000
            maxlat = 10000000
            minlat = 0
            outlier_utme = utm_rows.filter((pl.col(lon)<minlon) | (pl.col(lon)>maxlon) 
                                       | (pl.col(lon).isnull()))
            outlier_utmn = utm_rows.filter((pl.col(lat)<minlat) | (pl.col(lat)>maxlat) 
                                       | (pl.col(lat).isnull()))

            if len(outlier_utme) > 0:
                Logger.logMessage("There are UTM Easting coordinates in the Alternate Receptors file "
                                  + "that are < 0 or > 1000000. Please correct these values.")
                messagebox.showinfo("There are UTM Easting coordinates in the Alternate Receptors file "
                                  + "that are < 0 or > 1000000. Please correct these values.")
                return None

            if len(outlier_utmn) > 0:
                Logger.logMessage("There are UTM Northing coordinates in the Alternate Receptors file "
                                  + "that are < 160000 or > 850000. Please correct these values.")
                messagebox.showinfo("There are UTM Northing coordinates in the Alternate Receptors file "
                                  + "that are < 160000 or > 850000. Please correct these values.")
                return None

            utm_rows = utm_rows.with_columns(pl.col(utmzone).str.slice(-1).alias('zone'))
            try:
                utm_rows = utm_rows.with_column(pl.col('zone').cast(pl.Int64, strict=False))
            except ValueError as v:
                Logger.logMessage("Alternate Receptors file contains malformed UTM zone. "
                                  + "Please correct.")
                messagebox.showinfo("Alternate Receptors file contains malformed UTM zone. "
                                  + "Please correct.")
                return None
                
        
        for index, row in df.iterrows():

            receptor = row[rec_id]
            loc_type = row[location_type]

            maxlon = 180 if loc_type == 'L' else 850000
            minlon = -180 if loc_type == 'L' else 160000
            maxlat = 85 if loc_type == 'L' else 10000000
            minlat = -80 if loc_type == 'L' else 0

            if row[lon] > maxlon or row[lon] < minlon or math.isnan(row[lon]):
                Logger.logMessage("Receptor " + receptor + ": lon value " + str(row[lon]) + " out of range " +
                                  "in the Alternate User Receptors List.")
                messagebox.showinfo("Longitude out of Range", "Receptor " + receptor + ": lon value " + str(row[lon]) + " out of range " +
                                  "in the Alternate User Receptors List.")
                return None
            
            if row[lat] > maxlat or row[lat] < minlat or math.isnan(row[lat]):
                Logger.logMessage("Receptor " + receptor + ": lat value " + str(row[lat]) + " out of range " +
                                  "in the Alternate User Receptors List.")
                messagebox.showinfo("Latitude out of Range", "Receptor " + receptor + ": lat value " + str(row[lat]) + " out of range " +
                                  "in the Alternate User Receptors List.")
                
                return None

            if loc_type == 'U':
                zone = row[utmzone]
                if zone.endswith('N') or zone.endswith('S'):
                    zone = zone[:-1]

                try:
                    zonenum = int(zone)
                except ValueError as v:
                    Logger.logMessage("Receptor " + receptor + ": UTM zone value " + str(row[utmzone]) + " malformed " +
                                      "in the Alternate User Receptors List.")
                    messagebox.showinfo("UTM value malformed", "Receptor " + receptor + ": UTM zone value " + str(row[utmzone]) + " malformed " +
                                      "in the Alternate User Receptors List.")
                    return None

                if zonenum < 1 or zonenum > 60:
                    Logger.logMessage("Receptor " + receptor + ": UTM zone value " + str(row[utmzone]) + " invalid " +
                                      "in the Alternate User Receptors List.")
                    messagebox.showinfo("UTM zone value invalid", "Receptor " + receptor + ": UTM zone value " + str(row[utmzone]) + " invalid " +
                                      "in the Alternate User Receptors List.")
                    
                    return None

            valid = ['P', 'B', 'M']
            if row[rec_type] not in valid:
                Logger.logMessage("Receptor " + receptor + ": Receptor type value " + str(row[rec_type]) + " invalid " +
                                  "in the Alternate User Receptors List.")
                messagebox.showinfo("Receptor type invalid", "Receptor " + receptor + ": Receptor type value " + str(row[rec_type]) + " invalid " +
                                  "in the Alternate User Receptors List.")
                return None

        Logger.logMessage("Uploaded alternate user receptors.\n")
        return df
