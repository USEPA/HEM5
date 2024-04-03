from com.sca.hem4.ej.summary.DGSummary import DGSummary


class HiDGSummary(DGSummary):

    def get_table_name(self):
        return 'C-6. Proximity and Average Hazard Indices for Racial and Ethnic Groups, Age Groups, Adults without a ' + \
               'High School Diploma, People Living in Low Income Households, and People Living in ' + \
               'Linguistic Isolation - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_notes(self):
        notes_dict = {
                      'a':"The demographic populations are based on the 2020 Decennial Census' total block populations that are located within the indicated radius, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area."
                      ,
                      'c':"The People of Color population is the total population minus the White population and includes people identifying as African American, Native American, Other and Multiracial, or Hispanic/Latino."
                      ,
                      'd':'In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category for these analyses. A person is identified as one of five racial/ethnic categories: White, African American, Native American, Other and Multiracial, or Hispanic/Latino.'
                      ,
                      'e':"The population-weighted average hazard index takes into account hazard index levels at all populated block receptors in the entire modeled domain. Hazard indices from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year lifetime,"
                      ,
                      'note1_e':"and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      }            
        return notes_dict

    def get_risk_name(self):
        return self.hazard_name + ' Hazard Indices'

    def get_risk_header(self):
        return 'Average ' + self.hazard_name + " HI \u1D49"
