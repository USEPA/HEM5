import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from upload.DoseResponse import DoseResponse
from upload.EmissionsLocations import EmissionsLocations
from upload.FacilityList import FacilityList
from upload.HAPEmissions import HAPEmissions
from upload.UserReceptors import UserReceptors 
from upload.BouyantLine import BouyantLine


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
            
            self.model.Polyvertex(path, dependency)

        elif filetype == "bouyant line":

            self.model.BouyantLine(path, dependency)


        elif filetype == "user receptors":
            self.model.ureceptr = UserReceptors(path, dependency)


