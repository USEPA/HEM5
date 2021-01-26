from com.sca.ej.summary.DGSummary import DGSummary


class HiDGSummary(DGSummary):

    def get_table_name(self):
        return 'C-6. Distribution of Hazard Indices for Racial and Ethnic Groups, Age Groups, Adults without a ' + \
               'High School Diploma, People Living in Households Below the Poverty Level, and People Living in ' + \
               'Linguistic Isolation - ' + self.radius + ' km Study Area Radius'

    def get_notes(self):
        return 'Notes:\n\n' + \
               '\u1D43Distributions by race, ethnicity, age, education, income and linguistic isolation are based on ' + \
               'demographic information at the census block group level. ' + self.hazard_name + ' hazard indices from ' + \
               self.source_category + ' emissions are modeled at the census block level.\n' + \
               '\u1D47The minority population includes people identifying as African American, Native American, Other ' + \
               'and Multiracial, or Hispanic/Latino. Measures are taken to avoid double counting of people identifying ' + \
               'as both Hispanic/Latino and a racial minority.\n' + \
               '\u1D9CIn order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct ' + \
               'demographic category for these analyses. A person is identified as one of five racial/ethnic ' + \
               'categories above: White, African American, Native American, Other and Multiracial, or Hispanic/Latino.\n' + \
               '\u1D48The population-weighted average hazard index takes into account hazard index levels at all ' + \
               'populated block receptors in the modeled domain for the entire source category.'

    def get_risk_name(self):
        return self.hazard_name + ' Hazard Indices'

    def get_risk_header(self):
        return 'Average ' + self.hazard_name + " HI"
