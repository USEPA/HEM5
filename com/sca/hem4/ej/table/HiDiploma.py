from com.sca.ej.table.WorksheetTable import WorksheetTable


class HiDiploma(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name):
        self.active_columns = [0, 9, 10]
        self.prefix = prefix
        self.name = name
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-3. Distribution of Hazard Indices for Adults without a High School Diploma - ' + \
               self.radius + ' km Study Area Radius'

    def get_sub_header_1(self):
        return self.name + ' Hazard Index Ranges for the ' + self.source_category + ' Source Category'

    def get_sub_header_2(self):
        return 'Number of People within ' + self.radius + ' km of any Facility in Different Hazard Index Ranges \u1D43'

    def get_average_header(self):
        return "Average Hazard Index\u1D47"

    def get_notes(self):
        return 'Notes:\n\n\u1D43 Distributions by education level are based on education data at the census block ' + \
               'group level. Hazard indices for ' + self.source_category + ' emissions are modeled ' + \
               'at the census block level.\n' + \
               '\u1D47 The population-weighted average hazard index takes into account hazard index levels at all ' + \
               'populated block receptors in the modeled domain for the entire source category.'

    def get_sheet_name(self):
        return 'Table' + self.identifier + '3NC'

    def get_columns(self):
        return ['Total Population', 'Number >= 25 Years Old', 'Number >= 25 Years Old without a High School Diploma']

    def optional_format(self, worksheet):
        worksheet.set_column("E1:E1", 18)
