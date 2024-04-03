from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary


class HiFacilitySummary(FacilitySummary):

    def get_table_name(self):
        return 'Summary of Demographic Assessment of Risk Results for Facilities in the ' + self.source_category + \
               ' run group - \nPopulation with a ' + self.hazard_name + ' Hazard Index Greater Than ' + \
               self.hi_risk_threshold + ' within a  ' + self.radius + ' km Study Area Radius around each facility. \u1d43'

    def get_risk_label(self):
        return 'Above HI'

    def get_sheet_name(self):
        return "HI > " + str(self.hi_risk_threshold)

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]

    def get_notes(self):
        notes_dict = {'a':"The demographic percentages are based on the 2020 Decennial Census' block populations, which are linked to the Census’ 2018-2022 American Community Survey (ACS) five-year demographic averages at the block group level. To derive"
                      ,
                      'note1_a':"demographic percentages, it is assumed a given block's demographics are the same as the block group in which it is contained. Demographics are tallied for all blocks falling within the indicated radius. Demographic-specific populations"
                      ,
                      'note2_a':"may be determined by multiplying the total population provided in each row by the respective demographic percentages in the same row."
                      ,
                      'b':'The "Proximity" analysis is for the entire population irrespective of '
                          'risk (i.e., for all risk levels combined). The "At Risk" analysis is for only '
                          'the population within Census blocks having HEM5-modeled risk at and above the indicated risk level.' 
                      ,
                      'c':'The total population values for the run group and each individual facility are based on block level data from the 2020 Decennial Census, with block populations summed over the area defined by the indicated radius around each facility.'
                      ,
                      'd':'A person is identified as one of five racial/ethnic categories: White, African American, Native American, Other and Multiracial, or Hispanic/Latino. The People of Color population is the total population minus the White population.'
                      ,
                      'e':'To avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category. A person who identifies as Hispanic or Latino is counted only as Hispanic/Latino for this analysis (regardless of other racial identifiers).'
                      ,
                      'f':'The nationwide population and demographic percentages are based on the 2018-2022 ACS for the categories defined above, for the 50 states, the District of Columbia, and Puerto Rico. Nationwide demographic percentages based on'
                      ,
                      'note1_f':'different demographic category definitions and/or different ACS averaging years will differ from the nationwide row values shown.'
                      ,
                      'g':'The state and county populations include tallies from any states and counties, respectively, with one or more census blocks within the radius of the modeled area around each facility.'
                     }
        return notes_dict    