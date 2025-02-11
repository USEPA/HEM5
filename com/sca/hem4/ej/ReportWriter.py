import os
import datetime
import xlsxwriter
from com.sca.hem4.ej.summary.CancerDGSummary import CancerDGSummary
from com.sca.hem4.ej.summary.CancerElaineSummary import CancerElaineSummary
from com.sca.hem4.ej.summary.CancerFacilitySummary import CancerFacilitySummary
from com.sca.hem4.ej.summary.CancerKCSummary import CancerKCSummary
from com.sca.hem4.ej.summary.HiDGSummary import HiDGSummary
from com.sca.hem4.ej.summary.HiElaineSummary import HiElaineSummary
from com.sca.hem4.ej.summary.HiFacilitySummary import HiFacilitySummary
from com.sca.hem4.ej.summary.HiKCSummary import HiKCSummary
import com.sca.hem4.ej.table.HiRacialEthnic as hiRacialEthnicModule
import com.sca.hem4.ej.table.HiAgeGroups as hiAgeGroupsModule
import com.sca.hem4.ej.table.HiDiploma as hiDiplomaModule
import com.sca.hem4.ej.table.HiPoverty as hiPovertyModule
import com.sca.hem4.ej.table.HiLinguisticIsolation as hiLinguisticIsolationModule
import com.sca.hem4.ej.table.HiDisabilities as hiDisabilitiesModule
import com.sca.hem4.ej.table.CancerRacialEthnic as cancerRacialEthnicModule
import com.sca.hem4.ej.table.CancerAgeGroups as cancerAgeGroupsModule
import com.sca.hem4.ej.table.CancerDiploma as cancerDiplomaModule
import com.sca.hem4.ej.table.CancerPoverty as cancerPovertyModule
import com.sca.hem4.ej.table.CancerLinguisticIsolation as cancerLinguisticIsolationModule
import com.sca.hem4.ej.table.CancerDisabilities as cancerDisabilitiesModule


# The class that provides methods for creating/closing workbooks and adding information to them.
class ReportWriter():

    # Class-level data structure that maintains facility specific workbooks across instances of ReportWriter so that
    # facility data can be appended as we iterate.
    facility_summary_workbooks = {}

    def __init__(self, target_dir, source_cat, source_cat_prefix, radius, facility,
                 cancer_risk_threshold, hi_risk_threshold, write_notes):
        self.output_dir = target_dir
        self.source_cat = source_cat
        self.source_cat_prefix = source_cat_prefix
        self.cancer_risk_threshold = cancer_risk_threshold
        self.hi_risk_threshold = hi_risk_threshold
        self.radius = radius
        self.facility = facility
        self.workbook = None
        self.formats = None
        self.hazard_prefix = None
        self.hazard_name = None
        self.write_notes = write_notes

        self.hiSheets = {'HiRacialEthnic': hiRacialEthnicModule,
                         'HiAgeGroups': hiAgeGroupsModule,
                         'HiDiploma': hiDiplomaModule,
                         'HiPoverty': hiPovertyModule,
                         'HiLinguisticIsolation': hiLinguisticIsolationModule,
                         'HiDisabilities': hiDisabilitiesModule}

        self.cancerSheets = {'CancerRacialEthnic': cancerRacialEthnicModule,
                             'CancerAgeGroups': cancerAgeGroupsModule,
                             'CancerDiploma': cancerDiplomaModule,
                             'CancerPoverty': cancerPovertyModule,
                             'CancerLinguisticIsolation': cancerLinguisticIsolationModule,
                             'CancerDisabilities': cancerDisabilitiesModule}

    def create_cancer_workbook(self):
        filename = ReportWriter.construct_filename(self.hazard_prefix, self.facility, self.cancer_risk_threshold,
                                                   self.hi_risk_threshold, self.output_dir, self.source_cat_prefix,
                                                   self.radius, cancer=True)
        self.workbook = xlsxwriter.Workbook(filename)
        self.formats = self.create_formats(self.workbook)

    def create_toshi_workbook(self, prefix, name):
        self.hazard_prefix = prefix
        self.hazard_name = name
        filename = ReportWriter.construct_filename(self.hazard_prefix, self.facility, self.cancer_risk_threshold,
                                                   self.hi_risk_threshold, self.output_dir, self.source_cat_prefix,
                                                   self.radius, cancer=False)

        self.workbook = xlsxwriter.Workbook(filename)
        self.formats = self.create_formats(self.workbook)

    def close_workbook(self):
        if self.workbook is not None:
            self.workbook.close()

    def close_all_workbooks(self):
        self.close_workbook()

        for wb_list in ReportWriter.facility_summary_workbooks.values():
            for wb in wb_list:
                wb.close()

        ReportWriter.init_facility_summaries()

    # Create formats related to font, formatting, etc. that are used in Excel worksheets.
    def create_formats(self, workbook):
        formats = {}

        formats['top_header'] = workbook.add_format({
            'bold': 1,
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_1'] = workbook.add_format({
            'bold': 0,
            'bottom': 1,
            'align': 'center',
            'valign': 'bottom',
            'text_wrap': 1})

        formats['sub_header_2'] = workbook.add_format({
            'bold': 0,
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_3'] = workbook.add_format({
            'bold': 0,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_4'] = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_5'] = workbook.add_format({
            'bold': 0,
            'align': 'center',
            'valign': 'vcenter'})

        formats['sub_header_6'] = workbook.add_format({
            'bold': 0,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_7'] = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': 0})

        formats['notes'] = workbook.add_format({
            'font_size': 11,
            'bold': 0,
            'align': 'left',
            'valign': 'top',
            'text_wrap': 1})

        formats['wrap'] = workbook.add_format({
            'text_wrap': 1})

        formats['number'] = workbook.add_format({
            'num_format': '#,##0'})

        formats['percentage'] = workbook.add_format({
            'num_format': '0.0%'})

        formats['int_percentage'] = workbook.add_format({
            'num_format': '0%'})
        
        formats['superscript'] = workbook.add_format({'font_script': 1})

        formats['asterik'] = workbook.add_format({'bold': 1, 'font_size': 14})
        
        formats['vcenter'] = workbook.add_format({'valign': 'vcenter'})
        
        formats['bottom_border'] = workbook.add_format({'bottom': 1})

        formats['wrap_w_bottom'] = workbook.add_format({
            'text_wrap': 1,
            'bottom': 1})

        formats['percentage_w_bottom'] = workbook.add_format({
            'num_format': '0.0%',
            'bottom': 1})

        return formats

    @staticmethod
    def construct_filename(hazard_prefix=None, facility=None, cancer_risk_threshold=None, hi_risk_threshold=None,
                           output_dir=None, source_cat_prefix=None, radius=None, cancer=True):
        # Test_50_km_1_pop_Neur_demo_tables_date.xlsx

        hazard_type = 'pop_Cancer' if cancer else 'pop_' + hazard_prefix
        date_string = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        facility_name = '' if facility is None else facility + '_'
        risk = str(cancer_risk_threshold) if cancer else str(hi_risk_threshold)
        return os.path.join(output_dir, source_cat_prefix + '_' + facility_name + str(int(radius)) +
                            '_km_' + risk + '_' + hazard_type + '_demo_tables_' + date_string + '.xlsx')

    @staticmethod
    def construct_facility_summary_filename(hazard_prefix=None, facility=None,
                                            output_dir=None, source_cat_prefix=None, radius=None, cancer=True):
        hazard_type = 'Cancer_' if cancer else hazard_prefix + '_'
        date_string = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        facility_name = '' if facility is None else facility + '_'

        return os.path.join(output_dir, source_cat_prefix + '_' + facility_name + 'Pop-Summary_' +
                            str(int(radius)) + '_km_' + hazard_type + date_string + '.xlsx')


    def create_cancer_summaries(self, national_values, state_values, county_values, values, max_risk):
        dg_summary = CancerDGSummary(radius=self.radius, source_category=self.source_cat, facility=self.facility)
        dg_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, state_values=state_values,
                                  county_values=county_values, values=values)

        kc_summary = CancerKCSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                     hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                     facility=self.facility)
        kc_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, state_values=state_values,
                                  county_values=county_values, values=values, max_value=max_risk)

        elaine_summary = CancerElaineSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                             hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                             facility=self.facility)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, state_values=state_values,
                                      county_values=county_values, values=values)

    def create_hi_summaries(self, national_values, state_values, county_values, values, max_risk):
        dg_summary = HiDGSummary(radius=self.radius, source_category=self.source_cat, facility=self.facility)
        dg_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name,
                                  formats=self.formats, national_values=national_values,
                                  state_values=state_values, county_values=county_values, values=values)

        kc_summary = HiKCSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                 hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                 facility=self.facility)
        kc_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name, formats=self.formats,
                                  national_values=national_values, state_values=state_values,
                                  county_values=county_values, values=values, max_value=max_risk)

        elaine_summary = HiElaineSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                         hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                         hazard_name=self.hazard_name, facility=self.facility)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, state_values=state_values,
                                      county_values=county_values, values=values)

    @staticmethod
    def init_facility_summaries():
        ReportWriter.facility_summary_workbooks = {}

    # Create facility summary workbooks as needed that will eventually be populated with facility summary data
    def create_facility_summaries(self, toshis, cancer_selected):

        workbook_key = str(self.radius) + ("cancer" if cancer_selected else "hi")
        if workbook_key not in ReportWriter.facility_summary_workbooks.keys():
            # Create workbooks for this radius/risk combination. Note that the class-level data
            # structure that stores workbooks ("facility_summary_workbooks") is keyed by radius and contains a list
            # that looks like this: [cancer_workbook, toshi_1_workbook, toshi_2_workbook, ...]
            workbooks = []

            if cancer_selected:
                cancer_filename =\
                    ReportWriter.construct_facility_summary_filename(None, self.facility,
                                                                     self.output_dir, self.source_cat_prefix,
                                                                     self.radius, cancer=True)
                new_workbook = xlsxwriter.Workbook(cancer_filename)
                self.create_formats(new_workbook)
                workbooks.append(new_workbook)

            if not cancer_selected:
                for toshi in toshis:
                    toshi_filename =\
                        self.construct_facility_summary_filename(toshi, self.facility,
                                                                 self.output_dir, self.source_cat_prefix,
                                                                 self.radius, cancer=False)
                    new_workbook = xlsxwriter.Workbook(toshi_filename)
                    self.create_formats(new_workbook)
                    workbooks.append(new_workbook)

            ReportWriter.facility_summary_workbooks[workbook_key] = workbooks

    def add_cancer_facility_summaries(self, national_values, state_values, county_values, values, run_group_values):
        # Retrieve the workbook that corresponds to this radius
        workbook_key = str(self.radius) + "cancer"
        workbook = ReportWriter.facility_summary_workbooks[workbook_key][0]
        formats = self.create_formats(workbook)

        # For each workbook, add an appropriately named sheet if it doesn't exist
        cancer_fac_summary = CancerFacilitySummary(facilityId=self.facility, radius=self.radius,
                                                   cancer_risk_threshold=self.cancer_risk_threshold,
                                                   hi_risk_threshold=self.hi_risk_threshold,
                                                   source_category=self.source_cat)
        cancer_fac_summary.create_summary(workbook=workbook, hazard_name=None, formats=formats,
                                          national_values=national_values, state_values=state_values,
                                          county_values=county_values, values=values,
                                          run_group_values=run_group_values,
                                          write_notes=self.write_notes)

    def add_hi_facility_summaries(self, national_values, state_values, county_values, values, run_group_values, toshis):

        toshi_index = 0
        # toshis data structure has key/value pairs corresponding to prefix / hazard name
        for key,value in toshis.items():
            # Retrieve the workbook that corresponds to this radius / toshi
            workbook_key = str(self.radius) + "hi"
            workbook = ReportWriter.facility_summary_workbooks[workbook_key][toshi_index]
            formats = self.create_formats(workbook)

            # For each workbook, add an appropriately named sheet if it doesn't exist
            hi_fac_summary = HiFacilitySummary(facilityId=self.facility, radius=self.radius,
                                               cancer_risk_threshold=self.cancer_risk_threshold,
                                               hi_risk_threshold=self.hi_risk_threshold,
                                               source_category=self.source_cat)
            hi_fac_summary.create_summary(workbook=workbook, hazard_name=value, formats=formats,
                                          national_values=national_values, state_values=state_values,
                                          county_values=county_values, values=values[key],
                                          run_group_values=run_group_values[key],
                                          write_notes=self.write_notes)

            toshi_index += 1

    def create_hi_tables(self, values):
        for key, value in self.hiSheets.items():
            table_class = getattr(value, key)
            instance = table_class(self.radius, self.source_cat, self.hazard_prefix, self.hazard_name, self.facility)
            instance.create_table(workbook=self.workbook, formats=self.formats, values=values)

    def create_cancer_tables(self, values):
        for key, value in self.cancerSheets.items():
            table_class = getattr(value, key)
            instance = table_class(self.radius, self.source_cat, self.facility)
            instance.create_table(workbook=self.workbook, formats=self.formats, values=values)
