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
        self.colnames = [rec_id, rec_type, location_type, lon, lat
                          , utmzone, elev, hill, population]
        self.datatypes = {rec_id:pl.Utf8, rec_type:pl.Utf8, location_type:pl.Utf8
                          , lon:pl.Float64, lat:pl.Float64
                          , utmzone:pl.Utf8, elev:pl.Float64, hill:pl.Float64
                          , population:pl.Int64}
                
        self.dataframe = self.readFromPathCsvPolars(self.colnames)

        
    def clean(self, df):
        cleaned = df
        cleaned = cleaned.select([pl.exclude(location_type), pl.col(location_type).str.to_uppercase()])
        cleaned = cleaned.select([pl.exclude(rec_type), pl.col(rec_type).str.to_uppercase()])
        
        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if df.select(pl.col(rec_id).is_null().sum()).collect()[0, rec_id] > 0:
            Logger.logMessage("One or more Receptor IDs are missing in the Alternate Receptors file. Please correct and retry.")
            messagebox.showinfo("Missing Receptor IDs", "One or more Receptor IDs are missing in the Alternate Receptors file. Please correct and retry.")
            return None

        # Check for duplicate receptor ids
        uniq = df.collect().unique(subset=[rec_id])
        if uniq.select(pl.count())[0,0] != df.collect().select(pl.count())[0,0]:
            Logger.logMessage("One or more receptor IDs are duplicated in the Alternate Receptors file. Please correct and retry.")
            messagebox.showinfo("Duplicate receptor IDs", "One or more receptor IDs are duplicated in the Alternate Receptors file. Please correct and retry.")
            return None

        # Check for invalid elevations (meters)
        if len(df.filter((pl.col(elev) < -415) | (pl.col(elev) > 8850)).collect()) > 0 :
            Logger.logMessage("There is at least one elevation value in the Alternate Receptor file that is less than -415m or greater than 8850m. Please correct and retry.")
            messagebox.showinfo("Invalied Elevation Values", "There is at least one elevation value in the Alternate Receptor file that is less than -415m or greater than 8850m. Please correct and retry.")
            return None

        # Check for negative population values
        if len(df.filter(pl.col(population) < 0).collect()) > 0 :
            Logger.logMessage("Some receptors have negative population values in the Alternate Receptor file. Please correct and retry.")
            messagebox.showinfo("Negative Population Values", "Some receptors have negative population values in the Alternate Receptor file. Please correct and retry.")
            return None

        # Check for missing population values
        if len(df.filter((pl.col(population).is_null()) & (pl.col(rec_type) == 'P')).collect()) > 0 :
            Logger.logMessage("Some 'P' receptors are missing population values in the Alternate Receptor file. Please correct and retry.")
            messagebox.showinfo("Missing Population Values", "Some 'P' receptors are missing population values in the Alternate Receptor file. Please correct and retry.")
            return None

        if len(df.filter((pl.col(location_type) != 'L') & (pl.col(location_type) != 'U')).collect()) > 0 :
            Logger.logMessage("One or more receptors have an invalid Location Type in the Alternate Receptors file. Valid types are L or U. Please correct and retry.")
            messagebox.showinfo("Invalid Location Type", "One or more receptors are have an invalid Location Type in the Alternate Receptors file. Valid types are L or U. Please correct and retry.")
            return None


        #------ Check that coordinates make sense ----------------
        
        # Check for duplicate coordinates
        uniq = df.collect().unique(subset=[lat, lon])
        if uniq.select(pl.count())[0,0] != df.collect().select(pl.count())[0,0]:
            Logger.logMessage("One or more lat/lon coordinates are duplicated in the Alternate Receptors file. Please correct and retry.")
            messagebox.showinfo("Duplicate lat/lon", "One or more lat/lon coordinates are duplicated in the Alternate Receptors file. Please correct and retry.")
            return None

        
        # check lat/lons
        latlon_rows = df.filter(pl.col(location_type)=='L').collect()
        if len(latlon_rows) > 0:
            maxlon = 180
            minlon = -180
            maxlat = 85
            minlat = -80
            outlier_lon = latlon_rows.filter((pl.col(lon)<minlon) | (pl.col(lon)>maxlon) 
                                       | (pl.col(lon).is_null()))
            outlier_lat = latlon_rows.filter((pl.col(lat)<minlat) | (pl.col(lat)>maxlat) 
                                       | (pl.col(lat).is_null()))
            if len(outlier_lon) > 0:
                Logger.logMessage("There are longitudes in the Alternate Receptors file "
                                  + "that are < -180 or > 180. Please correct these values.")
                messagebox.showinfo("Longitudes out of range", "There are longitudes in the Alternate Receptors file "
                                  + "that are < -180 or > 180. Please correct these values.")
                return None

            if len(outlier_lat) > 0:
                Logger.logMessage("There are latitudes in the Alternate Receptors file "
                                  + "that are < -80 or > 85. Please correct these values.")
                messagebox.showinfo("Latitudes out of range", "There are latitudes in the Alternate Receptors file "
                                  + "that are < -80 or > 85. Please correct these values.")
                return None
                
        # check UTM coordinates
        utm_rows = df.filter(pl.col(location_type)=='U').collect()
        if len(utm_rows) > 0:
            maxlon = 850000
            minlon = 160000
            maxlat = 10000000
            minlat = 0
            outlier_utme = utm_rows.filter((pl.col(lon)<minlon) | (pl.col(lon)>maxlon) 
                                       | (pl.col(lon).is_null()))
            outlier_utmn = utm_rows.filter((pl.col(lat)<minlat) | (pl.col(lat)>maxlat) 
                                       | (pl.col(lat).is_null()))

            if len(outlier_utme) > 0:
                Logger.logMessage("There are UTM Easting coordinates in the Alternate Receptors file "
                                  + "that are < 160000 or > 850000. Please correct these values.")
                messagebox.showinfo("UTM Easting out of range", "There are UTM Easting coordinates in the Alternate Receptors file "
                                  + "that are < 160000 or > 850000. Please correct these values.")
                return None

            if len(outlier_utmn) > 0:
                Logger.logMessage("There are UTM Northing coordinates in the Alternate Receptors file "
                                  + "that are < 0 or > 10000000. Please correct these values.")
                messagebox.showinfo("UTM Northing out of range", "There are UTM Northing coordinates in the Alternate Receptors file "
                                  + "that are < 0 or > 10000000. Please correct these values.")
                return None

            
            # make sure UTM zone is correctly formatted
            utm_rows = utm_rows.with_columns(pl.col(utmzone).str.replace(r".$", "").alias("zone"))
            try:
                utm_rows = utm_rows.with_column(pl.col('zone').cast(pl.Int64, strict=True))
            except BaseException as e:
                Logger.logMessage("Alternate Receptors file contains malformed UTM zone. "
                                  + "Please correct.")
                messagebox.showinfo("Malformed UTM zone", "Alternate Receptors file contains malformed UTM zone. "
                                  + "Please correct.")
                return None
            
            # make sure UTM zone value is within range
            if len(utm_rows.filter((pl.col('zone') < 1) | (pl.col('zone') > 60))) > 0:
                Logger.logMessage("Alternate Receptors file contains at least one invalid UTM zone that is < 1 or > 60. " +
                                  "Please correct.")
                messagebox.showinfo("Invalid UTM zone", "Alternate Receptors file contains at least one invalid UTM zone that is < 1 or > 60. " +
                                    "Please correct.")
                return None                
        
        # Make sure receptor type code is valid
        valid = ['P', 'B', 'M']
        invalid_df = df.filter(~pl.col(rec_type).is_in(valid)).collect()
        if len(invalid_df) > 0:
            Logger.logMessage("Alternate Receptors file contains receptor types that are not P, B, or M. " + 
                              "Please correct.")
            messagebox.showinfo("Invalid receptor type", "Alternate Receptors file contains receptor types that are not P, B, or M. " + 
                                "Please correct.")
            return None

        Logger.logMessage("Uploaded alternate user receptors.\n")
        return df
