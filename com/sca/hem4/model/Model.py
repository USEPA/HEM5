from collections import defaultdict

fac_id = 'fac_id';
source_id = 'source_id';
pollutant = 'pollutant';
group = 'group';
lon = 'lon';
lat = 'lat';
elev = 'elev';
hill = 'hill';
overlap = 'overlap';
conc = 'conc'
result = 'result';
flag = 'flag';
avg_time = 'avg_time';
num_yrs = 'num_yrs';
net_id = 'net_id';
angle = 'angle';

class Model():

    def __init__(self):
        """
        The following are inputs and have dataframe, msg, 
        
        faclist - facilities list options file 
        emisloc
        
        
        """
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
        self.seasons = None
        self.emisvar = None
        self.facids = None
        self.depdeplt = None
        self.polargrid = None
        self.organs = None
        self.riskfacs_df = None
        self.all_polar_receptors_df = None
        self.all_inner_receptors_df = None
        self.all_outer_receptors_df = None
        self.risk_by_latlon = None
        self.max_indiv_risk_df = None
        self.sourcelocs = None
        self.gasparams = None
        self.model_optns = defaultdict()
        self.save = None

        # Facility-specific values that are computed during the run - these are ephemeral
        # and get overwritten when the next facility runs.
        self.computedValues = {}

        # Initialize model options
        self.initializeOptions()

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
        self.seasons = None
        self.emisvar = None
        self.facids = None
        self.depdeplt = None
        self.polargrid = None
        self.organs = None
        self.riskfacs_df = None
        self.all_polar_receptors_df = None
        self.all_inner_receptors_df = None
        self.all_outer_receptors_df = None
        self.risk_by_latlon = None
        self.max_indiv_risk_df = None
        self.sourcelocs = None
        self.gasparams = None
        self.model_optns = defaultdict()
        self.save = None

        # Initialize model options
        self.initializeOptions()


    def initializeOptions(self):
        self.model_optns['ureponly'] = False
        self.model_optns['ureponly_nopop'] = False
        self.model_optns['ureponly_flat'] = False