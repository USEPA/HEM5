from com.sca.hem4.ej.summary.DGSummary import DGSummary


class CancerDGSummary(DGSummary):

    def get_table_name(self):
        return 'C-6. Proximity and Average Risk Results for All Demographic Groups Analyzed - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_notes(self):
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
                      'note2_d':"  based on the 2018-2022 ACS. The study area's facility-specific and run group-wide population counts are based on the methodology noted in footnote 'a' to derive block-level demographic population counts for the study area,"
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
                      'g':'The demographic percentages for people with one or more disabilities are based on Census ACS surveys at the block group level of civilian '
                          'non-institutionalized people (i.e., all U.S. civilians not residing in institutional group quarters facilities such as '
                      ,
                      'note1_g':'  correctional institutions, juvenile facilities, skilled nursing facilities, and other long-term care living arrangements). '
                                'To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation '
                      ,
                      'note2_g':'  and then divided by the total U.S. population based on the 2018-2022 ACS. The study areas’ facility-specific and '
                                'run group-wide population counts are based on the methodology noted in footnote 1 to derive block-level demographic population counts'
                      ,
                      'note3_g':'  for the study area, which are then divided by the respective total block-level population (facility-specific and run group-wide) to '
                                'derive the study area demographic percentages shown.'
                      ,
                      'h':'The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area.'
                      ,
                      'i':'The population-weighted average risk takes into account risk levels at all populated block receptors in the entire modeled domain. Risks from the modeled emissions are at the census block level, based on the predicted outdoor concentration over a 70-year lifetime,'
                      ,
                      'note1_i':"  and not adjusted for exposure factors. See the HEM5 User's Guide for more information."
                      }            
        return notes_dict

    def get_risk_name(self):
        return 'Risk'

    def get_columns(self):
        return ['', 'Total Population', 'White', 'People of Color \u1d47', 'Black', 'American Indian or Alaska Native',
                'Asian', 'Other and Multiracial', 'Hispanic or Latino \u1d9c', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'Below the Poverty Level \u1d48',
                'Below Twice the Poverty Level \u1d48', 'Total Number >= 25 Years Old',
                'Over 25 without a High School Diploma \u1d49', 'People Living in Limited English Speaking Households \u1da0',
                'People with One or More Disabilities \u1d4d']

    def get_risk_header(self):
        return 'Average risk (in one million) \u2071'
