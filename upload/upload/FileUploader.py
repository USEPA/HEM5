import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from upload.DoseResponse import DoseResponse
from upload.EmissionsLocations import EmissionsLocations
from upload.FacilityList import FacilityList
from upload.HAPEmissions import HAPEmissions
from upload.TargetOrganEndpoints import TargetOrganEndpoints
from upload.UserReceptors import UserReceptors
from upload.Polyvertex import Polyvertex 
from upload.BuoyantLine import BuoyantLine
from upload.Downwash import Downwash
from upload.Particle import Particle
from upload.LandUse import LandUse
from upload.Seasons import Seasons
from upload.GasParams import GasParams


class FileUploader():

    def __init__(self, model):
        self.model = model

    def uploadLibrary(self, filetype):
        if filetype == "haplib":
            self.model.haplib = DoseResponse()
        elif filetype == "organs":
            self.model.organs = TargetOrganEndpoints()
            
        elif filetype == "gas params":
            self.model.gasparams = GasParams()

    def upload(self, filetype, path):
            if filetype == "faclist":
                self.model.faclist = FacilityList(path)
            elif filetype == "hapemis":
                self.model.hapemis = HAPEmissions(path)
            elif filetype == "emisloc":
                self.model.emisloc = EmissionsLocations(path)


    def uploadDependent(self, filetype, path, dependency, facilities=None):

        if filetype == "polyvertex":
            self.model.multipoly = Polyvertex(path, dependency)

        elif filetype == "buoyant line":
            self.model.multibuoy = BuoyantLine(path, dependency)

        elif filetype == "user receptors":
            self.model.ureceptr = UserReceptors(path, dependency)
            
        elif filetype ==  "building downwash":
            self.model.bldgdw = Downwash(path, dependency)

        elif filetype == "particle depletion":
            self.model.partdep = Particle(path, dependency, facilities)
           
        elif filetype == "land use":
            self.model.landuse = LandUse(path, dependency)
          
        elif filetype == "seasons":
            self.model.seasons = Seasons(path, dependency)
        
        elif filetype == "emissions variation":
            pass
                
