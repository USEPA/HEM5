import os

from numpy.core.multiarray import array
from pandas import DataFrame

from com.sca.hem4.log import Logger
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter

class InputSelectionOptions(ExcelWriter):
    """
    Provides the options and input file names specified by the user at the start of the run.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.facilityId = facilityId
        self.filename = os.path.join(targetDir, facilityId + "_input_selection_options.xlsx")

    def getHeader(self):
        return ['title1', 'title2', 'hap_phase', 'rural_urban', 'dep_yn', 'depl_yn', 'part_vap', 'dep', 'depl',
                'incl_elev', 'incl_hour', 'model status', 'hr_ratio', 'incl_bldg_dw', 'incl_size','user_rcpt', 'max_rad', 'min_rad', 'blk_dist',
                'ovrlap_dist', 'conc_cir', 'radials', 'emis_file', 'hap_emis_file', 'user_rcpt_file', 'part_size_file',
                'bldg_file', 'acute', 'acute hours', 'poll_type', 'done', 'num_of_runs', 'facil_number', 'multi_file',
                'all_receptors', 'pop_size', 'first_ring', 'landuse_file', 'season_file', 'vertex_file', 'diurnal', 'time_blks',
                'seas_var', 'emis_var', 'emis_var_file', 'results_temporal', 'fastall', 'flagpole', 'hremis_file', 'bldg_dw_so',
                'hour_emis', 'prefix', 'prefixyn', 'blp_file', 'reset']

    def generateOutputs(self):

        faclist = self.model.faclist.dataframe
        facoptions = faclist.loc[faclist.fac_id == self.facilityId].iloc[0]

        title1 = self.facilityId

        # Options that are in the faclist input file
        ruralurban = facoptions['rural_urban']
        phase = facoptions['phase']
        dep_yn = facoptions['dep']
        depl_yn = facoptions['depl']
        elev = facoptions['elev']
        hours = facoptions['hours']
        bldg_dw = facoptions['bldg_dw']
        user_rcpt = facoptions['user_rcpt']
        overlap_dist = facoptions['overlap_dist']
        conc_cir = facoptions['circles']
        radials = facoptions['radial']
        acute = facoptions['acute']
        fastall = facoptions['fastall']
        max_rad = facoptions['max_dist']
        facil_number = self.facilityId

        # Where oh where do you live?
        title2, part_vap, dep, depl, model_status, hr_ratio, incl_size, min_rad, blk_dist, acute_hours, \
        poll_type, done, num_of_runs, multi_file, all_receptors, pop_size, first_ring, diurnal, time_blks, \
        seas_var, emis_var, results_temporal, flagpole, bldg_dw_so, hour_emis, prefix, prefixyn, reset = ('?',)*28

        emis_file = self.model.haplib.path
        hap_emis_file = self.model.hapemis.path
        user_rcpt_file = ''
        if self.model.ureceptr is not None:
            user_rcpt_file = self.model.ureceptr.path

        part_size_file = ''
        if self.model.partdep is not None:
            part_size_file = self.model.partdep.path

        bldg_file = ''
        landuse_file = ''
        season_file = ''
        vertex_file = ''
        emis_var_file = ''
        hremis_file = ''
        blp_file = ''
        # if hasattr(self.model, '?'):
        #     bldg_file = self.model.partdep.path

        #'landuse_file', 'season_file', 'vertex_file' 'emis_var_file' 'hremis_file' 'blp_file'

        optionlist = [title1, title2, phase, ruralurban, dep_yn, depl_yn, part_vap, dep, depl,
                      elev, hours, model_status, hr_ratio, bldg_dw, incl_size, user_rcpt, max_rad, min_rad, blk_dist,
                      overlap_dist, conc_cir, radials, emis_file, hap_emis_file, user_rcpt_file, part_size_file,
                      bldg_file, acute, acute_hours, poll_type, done, num_of_runs, facil_number, multi_file,
                      all_receptors, pop_size, first_ring, landuse_file, season_file, vertex_file, diurnal, time_blks,
                      seas_var, emis_var, emis_var_file, results_temporal, fastall, flagpole, hremis_file, bldg_dw_so,
                      hour_emis, prefix, prefixyn, blp_file, reset]
        df = DataFrame(array(optionlist, ndmin=2), dtype="object")

        df.replace(to_replace='nan', value='', inplace=True)

        self.data = df.values
        yield self.dataframe