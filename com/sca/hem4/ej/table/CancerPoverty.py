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
        return 'Table ' + self.identifier + '-4. Distribution of Cancer Risk for People Living in Households Below Twice ' + \
               'the Poverty Level and Below the Poverty Level - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility

        return 'Range of Lifetime Individual Cancer Risk from ' + scope + ' (Chance in One Million) \u1D47'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Ranges for Lifetime Cancer Risk \u1D47'

    def get_average_header(self):
        return "Average Risk (Chance in One Million) \u1D9C"

    def get_notes(self):
        notes_dict = {'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated"
                      ,
                      'note1_a':"radius, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"Risks from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year"
                      ,
                      'note1_b':"lifetime, and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      ,
                      'c':"The population-weighted average risk takes into account risk levels at all populated block receptors in the entire modeled domain."
                     }
        return notes_dict
    
    def get_sheet_name(self):
        return 'Table' + self.identifier + '4C'

    def get_columns(self):
        return ['Total Population', 'People Living in Households with Income Below Twice the Poverty Level',
                'People Living in Households with Income Below the Poverty Level']
