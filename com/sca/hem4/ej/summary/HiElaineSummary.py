from com.sca.hem4.ej.summary.ElaineSummary import ElaineSummary


class HiElaineSummary(ElaineSummary):

    def __init__(self, radius, cancer_risk_threshold, hi_risk_threshold, source_category, hazard_name, facility):
        self.radius = str(radius)
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.source_category = source_category
        self.hazard_name = hazard_name
        self.facility = facility

    def get_table_header(self):
        scope = 'The ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return 'Table C-6. ' + scope + ' : Demographic ' + \
               'Assessment based on ' + self.hazard_name + ' Hazard Index Results - ' + self.radius + \
               ' km Study Area Radius'

    def get_risk_header(self):
        return 'Population with Hazard Index Greater than ' + self.hi_risk_threshold

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]