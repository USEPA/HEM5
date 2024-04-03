from com.sca.hem4.ej.summary.KCSummary import KCSummary


class CancerKCSummary(KCSummary):

    def get_table_name(self):
        # scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
        #     'Facility ' + self.facility
        scope = self.source_category if self.facility is None else self.facility
        return 'Table 2. Demographic Assessment of Risk Results Based on ' + \
               scope + ' Emissions - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_notes(self, max_risk):
        scope = self.source_category if self.facility is None else self.facility
        maxrisk = str(int(max_risk)) if max_risk > 1 else str(max_risk)
        notes_dict = {'a':"The demographic percentages are based on the 2020 Decennial Census' total block populations, which are linked to the Census’ 2018-2022 American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':"The People of Color population is the total population minus the White population and includes people identifying as African American, Native American, Other and Multiracial, or Hispanic/Latino."
                      ,
                      'c':'In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category for these analyses. A person is identified as one of five racial/ethnic categories: White, African American, Native American, Other and Multiracial, or Hispanic/Latino.'
                      ,
                      'd':"The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area."
                      ,
                      'e':"The at-risk population and its demographic breakdown are the people residing within 10 km of each modeled facility with a cancer risk greater than or equal to 1 in 1 million."
                      ,
                      'f':"The maximum modeled risk is " + maxrisk + " in 1 million based on " + scope + " emissions. This maximum occurs at the single populated receptor with the highest modeled risk. See the HEM5 User's Guide for more information."
                      }
        return notes_dict

    def get_risk_header(self):
        return 'Population With Risk Greater Than or Equal to ' + self.cancer_risk_threshold + ' in 1 million'

    def get_max_risk_header(self):
        return 'Maximum Risk (in 1 million)'

    def get_risk_bins(self, data):
        # Note: this map corresponds to the bin assignments that happen in the DataModel#tabulate_mir_data() method.
        cancer_risk_map = {
            "1" : 1, "5" : 2, "10" : 3, "20" : 4, "30" : 5, "40" : 6, "50" : 7, "100" : 8, "200" : 9, "300" : 10
        }

        return data[cancer_risk_map[self.cancer_risk_threshold]:11]
