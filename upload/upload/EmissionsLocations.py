from upload.InputFile import InputFile

class EmissionsLocations(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):

        #EMISSIONS LOCATION excel to dataframe
        # HEADER------------------------
        # FacilityID|SourceID|LocationType|Longitude|Latitude|UTMzone|SourceType|Lengthx|Lengthy|Angle|HorzDim|
        # VertDim|AreaVolReleaseHgt|StackHgt_m|StackDiameter_m|ExitGasVel_m|ExitGasTemp_K|Elevation_m|X2|Y2
        emisloc_df = self.readFromPath(
            ("fac_id","source_id","location_type","lon","lat","utmzone","source_type","lengthx","lengthy","angle",
             "horzdim","vertdim","areavolrelhgt","stkht","stkdia","stkvel","stktemp","elev","x2","y2"),
            {0:str,1:str,2:str,3:float,4:float,5:float,6:str,7:float,8:float,9:float,10:float,11:float,12:float,
             13:float,14:float,15:float,16:float,17:float,18:float,19:float})

        #record upload in log
        emis_num = set(emisloc_df['fac_id'])
        self.log.append("Uploaded emissions location file for " + str(len(emis_num)) + " facilities\n")
        self.dataframe = emisloc_df