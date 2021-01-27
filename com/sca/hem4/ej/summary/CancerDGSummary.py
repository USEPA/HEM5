from com.sca.hem4.ej.summary.DGSummary import DGSummary


class CancerDGSummary(DGSummary):

    def get_table_name(self):
        return 'C-6. Distribution of Cancer Risk for Racial and Ethnic Groups, Age Groups, Adults without a ' + \
               'High School Diploma, People Living in Households Below the Poverty Level, and People Living in ' + \
               'Linguistic Isolation - ' + self.radius + ' km Study Area Radius'

    def get_notes(self):
        return 'Notes:\n\n' + \
               '\u1D43Distributions by race, ethnicity, age, education, income and linguistic isolation are based on ' + \
               'demographic information at the census block group level. Risks from ' + \
               self.source_category + ' emissions are modeled at the census block level.\n' + \
               '\u1D47Modeled risks are for a 70-year lifetime, based on the predicted outdoor concentration and not ' + \
               'adjusted for exposure factors.\n' + \
               '\u1D9CThe minority population includes people identifying as African American, Native American, Other ' + \
               'and Multiracial, or Hispanic/Latino. Measures are taken to avoid double counting of people identifying ' + \
               'as both Hispanic/Latino and a racial minority.\n' + \
               '\u1D48In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct ' + \
               'demographic category for these analyses. A person is identified as one of five racial/ethnic ' + \
               'categories above: White, African American, Native American, Other and Multiracial, or Hispanic/Latino.\n' + \
               '\u1D49The population-weighted average risk takes into account risk levels at all ' + \
               'populated block receptors in the modeled domain for the entire source category.'

    def get_risk_name(self):
        return 'Risk \u1D47'

    def get_columns(self):
        return ['', 'Total Population', 'White', 'Minority\u1D9C', 'African American', 'Native American',
                'Other and Multiracial', 'Hispanic or Latino\u1D48', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'People Living Below the Poverty Level', 'Total Number >= 25 Years Old',
                'Number >= 25 Years Old without a High School Diploma', 'People Living in Linguistic Isolation']

    def get_risk_header(self):
        return 'Average risk (in one million) \u1D49'
