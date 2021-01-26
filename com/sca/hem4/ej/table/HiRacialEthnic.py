from com.sca.ej.table.WorksheetTable import WorksheetTable


class HiRacialEthnic(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name):
        self.active_columns = [0, 1, 2, 3, 4, 5]
        self.prefix = prefix
        self.name = name
        WorksheetTable.__init__(self, radius=radius_value, source_category= source_category)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-1. Distribution of Hazard Indices for Racial and Ethnic Groups - ' + \
               self.radius + ' km Study Area Radius'

    def get_sub_header_1(self):
        return self.name + ' Hazard Index Ranges for the ' + self.source_category + ' Source Category'

    def get_sub_header_2(self):
        return 'Number of People within ' + self.radius + ' km of any Facility in Different Hazard Index Ranges \u1D43'

    def get_average_header(self):
        return "Average Hazard Index\u1D9C"

    def get_notes(self):
        return 'Notes:\n\n\u1D43 Distributions by race are based on demographic information at the census block ' + \
               'group level. Hazard indices for ' + self.source_category + ' emissions are modeled ' + \
               'at the census block level.\n' + \
               '\u1D47 In order to avoid double counting, the "Hispanic or Latino" category is treated as a ' + \
                'distinct demographic category for these analyses. A person is identified as one of five ' + \
               'racial/ethnic categories above: White, African American, Native American, Other and Multiracial, or' + \
                ' Hispanic/Latino.\n' + \
               '\u1D9C The population-weighted average hazard index takes into account hazard index levels at all ' + \
               'populated block receptors in the modeled domain for the entire source category.'

    def get_sheet_name(self):
        return 'Table' + self.identifier + '1NC'

    def get_columns(self):
        return ['Total Population', 'White', 'African American', 'Native American', 'Other and Multiracial',
                'Hispanic or Latino\u1D47']
