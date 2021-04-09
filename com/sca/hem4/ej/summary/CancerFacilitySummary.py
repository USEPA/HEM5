from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary


class CancerFacilitySummary(FacilitySummary):

    def get_table_name(self):
        return 'Summary of Community Assessment of Risk Results for Facilities in the ' + self.source_category + \
               ' run group - \nPopulation With Risk Greater Than or Equal to ' + \
               str(self.cancer_risk_threshold) + ' in 1 million within a  ' + str(self.radius) + \
               ' km Study Area Radius around each facility.'

    def get_risk_label(self):
        return 'At Risk'

    def get_sheet_name(self):
        return "Risk >= " + str(self.cancer_risk_threshold) + "-in-1-million"

    def get_risk_bins(self, data):
        # Note: this map corresponds to the bin assignments that happen in the DataModel#tabulate_mir_data() method.
        cancer_risk_map = {
            "1" : 1, "5" : 2, "10" : 3, "20" : 4, "30" : 5, "40" : 6, "50" : 7, "100" : 8, "200" : 9, "300" : 10
        }

        return data[cancer_risk_map[self.cancer_risk_threshold]:11]