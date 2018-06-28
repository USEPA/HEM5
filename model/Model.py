
class Model():

    def __init__(self):
        self.faclist = None
        self.emisloc = None
        self.hapemis = None
        self.multipoly = None
        self.multibuoy = None
        self.ureceptr = None
        self.haplib = None

        self.facids = None

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

        self.facids = None
