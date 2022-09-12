from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class HiPoverty(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name, facility):
        self.active_columns = [0, 12, 11]
        self.prefix = prefix
        self.name = name
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-4. Distribution of Hazard Indices for People Living in Households Below Twice the ' + \
                'Poverty Level and Below the Poverty Level - ' + self.radius + ' km Study Area Radius'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return self.name + ' Hazard Index Ranges for ' + scope

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Hazard Index Ranges \u1D43'

    def get_average_header(self):
        return "Average Hazard Index\u1D47"

    def get_notes(self):
        return 'Notes:\n\n\u1D43 Distributions by education level are based on education data at the census block ' + \
               'group level. Hazard indices for ' + self.source_category + ' emissions are modeled ' + \
               'at the census block level.\n' + \
               '\u1D47 The population-weighted average hazard index takes into account hazard index levels at all ' + \
               'populated block receptors in the modeled domain for the entire source category.'

    def get_sheet_name(self):
        return 'Table' + self.identifier + '4NC'

    def get_columns(self):
        return ['Total Population', 'People Living in Households with Income Below Twice the Poverty Level',
                'People Living in Households with Income Below the Poverty Level']

    def optional_format(self, worksheet):
        worksheet.set_column("D1:E1", 20)
        worksheet.set_row(3, 40)
