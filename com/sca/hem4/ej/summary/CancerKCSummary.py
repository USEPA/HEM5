from com.sca.hem4.ej.summary.KCSummary import KCSummary


class CancerKCSummary(KCSummary):

    def get_table_name(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return 'Table 2. Summary of Community Assessment of Risk Results for ' + \
               scope + ' - ' + self.radius + ' km Study Area Radius'

    def get_notes(self):
        return 'Notes:\n\n' + \
               'The minority population is the total population minus the white population.\n' + \
               'Source Category population figures are for the population residing within ' + self.radius + ' km from the center of ' + \
               'the modeled facilities with cancer risk greater than or equal to 1 in 1 million.'

    def get_risk_header(self):
        return 'Population With Risk Greater Than or Equal to ' + self.cancer_risk_threshold + ' in 1 million'

    def get_max_risk_header(self):
        return 'Maximum Risk (in 1 million)'

    def get_risk_bins(self, data):
        # Note: this map corresponds to the bin assignments that happen in the DataModel#tabulate_mir_data() method.
        cancer_risk_map = {
            "1" : 1, "5" : 2, "10" : 3, "20" : 4, "30" : 5, "40" : 6, "50" : 7, "100" : 8, "200" : 9, "300" : 10
        }

        return data[cancer_risk_map[self.cancer_risk_threshold]:11]
