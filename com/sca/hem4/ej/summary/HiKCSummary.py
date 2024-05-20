from com.sca.hem4.ej.summary.KCSummary import KCSummary


class HiKCSummary(KCSummary):

    def get_notes(self, max_risk):
        scope = self.source_category if self.facility is None else self.facility
        maxrisk = str(int(max_risk)) if max_risk > 1 else str(max_risk)
        notes_dict = {
                      'a':"The demographic percentages are based on the 2020 Decennial Census' block populations, which are linked to the Census’ 2018-2022 American Community Survey (ACS) five-year demographic averages at the block group level. To derive"
                      ,
                      'note1_a':"  demographic percentages, it is assumed a given block's demographics are the same as the block group in which it is contained. Demographics are tallied for all blocks falling within the indicated radius."
                      ,
                      'b':"A person is identified as one of six racial/ethnic categories: White, Black, American Indian or Alaska Native, Asian, Other and Multiracial, or Hispanic/Latino. The People of Color population is the total population minus the White population."
                      ,
                      'c':'To avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category. A person who identifies as Hispanic or Latino is counted only as Hispanic/Latino for this analysis (regardless of other racial identifiers).'
                      ,
                      'd':'The demographic percentages for people living below the poverty line or below twice the poverty line are based on Census ACS surveys at the block group level that do not include people in group living situations such as'
                      ,
                      'note1_d':'  dorms, prisons, nursing homes, and military barracks. To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation and then divided by the total U.S. population'
                      ,
                      'note2_d':"  based on the 2018-2022 ACS. The study area's facility-specific and run group-wide population counts are based on the methodology noted in footnote 1 to derive block-level demographic population counts for the study area,"
                      ,
                      'note3_d':'  which are then divided by the respective total block-level population (facility-specific and run group-wide) to derive the study area demographic percentages shown.'
                      ,
                      'e':'The demographic percentage for people >= 25 years old without a high school diploma is based on Census ACS data for the total population 25 years old and older at '
                          'the block group level, which is used as the denominator when calculating this demographic percentage.'
                      ,
                      'f':'The Limited English Speaking population is estimated at the block group level by taking the product of the block group population and the fraction of '
                          'Limited English Speaking households in the block group, assuming that the number of individuals '
                      ,
                      'note1_f':'  per household is the same for Limited English Speaking households '
                                'as for the general population, and summed over all block groups.'
                      ,
                      'g':"The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area."
                      ,
                      'h':"The at-risk population and its demographic breakdown are the people residing within the indicated study area radius of each modeled facility with a hazard index greater than the indicated level."
                      ,
                      'i':"The maximum modeled " + self.hazard_name + " hazard index is " + maxrisk + " based on " + scope + " emissions. This maximum occurs at the single populated receptor with the highest modeled hazard index. See the HEM5 User's Guide for more information."
                      }
        return notes_dict

    def get_risk_header(self):
        return 'Population With a Hazard Index (HI) Greater Than ' + self.hi_risk_threshold

    def get_max_risk_header(self):
        return 'Maximum Hazard Index'

    def get_risk_bins(self, data):
        return data[int(self.hi_risk_threshold):11]