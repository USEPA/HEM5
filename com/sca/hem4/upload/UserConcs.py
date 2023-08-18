from com.sca.hem4.upload.InputFile import InputFile
from tkinter import messagebox
from com.sca.hem4.log import Logger



class UserConcs(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):
        
        self.colnames = ['rec_id', 'lon', 'lat', 'pollutant', 'cconc', 'aconc']
        self.numericColumns = ['lon', 'lat', 'cconc', 'aconc']
        self.strColumns = ['rec_id', 'pollutant']
                
        self.dataframe = self.readFromPathCsv(self.colnames)

        
    def clean(self, df):
        cleaned = df
        cleaned['pollutant'] = cleaned['pollutant'].str.lower()
        cleaned = df.fillna({'cconc':0, 'aconc':0, 'rec_id':'', 'pollutant':'',
                             'lon':-999.9, 'lat':-999.9})        
        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df['rec_id'] == '')]) > 0:
            Logger.logMessage("One or more receptor IDs are missing in the User Conc file.")
            messagebox.showinfo("Missing receptor IDs", "One or more receptor IDs are missing in the User Conc file.")           
            return None

        if len(df.loc[(df['pollutant'] == '')]) > 0:
            Logger.logMessage("One or more pollutant names are missing in the User Conc file.")
            messagebox.showinfo("Missing pollutant names", "One or more pollutant names are missing in the User Conc file.")
            return None

        # Check for duplicate records
        duplicates = self.duplicates(df, ['rec_id', 'lon', 'lat', 'pollutant'])
        if len(duplicates) > 0:
            Logger.logMessage("The following records are duplicated in the User Conc file (key=rec_id, lon, lat, pollutant):")
            for d in duplicates:
                Logger.logMessage(d)
            messagebox.showinfo("Duplicate Records", "One or more records are duplicated in the User Conc file (key=rec_id, lon, lat, pollutant).")
            return None


        #------ Check that coordinates make sense ----------------
        
        maxlon = 180
        minlon = -180
        maxlat = 85
        minlat = -80
        outlier_lon = df[(df['lon'] < minlon) | (df['lon'] > maxlon)]
        outlier_lat = df[(df['lat'] < minlat) | (df['lat'] > maxlat)]

        if len(outlier_lon) > 0:
            Logger.logMessage("There are longitudes in the User Conc file "
                              + "that are < -180 or > 180. Please correct these values.")
            messagebox.showinfo("Longitudes out of range", "There are longitudes in the User Conc file "
                              + "that are < -180 or > 180. Please correct these values.")
            return None

        if len(outlier_lat) > 0:
            Logger.logMessage("There are latitudes in the User Conc file "
                              + "that are < -80 or > 85. Please correct these values.")
            messagebox.showinfo("Latitudes out of range", "There are latitudes in the User Conc file "
                              + "that are < -80 or > 85. Please correct these values.")
            return None
                

        Logger.logMessage("Uploaded User Concentration file.\n")
        return df
