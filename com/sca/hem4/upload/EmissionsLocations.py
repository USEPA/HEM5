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

        #EMISSIONS LOCATION excel to dataframe
        # HEADER------------------------
        # FacilityID|SourceID|LocationType|Longitude|Latitude|UTMzone|SourceType|Lengthx|Lengthy|Angle|HorzDim|
        # VertDim|AreaVolReleaseHgt|StackHgt_m|StackDiameter_m|ExitGasVel_m|ExitGasTemp_K|Elevation_m|X2|Y2
        emisloc_df = self.readFromPath(
            (fac_id,source_id,location_type,lon,lat,utmzone,source_type,lengthx,lengthy,angle,
             horzdim,vertdim,areavolrelhgt,stkht,stkdia,stkvel,stktemp,elev,x2,y2,method,massfrac,partdiam))

        # We need to do this now, since the GUI needs to know right away whether or not to prompt
        # for a particle file.
        emisloc_df = emisloc_df.fillna({method:1, massfrac:1, partdiam:1})
        emisloc_df = emisloc_df.reset_index(drop=True)

        #record upload in log
        emis_num = set(emisloc_df[fac_id])
        self.log.append("Uploaded emissions location file for " + str(len(emis_num)) + " facilities\n")
        self.dataframe = emisloc_df