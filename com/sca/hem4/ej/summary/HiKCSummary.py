from com.sca.hem4.ej.summary.KCSummary import KCSummary


class HiKCSummary(KCSummary):

    def get_notes(self, max_risk):
        scope = self.source_category if self.facility is None else self.facility
        notes_dict = {'a':"The demographic percentages are based on the 2020 Decennial Census' total block populations, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"The People of Color population is the total population minus the White population and includes people identifying as African American, Native American, Other and Multiracial, or Hispanic/Latino."
                      ,
                      'c':'In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category for these analyses. A person is identified as one of five racial/ethnic categories: White, African American, Native American, Other and Multiracial, or Hispanic/Latino.'
                      ,
                      'd':"The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area."
                      ,
                      'e':"The at-risk population and its demographic breakdown are the people residing within 10 km of each modeled facility with a hazard index greater than or equal to 1."
                      ,
                      'f':"The maximum modeled hazard index is " + str(max_risk) + " based on " + scope + " emissions. This maximum occurs at the single populated receptor with the highest modeled hazard index. See the HEM5 User's Guide for more information."
                      }
        return notes_dict

    def get_risk_header(self):
        return 'Population With a Hazard Index (HI) Greater Than ' + self.hi_risk_threshold

    def get_max_risk_header(self):
        return 'Maximum Hazard Index'

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]