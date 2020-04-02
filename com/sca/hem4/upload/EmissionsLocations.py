from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *
from com.sca.hem4.support.UTM import *

location_type = 'location_type'
source_type = 'source_type'
lengthx = 'lengthx'
lengthy = 'lengthy'
angle = 'angle'
horzdim = 'horzdim'
vertdim = 'vertdim'
areavolrelhgt = 'areavolrelhgt'
stkht = 'stkht'
stkdia = 'stkdia'
stkvel = 'stkvel'
stktemp = 'stktemp'
x2 = 'x2'
y2 = 'y2'
method = 'method'
massfrac = 'massfrac'
partdiam = 'partdiam'

class EmissionsLocations(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):

        # two row header
        self.skiprows = 1

        # Specify dtypes for all fields
        self.numericColumns = [lon,lat,lengthx,lengthy,angle,horzdim,vertdim,areavolrelhgt,
                               stkht,stkdia,stkvel,stktemp,elev,x2,y2,method,massfrac,partdiam]
        self.strColumns = [fac_id,source_id,location_type,source_type,utmzone]

        emisloc_df = self.readFromPath(
            (fac_id,source_id,location_type,lon,lat,utmzone,source_type,lengthx,lengthy,angle,
             horzdim,vertdim,areavolrelhgt,stkht,stkdia,stkvel,stktemp,elev,x2,y2,method,massfrac,partdiam))

        self.dataframe = emisloc_df

    def clean(self, df):

        cleaned = df.fillna({utmzone:'0N', source_type:'', lengthx:1, lengthy:1, angle:0,
                                    horzdim:1, vertdim:1, areavolrelhgt:0, stkht:0,
                                    stkvel:0, stktemp:0, elev:0, x2:0, y2:0, method:1, massfrac:1, partdiam:1})
        cleaned.replace(to_replace={fac_id:{"nan":""}, source_id:{"nan":""}}, inplace=True)
        cleaned = cleaned.reset_index(drop = True)

        # upper case of selected fields
        cleaned[source_type] = cleaned[source_type].str.upper()
        cleaned[location_type] = cleaned[location_type].str.upper()

        return cleaned

    def validate(self, df):
        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        if len(df.loc[(df[fac_id] == '')]) > 0:
            Logger.logMessage("One or more facility IDs are missing in the Emissions Locations List.")
            return None

        if len(df.loc[(df[source_id] == '')]) > 0:
            Logger.logMessage("One or more source IDs are missing in the Emissions Locations List.")
            return None

        if len(df.loc[(df[location_type] != 'L') & (df[location_type] != 'U')]) > 0:
            Logger.logMessage("One or more locations are missing a coordinate system in the Emissions Locations List.")
            return None

        if len(df.loc[(df[source_type] != 'P') & (df[source_type] != 'C') &
                      (df[source_type] != 'H') & (df[source_type] != 'A') &
                      (df[source_type] != 'V') & (df[source_type] != 'N') &
                      (df[source_type] != 'B') & (df[source_type] != 'I')]) > 0:
            Logger.logMessage("One or more source types are missing a valid value in the Emissions Locations List.")
            return None

        for index, row in df.iterrows():

            facility = row[fac_id]
            type = row[location_type]

            maxlon = 180 if type == 'L' else 850000
            minlon = -180 if type == 'L' else 160000
            maxlat = 85 if type == 'L' else 10000000
            minlat = -80 if type == 'L' else 0

            if row[lon] > maxlon or row[lon] < minlon:
                Logger.logMessage("Facility " + facility + ": lon value " + str(row[lon]) + " out of range " +
                                  "in the Emissions Locations List.")
                return None
            if row[lat] > maxlat or row[lat] < minlat:
                Logger.logMessage("Facility " + facility + ": lat value " + str(row[lat]) + " out of range " +
                                  "in the Emissions Locations List.")
                return None

            if type == 'U':
                zone = row[utmzone]
                if zone.endswith('N') or zone.endswith('S'):
                    zone = zone[:-1]

                try:
                    zonenum = int(zone)
                except ValueError as v:
                    Logger.logMessage("Facility " + facility + ": UTM zone value " + str(row[utmzone]) + " malformed " +
                                      "in the Emissions Locations List.")
                    return None

                if zonenum < 1 or zonenum > 60:
                    Logger.logMessage("Facility " + facility + ": UTM zone value " + str(row[utmzone]) + " invalid " +
                                      "in the Emissions Locations List.")
                    return None

        # ----------------------------------------------------------------------------------
        # Defaulted: Invalid values in these columns will be replaced with a default.
        # ----------------------------------------------------------------------------------
        for index, row in df.iterrows():

            facility = row[fac_id]

            if row[lengthx] <= 0:
                Logger.logMessage("Facility " + facility + ": Length X value " + str(row[lengthx]) +
                                  " out of range. Defaulting to 1.")
                row[lengthx] = 1
            if row[lengthy] <= 0:
                Logger.logMessage("Facility " + facility + ": Length Y value " + str(row[lengthy]) +
                                  " out of range. Defaulting to 1.")
                row[lengthy] = 1
            if row[angle] < 0 or row[angle] >= 90:
                Logger.logMessage("Facility " + facility + ": angle value " + str(row[angle]) +
                                  " out of range. Defaulting to 0.")
                row[angle] = 0
            if row[horzdim] <= 0:
                Logger.logMessage("Facility " + facility + ": Horizontal dim value " + str(row[horzdim]) +
                                  " out of range. Defaulting to 1.")
                row[horzdim] = 1
            if row[vertdim] <= 0:
                Logger.logMessage("Facility " + facility + ": Vertical dim value " + str(row[vertdim]) +
                                  " out of range. Defaulting to 1.")
                row[vertdim] = 1
            if row[areavolrelhgt] < 0:
                Logger.logMessage("Facility " + facility + ": Release height value " + str(row[areavolrelhgt]) +
                                  " out of range. Defaulting to 0.")
                row[areavolrelhgt] = 0
            if row[stkht] < 0:
                Logger.logMessage("Facility " + facility + ": Stack height value " + str(row[stkht]) +
                                  " out of range. Defaulting to 0.")
                row[stkht] = 0
            if row[stkdia] <= 0:
                Logger.logMessage("Facility " + facility + ": Stack diameter value " + str(row[stkdia]) +
                                  " out of range.")
                return None
            if row[stkvel] < 0:
                Logger.logMessage("Facility " + facility + ": Exit velocity value " + str(row[stkvel]) +
                                  " out of range. Defaulting to 0.")
                row[stkvel] = 0
            if row[method] not in [1, 2]:
                Logger.logMessage("Facility " + facility + ": Method value " + str(row[method]) +
                                  " invalid. Defaulting to 1.")
                row[method] = 1
            if row[massfrac] < 0 or row[massfrac] > 1:
                Logger.logMessage("Facility " + facility + ": Mass fraction value " + str(row[massfrac]) +
                                  " invalid. Defaulting to 1.")
                row[massfrac] = 1
            if row[partdiam] <= 0:
                Logger.logMessage("Facility " + facility + ": Particle diameter value " + str(row[partdiam]) +
                                  " invalid. Defaulting to 1.")
                row[partdiam] = 1

            df.loc[index] = row

        self.log.append("Uploaded emissions location file for " + str(len(df)) + " facilities.\n")
        return df
