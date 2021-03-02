import os
from com.sca.hem4.ej.data.DataModel import DataModel
from com.sca.hem4.ej.ReportWriter import ReportWriter


class EnvironmentalJustice():

    def __init__(self, mir_rec_df, acs_df, levels_df, outputdir, source_cat_name, source_cat_prefix, radius,
                 cancer_risk_threshold, hi_risk_threshold, requested_toshis, facility=None):
        self.output_dir = outputdir
        self.source_cat = source_cat_name
        self.source_cat_prefix = source_cat_prefix
        self.radius = radius
        self.facility = facility
        self.cancer_risk_threshold = cancer_risk_threshold
        self.hi_risk_threshold = hi_risk_threshold
        self.requested_toshis = requested_toshis

        missing_block_path = outputdir

        # Create a data model to hold hazard and census demographic data
        self.data_model = DataModel(mir_rec_df=mir_rec_df, acs_df=acs_df, levels_df=levels_df, toshis=requested_toshis,
                                    missing_block_path=missing_block_path, radius=radius, facility=facility)

        self.report_writer = ReportWriter(target_dir=self.output_dir, source_cat_prefix=self.source_cat_prefix,
                                     source_cat=self.source_cat, radius=self.radius, facility=facility,
                                     cancer_risk_threshold=self.cancer_risk_threshold,
                                     hi_risk_threshold=self.hi_risk_threshold)

    def create_reports(self):

        # First, create the output path if it doesn't exist
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Create cancer workbook...
        self.report_writer.create_cancer_workbook()
        self.report_writer.create_cancer_tables(values=self.data_model.cancer_bins)
        self.report_writer.create_cancer_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.cancer_bins,
                                              max_risk=self.data_model.max_risk['mir'])
        self.report_writer.close_workbook()

        # Create all requested TOSHI workbooks
        for key,value in self.requested_toshis.items():
            self.report_writer.create_toshi_workbook(key, value)
            self.report_writer.create_hi_tables(values=self.data_model.toshi_bins[key])
            self.report_writer.create_hi_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.toshi_bins[key],
                                              max_risk=self.data_model.max_risk[key])
            self.report_writer.close_workbook()

    def create_facility_summaries(self):
        # First, create the output path if it doesn't exist
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        # Create new facility summary workbooks and sheets if necessary
        self.report_writer.create_facility_summaries(toshis=self.requested_toshis)
        
    def add_facility_summaries(self, run_group_data_model):
        self.report_writer.add_cancer_facility_summaries(national_values=self.data_model.national_bin,
                                                         values=self.data_model.cancer_bins,
                                                         run_group_values=run_group_data_model.cancer_bins)

        self.report_writer.add_hi_facility_summaries(national_values=self.data_model.national_bin,
                                                     values=self.data_model.toshi_bins,
                                                     run_group_values=run_group_data_model.toshi_bins,
                                                     toshis=self.requested_toshis)

    def close_facility_summaries(self):
        self.report_writer.close_all_workbooks()