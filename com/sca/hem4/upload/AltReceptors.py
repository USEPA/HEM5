from com.sca.hem4.CensusBlocks import population
from com.sca.hem4.upload.InputFile import InputFile
from tkinter import messagebox
from com.sca.hem4.upload.EmissionsLocations import *
from com.sca.hem4.upload.FacilityList import *

rec_type = 'rec_type';
rec_id = 'rec_id';

class AltReceptors(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):
        
        # Specify dtypes for all fields
        self.numericColumns = [lon, lat, elev, hill, population]
        self.strColumns = [location_type, utmzone, rec_type, rec_id]

        altreceptor_df = self.readFromPathCsv(
                (rec_id, rec_type, location_type, lon, lat, utmzone, elev, hill, population))

        self.log.append("Uploaded Alternate Receptors")

        self.dataframe = altreceptor_df