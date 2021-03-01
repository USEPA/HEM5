from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary


class HiFacilitySummary(FacilitySummary):

    def get_table_name(self):
        return 'Summary of Demographic Assessment of Risk Results for Facilities in the [' + self.source_category + \
               ' run group / source category] - \nPopulation with a ' + self.hazard_name + ' Hazard Index Greater Than ' + \
               self.hi_risk_threshold + ' within a  ' + self.radius + ' km Study Area Radius around each facility.'

    def get_risk_label(self):
        return 'Above HI'

    def get_sheet_name(self):
        return "HI > " + str(self.hi_risk_threshold)

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]