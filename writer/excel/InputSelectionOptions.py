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

        options = self.model.faclist.dataframe.loc[self.model.faclist.dataframe.fac_id == self.facilityId]

        ruralurban = options.iloc[0]['rural_urban']
        df = DataFrame(array(['','','','','',ruralurban], ndmin=2), dtype="object")

        df.replace(to_replace='nan', value='', inplace=True)

        self.data = df.values