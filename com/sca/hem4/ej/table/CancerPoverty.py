from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class CancerPoverty(WorksheetTable):

    def __init__(self, radius_value, source_category, facility):
        self.name = None
        self.prefix = None
        self.active_columns = [0, 12, 11]
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to < 1', '1 to < 5', '5 to < 10', '10 to < 20', '20 to < 30', '30 to < 40', '40 to < 50',
                '50 to < 100', '100 to < 200', '200 to < 300', '>= 300']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-4. Distribution of Cancer Risk for People Living in Households Below Two Times ' + \
               'the Poverty Level and Below the Poverty Level - ' + self.radius + ' km Study Area Radius'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility

        return 'Range of Lifetime Individual Cancer Risk from ' + scope + ' (Chance in One Million) \u1D43'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Ranges for Lifetime Cancer Risk \u1D47'

    def get_average_header(self):
        return "Average Risk (Chance in One Million)\u1D43"

    def get_notes(self):
        return 'Notes:\n\n\u1D43 Modeled risks are for a 70-year lifetime, based on the predicted outdoor ' + \
               'concentration and not adjusted for exposure factors. Risks from ' + self.source_category + \
               ' emissions are modeled at the census block level.\n' + \
               '\u1D47Distributions by poverty status are based on poverty data at the census block group level.'

    def get_sheet_name(self):
        return 'Table' + self.identifier + '4C'

    def get_columns(self):
        return ['Total Population', 'People Living in Households with Income Below 2 Times the Poverty Level',
                'People Living in Households with Income Below the Poverty Level']

    def optional_format(self, worksheet):
        worksheet.set_row(0, 42)