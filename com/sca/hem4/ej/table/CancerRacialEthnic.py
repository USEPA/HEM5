from com.sca.ej.table.WorksheetTable import WorksheetTable


class CancerRacialEthnic(WorksheetTable):

    def __init__(self, radius_value, source_category):
        self.name = None
        self.prefix = None
        self.active_columns = [0, 1, 2, 3, 4, 5]
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category)

    def get_bin_headers(self):
        return ['0 to < 1', '1 to < 5', '5 to < 10', '10 to < 20', '20 to < 30', '30 to < 40', '40 to < 50',
                '50 to < 100', '100 to < 200', '200 to < 300', '>= 300']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-1. Distribution of Cancer Risk for Racial and Ethnic Groups - ' + \
               self.radius + ' km Study Area Radius'

    def get_sub_header_1(self):
        return 'Range of Lifetime Individual Cancer Risk from the ' + self.source_category + \
               ' Source Category (Chance in One Million) \u1D43'

    def get_sub_header_2(self):
        return 'Number of People within ' + self.radius + ' km of any Facility in Different Ranges for Lifetime ' + \
               'Cancer Risk \u1D47'

    def get_average_header(self):
        return "Average Risk (Chance in One Million)\u1D43"

    def get_notes(self):
        return 'Notes:\n\n\u1D43 Modeled risks are for a 70-year lifetime, based on the predicted outdoor ' + \
               'concentration and not adjusted for exposure factors. Risks from ' + self.source_category + \
               ' emissions are modeled at the census block level.\n' + \
               '\u1D47 Distributions by race are based on demographic information at the census block group level.\n' + \
                '\u1D9C In order to avoid double counting, the "Hispanic or Latino" category is treated as a ' + \
               'distinct demographic category for these analyses. A person is identified as one of five ' + \
               'racial/ethnic categories above: White, African American, Native American, Other and Multiracial, or' + \
               ' Hispanic/Latino.'

    def get_sheet_name(self):
        return 'Table' + self.identifier + '1C'

    def get_columns(self):
        return ['Total Population', 'White', 'African American', 'Native American', 'Other and Multiracial',
                'Hispanic or Latino\u1D9C']

