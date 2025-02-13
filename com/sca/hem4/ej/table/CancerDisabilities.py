from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class CancerDisabilities(WorksheetTable):

    def __init__(self, radius_value, source_category, facility):
        self.name = None
        self.prefix = None
        self.active_columns = [0, 17]
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to < 1', '1 to < 5', '5 to < 10', '10 to < 20', '20 to < 30', '30 to < 40', '40 to < 50',
                '50 to < 100', '100 to < 200', '200 to < 300', '>= 300']

    def get_table_name(self):
        return 'Table 6. Distribution of Cancer Risk for People With One or More Disabilities - ' + \
               self.radius + ' km Study Area Radius \u1d43'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility

        return 'Range of Lifetime Individual Cancer Risk from ' + scope + ' (Chance in One Million) \u1D47'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Ranges for Lifetime Cancer Risk \u1D47'

    def get_average_header(self):
        return "Average Risk (Chance in One Million) \u1D48"

    def get_notes(self):
        notes_dict = {'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated"
                      ,
                      'note1_a':"  radius, which for people with one or more disabilities are linked to the Census’ 2018-2022 American Community Survey five-year"
                      ,
                      'note2_a':"  demographic averages at the census tract level."
                      ,
                      'b':"Risks from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year"
                      ,
                      'note1_b':"  lifetime, and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      ,
                      'c':"The number of people with one or more disabilities is based on the American Community Survey at the census tract level of civilian"
                      ,
                      'note1_c':"  non-institutionalized people. The tract-based percentage of people with one or more disabilities is applied to all block groups"
                      ,
                      'note2_c':"  and blocks within the respective tract, for those blocks that are within the indicated radius and risk range."
                      ,
                      'd':"The population-weighted average risk takes into account risk levels at all populated block receptors in the entire modeled domain."
                     }
        return notes_dict

    def get_sheet_name(self):
        return 'Table6-C'

    def get_columns(self):
        return ['Total Population', 'People With One or More Disabilities \u1d9c']
