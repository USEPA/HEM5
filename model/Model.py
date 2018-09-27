

class Model():

    def __init__(self):
        self.faclist = None
        self.emisloc = None
        self.hapemis = None
        self.multipoly = None
        self.multibuoy = None
        self.ureceptr = None
        self.haplib = None
        self.bldgdw = None
        self.partdep = None
        self.landuse = None
        self.vegetation = None
        self.facids = None
        self.depdeplt = None

        # A Dataframe containing the details of the polar receptor locations
        # (sector, ring, distance, lat, lon, etc.)
        self.polargrid = None

    @property
    def fac_ids(self):
        """Read-only array of facility ids"""
        return self.facids

    def reset(self):
        self.faclist = None
        self.emisloc = None
        self.hapemis = None
        self.multipoly = None
        self.multibuoy = None
        self.ureceptr = None
        self.haplib = None
        self.bldgdw = None
        self.partdep = None
        self.landuse = None
        self.vegetation = None
        self.facids = None
        self.depdeplt = None
        self.polargrid = None
