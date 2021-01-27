import os
import datetime
import xlsxwriter
from com.sca.hem4.ej.summary.CancerDGSummary import CancerDGSummary
from com.sca.hem4.ej.summary.CancerElaineSummary import CancerElaineSummary
from com.sca.hem4.ej.summary.CancerKCSummary import CancerKCSummary
from com.sca.hem4.ej.summary.HiDGSummary import HiDGSummary
from com.sca.hem4.ej.summary.HiElaineSummary import HiElaineSummary
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

    def __init__(self, target_dir, source_cat, source_cat_prefix, radius):
        self.output_dir = target_dir
        self.source_cat = source_cat
        self.source_cat_prefix = source_cat_prefix
        self.radius = radius
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
        self.create_formats()

    def create_toshi_workbook(self, prefix, name):
        self.hazard_prefix = prefix
        self.hazard_name = name
        filename = self.construct_filename(cancer=False)
        self.workbook = xlsxwriter.Workbook(filename)
        self.create_formats()

    def close_workbook(self):
        if self.workbook is not None:
            self.workbook.close()

    def create_formats(self):
        formats = {}
        formats['top_header'] = self.workbook.add_format({
            'bold': 1,
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_1'] = self.workbook.add_format({
            'bold': 0,
            'bottom': 1,
            'align': 'center',
            'valign': 'bottom',
            'text_wrap': 1})

        formats['sub_header_2'] = self.workbook.add_format({
            'bold': 0,
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_3'] = self.workbook.add_format({
            'bold': 0,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': 1})

        formats['sub_header_4'] = self.workbook.add_format({
            'bold': 1,
            'align': 'left',
            'valign': 'vcenter'})

        formats['notes'] = self.workbook.add_format({
            'font_size': 12,
            'bold': 0,
            'align': 'left',
            'valign': 'top',
            'text_wrap': 1})

        formats['number'] = self.workbook.add_format({
            'num_format': '#,##0'})

        formats['percentage'] = self.workbook.add_format({
            'num_format': '0.0%'})

        formats['int_percentage'] = self.workbook.add_format({
            'num_format': '0%'})

        self.formats = formats

    def construct_filename(self, cancer=True):
        hazard_type = 'EJ_Cancer' if cancer else self.hazard_prefix + '_Noncancer'
        date_string = datetime.datetime.now().strftime("%m-%d-%Y")
        return os.path.join(self.output_dir, self.source_cat_prefix + '_' + str(self.radius) +
                            '_km_' + hazard_type + '_demo_tables_' + date_string + '.xlsx')

    def create_cancer_summaries(self, national_values, values, max_risk):
        dg_summary = CancerDGSummary(radius=self.radius, source_category=self.source_cat)
        dg_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, values=values)

        kc_summary = CancerKCSummary(radius=self.radius, source_category=self.source_cat)
        kc_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                  national_values=national_values, values=values, max_value=max_risk)

        elaine_summary = CancerElaineSummary(radius=self.radius, source_category=self.source_cat)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, values=values)

    def create_hi_summaries(self, national_values, values, max_risk):
        dg_summary = HiDGSummary(radius=self.radius, source_category=self.source_cat)
        dg_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name,
                                  formats=self.formats, national_values=national_values, values=values)

        kc_summary = HiKCSummary(radius=self.radius, source_category=self.source_cat)
        kc_summary.create_summary(workbook=self.workbook, hazard_name=self.hazard_name, formats=self.formats,
                                  national_values=national_values, values=values, max_value=max_risk)

        elaine_summary = HiElaineSummary(radius=self.radius, source_category=self.source_cat,
                                         hazard_name=self.hazard_name)
        elaine_summary.create_summary(workbook=self.workbook, formats=self.formats,
                                      national_values=national_values, values=values)

    def create_hi_tables(self, values):
        for key, value in self.hiSheets.items():
            table_class = getattr(value, key)
            instance = table_class(self.radius, self.source_cat, self.hazard_prefix, self.hazard_name)
            instance.create_table(workbook=self.workbook, formats=self.formats, values=values)

    def create_cancer_tables(self, values):
        for key, value in self.cancerSheets.items():
            table_class = getattr(value, key)
            instance = table_class(self.radius, self.source_cat)
            instance.create_table(workbook=self.workbook, formats=self.formats, values=values)
