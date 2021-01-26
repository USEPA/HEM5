from com.sca.ej.summary.ElaineSummary import ElaineSummary


class HiElaineSummary(ElaineSummary):

    def __init__(self, radius, source_category, hazard_name):
        self.radius = str(radius)
        self.source_category = source_category
        self.hazard_name = hazard_name

    def get_table_header(self):
        return 'Table C-6. ' + self.source_category + ' Source Category: Demographic ' + \
               'Assessment based on ' + self.hazard_name + ' Hazard Index Results - ' + self.radius + \
               ' km Study Area Radius'

    def get_risk_header(self):
        return 'Population with Hazard Index Greater than 1'
