from com.sca.hem4.ej.summary.KCSummary import KCSummary


class CancerKCSummary(KCSummary):

    def get_table_name(self):
        return 'Table 2. Summary of Demographic Assessment of Risk Results for the ' + \
               self.source_category + ' Source Category - ' + self.radius + ' km Study Area Radius'

    def get_notes(self):
        return 'Notes:\n\n' + \
               'The minority population is the total population minus the white population.\n' + \
               'Source Category population figures are for the population residing within ' + self.radius + ' km from the center of ' + \
               'the modeled facilities with cancer risk greater than or equal to 1 in 1 million.'

    def get_risk_header(self):
        return 'Population With Risk Greater Than or Equal to 1 in 1 million'

    def get_max_risk_header(self):
        return 'Maximum Risk (in 1 million)'
