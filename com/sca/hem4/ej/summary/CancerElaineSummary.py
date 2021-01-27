from com.sca.hem4.ej.summary.ElaineSummary import ElaineSummary


class CancerElaineSummary(ElaineSummary):

    def __init__(self, radius, source_category):
        self.radius = str(radius)
        self.source_category = source_category

    def get_table_header(self):
        return 'Table A-6. ' + self.source_category + ' Source Category: Demographic ' + \
               'Assessment based on Cancer Risk Results - ' + self.radius + \
               ' km Study Area Radius'

    def get_risk_header(self):
        return 'Population with Cancer Risk Greater than or Equal to 1 in 1 Million'
