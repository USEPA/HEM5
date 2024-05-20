from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class HiRacialEthnic(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name, facility):
        self.active_columns = [0, 1, 2, 3, 4, 5, 6]
        self.prefix = prefix
        self.name = name
        WorksheetTable.__init__(self, radius=radius_value, source_category= source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-1. Distribution of Hazard Indices for Racial and Ethnic Groups - ' + \
               self.radius + ' km Study Area Radius \u1D43'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return self.name + ' Hazard Index Ranges for ' + scope + ' \u1d47'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Hazard Index Ranges \u1D43'

    def get_average_header(self):
        return "Average " + self.name + " Hazard Index \u1D9C"

    def get_notes(self):
        notes_dict = {'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated radius, which are linked to the Census’"
                      ,
                      'note_a':"2018-2022 American Community Survey five-year demographic averages at the block group level. See the HEM5 User's Guide for more information."
                      ,
                      'b':"Hazard indices from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year lifetime, and not adjusted for exposure factors."
                      ,
                      'c':"The population-weighted average hazard index (HI) takes into account HI levels at all populated block receptors in the entire modeled domain."
                      ,
                      'd':'In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category for these analyses. A person is identified as one of six'
                      ,
                      'note_d':"racial/ethnic categories: White, Black, American Indian or Alaska Native, Asian, Other and Multiracial, or Hispanic/Latino."
                     }
        return notes_dict

    def get_sheet_name(self):
        return 'Table' + self.identifier + '1NC'

    def get_columns(self):
        return ['Total Population', 'White', 'Black', 'American Indian or Alaska Native', 'Asian', 'Other and Multiracial',
                'Hispanic or Latino \u1D48']
