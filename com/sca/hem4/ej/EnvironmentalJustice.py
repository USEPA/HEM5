import os
from com.sca.hem4.ej.data.DataModel import DataModel
from com.sca.hem4.ej.ReportWriter import ReportWriter


class EnvironmentalJustice():

    def __init__(self, mir_rec_df, acs_df, levels_df, outputdir, source_cat_name, source_cat_prefix, radius,
                 requested_toshis):
        self.output_dir = outputdir
        self.source_cat = source_cat_name
        self.source_cat_prefix = source_cat_prefix
        self.radius = radius
        self.requested_toshis = requested_toshis

        # Create a data model to hold hazard and census demographic data
        self.data_model = DataModel(mir_rec_df=mir_rec_df, acs_df=acs_df, levels_df=levels_df, toshis=requested_toshis,
                                    missing_block_path=outputdir)

    def create_reports(self):

        # First, create the output path if it doesn't exist
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        report_writer = ReportWriter(target_dir=self.output_dir, source_cat_prefix=self.source_cat_prefix,
                                     source_cat=self.source_cat, radius=self.radius)

        # Create cancer workbook...
        report_writer.create_cancer_workbook()
        report_writer.create_cancer_tables(values=self.data_model.cancer_bins)
        report_writer.create_cancer_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.cancer_bins,
                                              max_risk=self.data_model.max_risk['mir'])
        report_writer.close_workbook()

        # Create all requested TOSHI workbooks
        for key,value in self.requested_toshis.items():
            report_writer.create_toshi_workbook(key, value)
            report_writer.create_hi_tables(values=self.data_model.toshi_bins[key])
            report_writer.create_hi_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.toshi_bins[key],
                                              max_risk=self.data_model.max_risk[key])
            report_writer.close_workbook()
