from upload.DependentInputFile import DependentInputFile
from tkinter import messagebox

class UserReceptors(DependentInputFile):

    def __init__(self, path, dependency):
        DependentInputFile.__init__(self, path, dependency)

    def createDataframe(self):

        #USER RECEPTOR dataframe
        faclist_df = self.dependency

        # Specify dtypes for all fields
        self.numericColumns = ["lon", "lat", "elev"]
        self.strColumns = ["fac_id","loc_type", "utmzone", "rec_type", "rec_id"]

        ureceptor_df = self.readFromPath(
            ("fac_id", "loc_type", "lon", "lat", "utmzone", "elev", "rec_type", "rec_id"))

        #check for unassigned user receptors
        check_receptor_assignment = ureceptor_df["fac_id"]

        receptor_unassigned = []
        for receptor in check_receptor_assignment:
            #print(receptor)
            row = faclist_df.loc[faclist_df['fac_id'] == receptor]
            #print(row)
            check = row['user_rcpt'] == 'Y'
            #print(check)

            if check is False:
                receptor_unassigned.append(str(receptor))

        if len(receptor_unassigned) > 0:
            facilities = set(receptor_unassigned)
            messagebox.showinfo("Unassigned User Receptors", "Receptors for " + ", ".join(facilities) + " have not been assigned. Please edit the 'user_rcpt' column in the facility options file.")
        else:
            check_receptor_assignment = [str(facility) for facility in check_receptor_assignment]
            self.log.append("Uploaded user receptors for " + " ".join(check_receptor_assignment) + "\n")

            self.dataframe = ureceptor_df ##moved this into the loop
