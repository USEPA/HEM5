import datetime
import os
from com.sca.ej.data.DataModel import DataModel
from com.sca.ej.ReportWriter import ReportWriter

rec_path = r"C:\Git_HEM4\HEM4\output\PrimCopperActual\MIR_HI_allreceptors_50km.csv"
acs_path = r"C:\ejtool\ejtool\ACS Data\ACS18BGEstimates_EJsubset_wb.xlsx"
acs_level_path = r"C:\ejtool\ejtool\ACS Data\ACS-tract-county_wb.xlsx"
output_directory = r"C:\Git_HEM4\HEM4\output\PrimCopperActual"
source_category_name = "Primary Copper Actual"
source_category_prefix = "PrimCopperActual"
radius_value = 50
requested_toshis = {'Deve':'Developmental', 'Neur':'Neurological', 'Resp':'Respiratory', 'Skel':'Skeletal'}

class EnvironmentalJustice():

    def __init__(self, mir_receptors_path, acs_dataset_path, outputdir, source_cat_name, source_cat_prefix, radius,
                 requested_toshi):
        self.output_dir = outputdir
        self.source_cat = source_cat_name
        self.source_cat_prefix = source_cat_prefix
        self.radius = radius
        self.requested_toshi = requested_toshi

        # Create a data model to hold hazard and census demographic data
        self.data_model = DataModel(mir_rec_path=mir_receptors_path, acs_path=acs_dataset_path,
                                    levels_path=acs_level_path, toshis=requested_toshis)

    def create_reports(self):

        # First, create the output path if it doesn't exist
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        report_writer = ReportWriter(target_dir=self.output_dir, source_cat_prefix=self.source_cat_prefix,
                                     source_cat=self.source_cat, radius=radius_value)

        # Create cancer workbook...
        report_writer.create_cancer_workbook()
        report_writer.create_cancer_tables(values=self.data_model.cancer_bins)
        report_writer.create_cancer_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.cancer_bins,
                                              max_risk=self.data_model.max_risk['mir'])
        report_writer.close_workbook()

        # Create all requested TOSHI workbooks
        for key,value in self.requested_toshi.items():
            report_writer.create_toshi_workbook(key, value)
            report_writer.create_hi_tables(values=self.data_model.toshi_bins[key])
            report_writer.create_hi_summaries(national_values=self.data_model.national_bin,
                                              values=self.data_model.toshi_bins[key],
                                              max_risk=self.data_model.max_risk[key])
            report_writer.close_workbook()


print (datetime.datetime.now())
justice = EnvironmentalJustice(outputdir=output_directory, mir_receptors_path=rec_path, acs_dataset_path=acs_path,
                               source_cat_name=source_category_name, source_cat_prefix=source_category_prefix,
                               radius=radius_value, requested_toshi=requested_toshis)
justice.create_reports()
print (datetime.datetime.now())
