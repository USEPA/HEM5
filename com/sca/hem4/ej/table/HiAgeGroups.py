from com.sca.hem4.ej.table.WorksheetTable import WorksheetTable


class HiAgeGroups(WorksheetTable):

    def __init__(self, radius_value, source_category, prefix, name, facility):
        self.prefix = prefix
        self.name = name
        self.active_columns = [0, 6, 7, 8]
        WorksheetTable.__init__(self, radius=radius_value, source_category=source_category, facility=facility)

    def get_bin_headers(self):
        return ['0 to <= 1', '>1 to <= 2', '>2 to <= 3', '>3 to <= 4', '>4 to <= 5', '>5 to <= 6', '>6 to <= 7',
                '>7 to <= 8', '>8 to <= 9', '>9 to <= 10', '> 10']

    def get_table_name(self):
        return 'Table ' + self.identifier + '-2. Distribution of Hazard Indices for Different Age Groups - ' + \
               self.radius + ' km Study Area Radius \u1d43'

    def get_sub_header_1(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return self.name + ' Hazard Index Ranges for ' + scope + ' \u1d47'

    def get_sub_header_2(self):
        article = 'any' if self.facility is None else 'the'
        return 'Number of People within ' + self.radius + ' km of ' + article + \
               ' Facility in Different Hazard Index Ranges \u1D47'

    def get_average_header(self):
        return "Average " + self.name + " Hazard Index \u1D9C"

    def get_notes(self):
        notes_dict = {'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated"
                      ,
                      'note1_a':"radius, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"Hazard indices from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year"
                      ,
                      'note1_b':"lifetime, and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      ,
                      'c':"The population-weighted average hazard index (HI) takes into account HI levels at all populated block receptors in the entire modeled domain."
                     }
        return notes_dict
    
    def get_sheet_name(self):
        return 'Table' + self.identifier + '2NC'

    def get_columns(self):
        return ['Total Population', 'Age (Years)\n0-17', 'Age (Years)\n18-64', 'Age (Years)\n>=65']
