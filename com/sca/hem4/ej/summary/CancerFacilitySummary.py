from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary


class CancerFacilitySummary(FacilitySummary):

    def get_table_name(self):
        return 'Summary of Demographic Assessment of Risk Results for Facilities in the ' + self.source_category + \
               ' run group - Population With Risk Greater Than or Equal to ' + \
               str(self.cancer_risk_threshold) + ' in 1 million within a  ' + str(self.radius) + \
               ' km Study Area Radius around each facility.'

    def get_risk_label(self):
        return 'At Risk'

    def get_sheet_name(self):
        return "Risk >= " + str(self.cancer_risk_threshold) + "-in-1-million"