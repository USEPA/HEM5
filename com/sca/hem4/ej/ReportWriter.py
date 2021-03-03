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
import com.sca.hem4.ej.table.CancerRacialEthnic as cancerRacialEthnicModule
import com.sca.hem4.ej.table.CancerAgeGroups as cancerAgeGroupsModule
import com.sca.hem4.ej.table.CancerDiploma as cancerDiplomaModule
import com.sca.hem4.ej.table.CancerPoverty as cancerPovertyModule
import com.sca.hem4.ej.table.CancerLinguisticIsolation as cancerLinguisticIsolationModule


class ReportWriter():

    facility_summary_workbooks = {}

    def __init__(self, target_dir, source_cat, source_cat_prefix, radius, facility,
                 cancer_risk_threshold, hi_risk_threshold):
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

        self.hiSheets = {'HiRacialEthnic': hiRacialEthnicModule,
                         'HiAgeGroups': hiAgeGroupsModule,
                         'HiDiploma': hiDiplomaModule,
                         'HiPoverty': hiPovertyModule,
                         'HiLinguisticIsolation': hiLinguisticIsolationModule}

        self.cancerSheets = {'CancerRacialEthnic': cancerRacialEthnicModule,
                             'CancerAgeGroups': cancerAgeGroupsModule,
                             'CancerDiploma': cancerDiplomaModule,
                             'CancerPoverty': cancerPovertyModule,
                             'CancerLinguisticIsolation': cancerLinguisticIsolationModule}

    def create_cancer_workbook(self):
        filename = self.construct_filename(cancer=True)
        self.workbook = xlsxwriter.Workbook(filename)
        self.formats = self.create_formats(self.workbook)

    def create_toshi_workbook(self, prefix, name):
        self.hazard_prefix = prefix
        self.hazard_name = name
        filename = self.construct_filename(cancer=False)
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
            'valign': 'vcenter'})

        formats['notes'] = workbook.add_format({
            'font_size': 12,
            'bold': 0,
            'align': 'left',
            'valign': 'top',
            'text_wrap': 1})

        formats['number'] = workbook.add_format({
            'num_format': '#,##0'})

        formats['percentage'] = workbook.add_format({
            'num_format': '0.0%'})

        formats['int_percentage'] = workbook.add_format({
            'num_format': '0%'})

        return formats

    def construct_filename(self, cancer=True):
        hazard_type = 'EJ_Cancer' if cancer else self.hazard_prefix + '_Noncancer'
        date_string = datetime.datetime.now().strftime("%m-%d-%Y")
        facility_name = '' if self.facility is None else self.facility + '_'
        risk = str(self.cancer_risk_threshold) if cancer else str(self.hi_risk_threshold)
        return os.path.join(self.output_dir, self.source_cat_prefix + '_' + facility_name + str(self.radius) +
                            '_km_' + risk + '_' + hazard_type + '_demo_tables_' + date_string + '.xlsx')

    def construct_facility_summary_filename(self, cancer=True, hazard_prefix=None):
        hazard_type = '_Cancer_' if cancer else hazard_prefix + '_Noncancer_'
        date_string = datetime.datetime.now().strftime("%m-%d-%Y")
        facility_name = '' if self.facility is None else self.facility + '_'

        return os.path.join(self.output_dir, self.source_cat_prefix + '_' + facility_name + 'EJ-Summary_' +
                            str(self.radius) + '_km_' + hazard_type + date_string + '.xlsx')

    def create_cancer_summaries(self, national_values, values, max_risk):
        dg_summary = CancerDGSummary(radius=self.radius, source_category=self.source_cat, facility=self.facility)
        dg_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, values=values)

        kc_summary = CancerKCSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                     hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                     facility=self.facility)
        kc_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, values=values, max_value=max_risk)

        elaine_summary = CancerElaineSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                             hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                             facility=self.facility)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, values=values)

    def create_hi_summaries(self, national_values, values, max_risk):
        dg_summary = HiDGSummary(radius=self.radius, source_category=self.source_cat, facility=self.facility)
        dg_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name,
                                  formats=self.formats, national_values=national_values, values=values)

        kc_summary = HiKCSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                 hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                 facility=self.facility)
        kc_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name, formats=self.formats,
                                  national_values=national_values, values=values, max_value=max_risk)

        elaine_summary = HiElaineSummary(radius=self.radius, cancer_risk_threshold=self.cancer_risk_threshold,
                                         hi_risk_threshold=self.hi_risk_threshold, source_category=self.source_cat,
                                         hazard_name=self.hazard_name, facility=self.facility)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, values=values)

    @staticmethod
    def init_facility_summaries():
        ReportWriter.facility_summary_workbooks = {}

    # Create facility summary workbooks as needed that will eventually be populated with facility summary data
    def create_facility_summaries(self, toshis):

        if self.radius not in ReportWriter.facility_summary_workbooks.keys():
            # Create workbooks for this radius/risk combination. Note that the class-level data
            # structure that stores workbooks ("facility_summary_workbooks") is keyed by radius and contains a list
            # that looks like this: [cancer_workbook, toshi_1_workbook, toshi_2_workbook, ...]
            workbooks = []
            cancer_filename = self.construct_facility_summary_filename(cancer=True)
            new_workbook = xlsxwriter.Workbook(cancer_filename)
            self.create_formats(new_workbook)
            workbooks.append(new_workbook)
            for toshi in toshis:
                toshi_filename = self.construct_facility_summary_filename(cancer=False, hazard_prefix=toshi)
                new_workbook = xlsxwriter.Workbook(toshi_filename)
                self.create_formats(new_workbook)
                workbooks.append(new_workbook)

            ReportWriter.facility_summary_workbooks[self.radius] = workbooks

    def add_cancer_facility_summaries(self, national_values, values, run_group_values):
        # Retrieve the workbooks that correspond to this radius
        workbook = ReportWriter.facility_summary_workbooks[self.radius][0]
        formats = self.create_formats(workbook)

        # For each workbook, add an appropriately named sheet if it doesn't exist
        cancer_fac_summary = CancerFacilitySummary(facilityId=self.facility, radius=self.radius,
                                                   cancer_risk_threshold=self.cancer_risk_threshold,
                                                   hi_risk_threshold=self.hi_risk_threshold,
                                                   source_category=self.source_cat)
        cancer_fac_summary.create_summary(workbook=workbook, hazard_name=self.hazard_name, formats=formats,
                                          national_values=national_values, values=values,
                                          run_group_values=run_group_values)

    def add_hi_facility_summaries(self, national_values, values, run_group_values, toshis):

        toshi_index = 1
        for toshi in toshis:
            # Retrieve the workbook that correspond to this radius / toshi
            workbook = ReportWriter.facility_summary_workbooks[self.radius][toshi_index]
            formats = self.create_formats(workbook)

            # For each workbook, add an appropriately named sheet if it doesn't exist
            hi_fac_summary = HiFacilitySummary(facilityId=self.facility, radius=self.radius,
                                               cancer_risk_threshold=self.cancer_risk_threshold,
                                               hi_risk_threshold=self.hi_risk_threshold,
                                               source_category=self.source_cat)
            hi_fac_summary.create_summary(workbook=workbook, hazard_name=self.hazard_name, formats=formats,
                                      national_values=national_values, values=values[toshi],
                                          run_group_values=run_group_values[toshi])

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
