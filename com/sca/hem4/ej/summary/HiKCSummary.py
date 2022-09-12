from com.sca.hem4.ej.summary.KCSummary import KCSummary


class HiKCSummary(KCSummary):

    def get_notes(self):
        return 'Notes:\n\n' + \
               'The People of Color population is the total population minus the White population.\n' + \
               'Source Category population figures are for the population residing within ' + self.radius + ' km from the center of ' + \
               'the modeled facilities with a hazard index greater than 1.'

    def get_risk_header(self):
        return 'Population With a Hazard Index (HI) Greater Than ' + self.hi_risk_threshold

    def get_max_risk_header(self):
        return 'Maximum Hazard Index'

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]