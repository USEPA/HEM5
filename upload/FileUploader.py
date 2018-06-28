import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from upload.DoseResponse import DoseResponse
from upload.EmissionsLocations import EmissionsLocations
from upload.FacilityList import FacilityList
from upload.HAPEmissions import HAPEmissions
from upload.UserReceptors import UserReceptors


class FileUploader():

    def __init__(self, model):
        self.model = model

    def upload(self, filetype, path):
            if filetype == "faclist":
                self.model.faclist = FacilityList(path)
            elif filetype == "hapemis":
                self.model.hapemis = HAPEmissions(path)
            elif filetype == "emisloc":
                self.model.emisloc = EmissionsLocations(path)
            elif filetype == "haplib":
                self.model.haplib = DoseResponse(path)
            elif filetype == "building downwash":
                pass
                #file_path = os.path.abspath(filename)
                # self.bd_list.set(file_path)
                # self.bd_path = file_path
                #
                # #building downwash dataframe
                # self.bd_df = pd.read_csv(open(self.bd_path ,"rb"))
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded building downwash for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif filetype == "particle depletion":
                pass
                #file_path = os.path.abspath(filename)
                # self.dep_part.set(file_path)
                # self.dep_part_path = file_path
                #
                # #particle dataframe
                # self.particle_df = pd.read_excel(open(self.dep_part_path, "rb")
                #                                  , names=("fac_id", "source_id", "diameter", "mass", "density"))
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded particle depletion for...")
                # self.scr.insert(tk.INSERT, "\n")

            elif filetype == "land use description":
                pass
                #file_path = os.path.abspath(filename)
                # self.dep_land.set(file_path)
                # self.dep_land_path = file_path
                #
                # self.land_df = pd.read_excel(open(self.dep_land_path, "rb"))
                # self.land_df.rename({"Facility ID " : "fac_id"})
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded land use description for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif filetype == "season vegetation":
                pass
                #file_path = os.path.abspath(filename)
                # self.dep_veg.set(file_path)
                # self.dep_veg_path = file_path
                #
                # self.veg_df = pd.read_csv(open(self.dep_veg_path, "rb"))
                # self.veg_df.rename({"Facility ID": "fac_id"})
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded season vegetation for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif filetype == "emissions variation":
                pass
                #file_path = os.path.abspath(filename)
                # self.evar_list.set(file_path)
                # self.evar_list_path = file_path
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded emissions variance for...")
                # self.scr.insert(tk.INSERT, "\n")


    def uploadDependent(self, filetype, path, dependency):

        if filetype == "polyvertex":

            emisloc_df = dependency;

            #POLYVERTEX excel to dataframe
            multipoly_df = pd.read_excel(open(path, "rb"),
                 names=("fac_id","source_id","location_type","lon","lat","utmzone","numvert","area", "fipstct"),
                 converters={"FacilityID":str,"source_id":str,"location_type":str,"lon":float,"lat":float,
                     "utmzone":str,"numvert":float,"area":float})

            #get polyvertex facility list for check
            find_is = emisloc_df[emisloc_df['source_type'] == "I"]
            fis = find_is['fac_id']

            #check for unassigned polyvertex
            check_poly_assignment = set(multipoly_df["fac_id"])
            poly_unassigned = []
            logMsg = ""

            for fac in fis:
                if fac not in check_poly_assignment:
                    poly_unassigned.append(fac)

            if len(poly_unassigned) > 0:
                messagebox.showinfo("Unassigned Polygon Sources",
                    "Polygon Sources for " + ", ".join(poly_unassigned) +
                    " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                #clear box and empty data frame
            else:
                logMsg = "Uploaded polygon sources for " + " ".join(check_poly_assignment) + "\n"

            return {'path': path, 'df': multipoly_df, 'messages': [logMsg]}

        elif filetype == "bouyant line":

            self.bouyant_list.set(path)
            self.bouyant_path = path

            #BOUYANT LINE excel to dataframe
            self.multibuoy_df = pd.read_excel(open(self.bouyant_path, "rb")
                                              , names=("fac_id", "avgbld_len", "avgbld_hgt", "avgbld_wid", "avglin_wid", "avgbld_sep", "avgbuoy"))


            #get bouyant line facility list
            self.emisloc_df['source_type'].str.upper()
            find_bs = self.emisloc_df[self.emisloc_df['source_type'] == "B"]

            fbs = find_bs['fac_id'].unique()

            #check for unassigned buoyants

            check_bouyant_assignment = set(self.multibuoy_df["fac_id"])

            bouyant_unassigned = []
            for fac in fbs:

                if fac not in check_bouyant_assignment:
                    bouyant_unassigned.append(fac)

            if len(bouyant_unassigned) > 0:
                messagebox.showinfo("Unassigned Bouyant Line parameters", "Bouyant Line parameters for " + ", ".join(bouyant_unassigned) + " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
            else:
                pass
                #record upload in log
                #self.scr.insert(tk.INSERT, "Uploaded bouyant line parameters for " + " ".join(check_bouyant_assignment))
                #self.scr.insert(tk.INSERT, "\n")


        elif filetype == "user receptors":
            self.model.ureceptr = UserReceptors(path, dependency)


