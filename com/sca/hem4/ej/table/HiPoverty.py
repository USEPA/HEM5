from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class HiPoverty(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name, facility):
        self.active_columns = [0, 13, 12]
        self.prefix = prefix
        self.name = name
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table 4. Distribution of Hazard Indices for People Living in Households Below Twice the ' + \
               'Poverty Level and Below the Poverty Level - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return self.name + ' Hazard Index Ranges for ' + scope + ' \u1d47'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Hazard Index Ranges \u1D43'

    def get_average_header(self):
        return "Average " + self.name + " Hazard Index \u1D48"

    def get_notes(self):
        notes_dict = {'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated"
                      ,
                      'note1_a':"  radius, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"Hazard indices from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year"
                      ,
                      'note1_b':"  lifetime, and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      ,
                      'c':"The number of people living below the poverty line or below twice the poverty line are based on the American Community Survey at the block group"
                      ,
                      'note1_c':"  level that do not include people in group living situations such as dorms, prisons, nursing homes, and military barracks."
                      ,
                      'd':"The population-weighted average hazard index (HI) takes into account HI levels at all populated block receptors in the entire modeled domain."
                     }
        return notes_dict

    def get_sheet_name(self):
        return 'Table4-NC'

    def get_columns(self):
        return ['Total Population', 'People Living in Households with Income Below Twice the Poverty Level',
                'People Living in Households with Income Below the Poverty Level']
