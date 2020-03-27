from com.sca.hem4.CensusBlocks import population
from com.sca.hem4.upload.DependentInputFile import DependentInputFile
from tkinter import messagebox
from com.sca.hem4.upload.EmissionsLocations import *
from com.sca.hem4.upload.FacilityList import *

rec_type = 'rec_type';
rec_id = 'rec_id';

class UserReceptors(DependentInputFile):

    def __init__(self, path, dependency, csvFormat):
        DependentInputFile.__init__(self, path, dependency, csvFormat=csvFormat)

    def createDataframe(self):

        #USER RECEPTOR dataframe
        faclist_df = self.dependency
        
        # Specify dtypes for all fields
        self.numericColumns = [lon, lat, elev, hill]
        self.strColumns = [fac_id,location_type, utmzone, rec_type, rec_id]

        if self.csvFormat:
            ureceptor_df = self.readFromPathCsv(
                (fac_id, location_type, lon, lat, utmzone, elev, rec_type, rec_id, hill))
        else:
            ureceptor_df = self.readFromPath(
                (fac_id, location_type, lon, lat, utmzone, elev, rec_type, rec_id, hill))
        
        #check for unassigned user receptors
        check_receptor_assignment = ureceptor_df[fac_id]

        receptor_unassigned = []
        for receptor in check_receptor_assignment:
            #print(receptor)
            row = faclist_df.loc[faclist_df[fac_id] == receptor]
            #print(row)
            check = row[user_rcpt] == 'Y'
            #print(check)

            if check is False:
                receptor_unassigned.append(str(receptor))

        if len(receptor_unassigned) > 0:
            facilities = set(receptor_unassigned)
            messagebox.showinfo("Unassigned User Receptors", "Receptors for " + ", ".join(facilities) + " have not been assigned. Please edit the 'user_rcpt' column in the facility options file.")
        else:
            check_receptor_assignment = [str(facility) for facility in check_receptor_assignment.unique()]
            self.log.append("Uploaded user receptors for " + " ".join(check_receptor_assignment) + "\n")

            self.dataframe = ureceptor_df ##moved this into the loop

    def validate(self, df):
        pass