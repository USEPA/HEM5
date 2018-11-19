import os

from numpy.core.multiarray import array
from pandas import DataFrame

from log import Logger
from writer.excel.ExcelWriter import ExcelWriter

class InputSelectionOptions(ExcelWriter):
    """
    Provides the options and input file names specified by the user at the start of the run.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.facilityId = facilityId
        self.filename = os.path.join(targetDir, facilityId + "_input_selection_options.xlsx")

    def calculateOutputs(self):

        self.headers = ['title1', 'title2', 'inhalation', 'multi_media', 'hap_phase', 'rural_urban', 'air_conc',
                        'dep_yn', 'depl_yn', 'part_vap', 'dep_prmt', 'dep', 'depl_prmt', 'depl', 'incl_elev',
                        'incl_hour', 'model status', 'hr_ratio', 'incl_bldg_dw', 'incl_size', 'user_rcpt', 'new_urfs',
                        'nurfs_file', 'rev_urfs', 'max_rad', 'min_rad', 'blk_dist', 'ovrlap_dist', 'conc_cir', 'radials',
                        'emis_file', 'hap_emis_file', 'user_rcpt_file', 'part_size_file', 'hour_temp_file', 'bldg_file',
                        'chronic', 'acute', 'acute hours', 'poll_type', 'done', 'nad', 'num_of_runs', 'polar_change',
                        'mode', 'aermod', 'facil_number', 'multi_file', 'crystal_ball', 'all_receptors', 'pop_size',
                        'first_ring', 'landuse_file', 'season_file', 'vertex_file', 'diurnal', 'time_blks', 'seas_var',
                        'emis_var', 'emis_var_file', 'results_temporal', 'census_year', 'fastall', 'flagpole',
                        'bldg_dw_so', 'hremis_file', 'hour_emis', 'prefix', 'prefixyn', 'm_usr_rcpt', 'm_dep_depl',
                        'm_prt_size', 'm_season', 'm_landuse', 'blp_file', 'csv_output', 'reset']

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
        facil_number = self.facilityId

        # Where oh where do you live?
        title2, inhalation, multimedia = ('?',)*3
        air_conc, part_vap, dep_prmt, dep, depl_prmt, depl = ('?',)*6
        model_status, hr_ratio, incl_size, new_urfs, nurfs_file, rev_urfs = ('?',)*6
        max_rad, min_rad, blk_dist, chronic, acute_hours = ('?',)*5
        poll_type, done, nad, num_of_runs = ('?',)*4
        polar_change, mode, aermod, multi_file, crystal_ball = ('?',)*5
        all_receptors, pop_size, first_ring, diurnal, time_blks = ('?',)*5
        seas_var, emis_var, results_temporal, census_year = ('?',)*4
        flagpole, bldg_dw_so, hour_emis, prefix, prefixyn = ('?',)*5
        m_usr_rcpt, m_dep_depl, m_prt_size, m_season, m_landuse, csv_output, reset = ('?',)*7

        emis_file = self.model.haplib.path
        hap_emis_file = self.model.hapemis.path
        user_rcpt_file = ''
        if self.model.ureceptr is not None:
            user_rcpt_file = self.model.ureceptr.path

        part_size_file = ''
        if self.model.partdep is not None:
            part_size_file = self.model.partdep.path

        hour_temp_file = ''
        # if hasattr(self.model, '?'):
        #     hour_temp_file = self.model.partdep.path

        bldg_file = ''
        # if hasattr(self.model, '?'):
        #     bldg_file = self.model.partdep.path

        #'landuse_file', 'season_file', 'vertex_file' 'emis_var_file' 'hremis_file' 'blp_file'

        optionlist = [title1,title2,inhalation,multimedia,phase,ruralurban, air_conc, dep_yn, depl_yn, part_vap,
                      dep_prmt, dep, depl_prmt, depl, elev, hours, model_status, hr_ratio, bldg_dw, incl_size,
                      user_rcpt, new_urfs, nurfs_file, rev_urfs, max_rad, min_rad, blk_dist, overlap_dist, conc_cir,
                      radials, emis_file, hap_emis_file, user_rcpt_file, part_size_file, hour_temp_file, bldg_file,
                      chronic, acute, acute_hours, poll_type, done, nad, num_of_runs, polar_change, mode, aermod,
                      facil_number, multi_file, crystal_ball, all_receptors, pop_size, first_ring, diurnal, time_blks,
                      seas_var, emis_var, results_temporal, census_year, fastall, flagpole, bldg_dw_so, hour_emis,
                      prefix, prefixyn, m_usr_rcpt, m_dep_depl, m_prt_size, m_season, m_landuse, csv_output, reset]
        df = DataFrame(array(optionlist, ndmin=2), dtype="object")

        df.replace(to_replace='nan', value='', inplace=True)

        self.data = df.values