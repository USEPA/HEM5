from com.sca.hem4.ej.summary.ElaineSummary import ElaineSummary


class CancerElaineSummary(ElaineSummary):

    def __init__(self, radius, cancer_risk_threshold, hi_risk_threshold, source_category, facility):
        self.radius = str(radius)
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.source_category = source_category
        self.facility = facility

    def get_table_header(self):
        scope =  self.source_category if self.facility is None else self.facility
        return 'Table for Preamble: Demographic Assessment of Cancer Risk Results based on ' + scope + ' Emissions ' + \
               '- ' + self.radius + ' km Study Area Radius \u1d43'

    def get_risk_header(self):
        return 'Population with Cancer Risk Greater than or Equal to ' + self.cancer_risk_threshold + \
               ' in 1 Million based on Modeled Emissions'

    def get_risk_bins(self, data):
        # Note: this map corresponds to the bin assignments that happen in the DataModel#tabulate_mir_data() method.
        cancer_risk_map = {
            "1" : 1, "5" : 2, "10" : 3, "20" : 4, "30" : 5, "40" : 6, "50" : 7, "100" : 8, "200" : 9, "300" : 10
        }

        return data[cancer_risk_map[self.cancer_risk_threshold]:11]