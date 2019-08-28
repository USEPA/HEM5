import os

from numpy.core.multiarray import array
from pandas import DataFrame

from log.Logger import Logger
from writer.excel.ExcelWriter import ExcelWriter

class InputSelectionOptions(ExcelWriter):
    """
    Provides the options and input file names specified by the user at the start of the run.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.facilityId = facilityId
        self.filename = os.path.join(targetDir, facilityId + "_input_selection_options.xlsx")

    def getHeader(self):
        return ['Facility ID', 'Aermod Title2', 'Emissions Phase', 'Rural/Urban', 'Deposition (YN)',
             'Depletion (YN)', 'Deposition Type (particle/vapor)', 'Depletion Type (particle/vapor)', 
             'Elevation (YN)', 'Acute Hours', 
             'Acute Multiplier', 'Building Downwash (YN)', 'User Receptors (YN)', 'Max Modeling Distance', 
             'Discrete Modeling Distance', 'Overlap Distance', 'Number of Polar Rings', 
             'Number of Polar Radials', 'Acute (YN)', 'All Receptors (YN)', 'First Ring Distance', 
             'Fastall (YN)', 'Facility Group Name', 'Facility List Options File', 
             'Emission Location File', 'HAP Emissions File', 'User Receptor File', 
             'Particle Size File', 'Building Downwash File', 'Buoyant Line File',
             'Landuse File', 'Seasons File', 'Polygon Vertex File']


    def generateOutputs(self):

#        faclist = self.model.faclist.dataframe
#        facoptions = faclist.loc[faclist.fac_id == self.facilityId].iloc[0]
        facoptions = self.model.facops

        title1 = self.facilityId
        title2 = self.model.model_optns['titletwo']
        dep_type = facoptions['pdep'].iloc[0] + '/' + facoptions['vdep'].iloc[0]
        depl_type = facoptions['pdepl'].iloc[0] + '/' + facoptions['vdepl'].iloc[0]
        ruralurban = self.model.model_optns['urban']
        phase = self.model.model_optns['phase']
        dep_yn = facoptions['dep'].iloc[0]
        depl_yn = facoptions['depl'].iloc[0]
        elev = facoptions['elev'].iloc[0]
        acute_hours = facoptions['hours'].iloc[0]
        acute_multiplier = facoptions['multiplier'].iloc[0]
        bldgdw_yn = facoptions['bldg_dw'].iloc[0]
        userrcpt_yn = facoptions['user_rcpt'].iloc[0]
        overlap_dist = facoptions['overlap_dist'].iloc[0]
        num_rings = facoptions['circles'].iloc[0]
        num_radials = facoptions['radial'].iloc[0]
        acute_yn = facoptions['acute'].iloc[0]
        fastall = facoptions['fastall'].iloc[0]
        max_dist = facoptions['max_dist'].iloc[0]
        mod_dist = facoptions['model_dist'].iloc[0]
        allrecpts_yn = facoptions['all_rcpts'].iloc[0]
        first_ring = facoptions['ring1'].iloc[0]
        grpname = self.model.group_name  
        faclist_file = self.model.faclist.path
        emisloc_file = self.model.emisloc.path
        hapemis_file = self.model.hapemis.path
        
        user_rcpt_file = ''
        if self.model.ureceptr is not None:
            user_rcpt_file = self.model.ureceptr.path

        part_size_file = ''
        if self.model.partdep is not None:
            part_size_file = self.model.partdep.path

        bldg_file = ''
        if self.model.bldgdw is not None:
            bldg_file = self.model.bldgdw.path
        
        landuse_file = ''
        if self.model.landuse is not None:
            landuse_file = self.model.landuse.path

        season_file = ''
        if self.model.seasons is not None:
            season_file = self.model.seasons.path

        vertex_file = ''
        if self.model.multipoly is not None:
            vertex_file = self.model.multipoly.path

        blp_file = ''
        if self.model.multibuoy is not None:
            blp_file = self.model.multibuoy.path
        

        optioncols = ['facid', 'title2', 'phase', 'ruralurban', 'dep_yn', 'depl_yn', 'dep_type', 'depl_type',
                      'elev_yn', 'acute_hrs', 'acute_mult', 'bldgdw_yn', 'userrcpt_yn', 'max_dist',
                      'model_dist', 'overlap_dist', 'num_rings', 'num_radials', 'acute_yn',
                      'allrecpts_yn', 'first_ring', 'fastall_yn', 'grpname', 'faclist_file',
                      'emisloc_file', 'hapemis_file', 'usrrcpt_file', 'partsize_file', 'bldgdw_file',
                      'blp_file', 'landuse_file', 'seasons_file', 'vertex_file']
        
        
        optionlist = [[title1, title2, phase, ruralurban, dep_yn, depl_yn, dep_type, depl_type,
                      elev, acute_hours, acute_multiplier, bldgdw_yn, userrcpt_yn, max_dist, mod_dist,
                      overlap_dist, num_rings, num_radials, acute_yn, allrecpts_yn, first_ring, 
                      fastall, grpname, faclist_file, emisloc_file, hapemis_file, 
                      user_rcpt_file, part_size_file, bldg_file, blp_file, landuse_file, 
                      season_file, vertex_file]]
        
        df = DataFrame(optionlist, columns=optioncols)

        self.dataframe = df
        self.data = df.values
        yield self.dataframe