import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from com.sca.hem4.upload.DoseResponse import DoseResponse
from com.sca.hem4.upload.EmissionsLocations import EmissionsLocations
from com.sca.hem4.upload.FacilityList import FacilityList
from com.sca.hem4.upload.HAPEmissions import HAPEmissions
from com.sca.hem4.upload.MetLib import MetLib
from com.sca.hem4.upload.TargetOrganEndpoints import TargetOrganEndpoints
from com.sca.hem4.upload.UserReceptors import UserReceptors
from com.sca.hem4.upload.AltReceptors import AltReceptors
from com.sca.hem4.upload.Polyvertex import Polyvertex
from com.sca.hem4.upload.BuoyantLine import BuoyantLine
from com.sca.hem4.upload.Downwash import Downwash
from com.sca.hem4.upload.Particle import Particle
from com.sca.hem4.upload.LandUse import LandUse
from com.sca.hem4.upload.Seasons import Seasons
from com.sca.hem4.upload.GasParams import GasParams
from com.sca.hem4.upload.EmisVar import EmisVar


class FileUploader():

    def __init__(self, model):
        self.model = model

    def uploadLibrary(self, filetype):
        if filetype == "haplib":
            self.model.haplib = DoseResponse()
        elif filetype == "organs":
            self.model.organs = TargetOrganEndpoints()
        elif filetype == "metlib":
            self.model.metlib = MetLib()
        elif filetype == "gas params":
            self.model.gasparams = GasParams()

    def upload(self, filetype, path):
            if filetype == "faclist":
                self.model.faclist = FacilityList(path)
            elif filetype == "hapemis":
                self.model.hapemis = HAPEmissions(path, self.model.haplib)
            elif filetype == "emisloc":
                self.model.emisloc = EmissionsLocations(path)
            elif filetype == "alt receptors":
                self.model.altreceptr = AltReceptors(path)


    def uploadDependent(self, filetype, path, dependency, facilities=None):

        if filetype == "polyvertex":
            self.model.multipoly = Polyvertex(path, dependency)

        elif filetype == "buoyant line":
            self.model.multibuoy = BuoyantLine(path, dependency)

        elif filetype == "user receptors":
            self.model.ureceptr = UserReceptors(path, dependency, False)

        elif filetype ==  "building downwash":
            self.model.bldgdw = Downwash(path, dependency)

        elif filetype == "particle depletion":
            self.model.partdep = Particle(path, dependency, facilities)
           
        elif filetype == "land use":
            self.model.landuse = LandUse(path, dependency)
          
        elif filetype == "seasons":
            self.model.seasons = Seasons(path, dependency)
        
        elif filetype == "emissions variation":
            self.model.emisvar = EmisVar(path, dependency)
                
