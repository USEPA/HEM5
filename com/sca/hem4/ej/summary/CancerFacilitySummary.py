from com.sca.hem4.ej.summary.FacilitySummary import FacilitySummary


class CancerFacilitySummary(FacilitySummary):

    def get_table_name(self):
        return 'Summary of Demographic Assessment of Risk Results for Facilities in the ' + self.source_category + \
               ' run group - \nPopulation With Risk Greater Than or Equal to ' + \
               str(self.cancer_risk_threshold) + ' in 1 million within a  ' + str(self.radius) + \
               ' km Study Area Radius around each facility. \u1d43'

    def get_risk_label(self):
        return 'At Risk'

    def get_sheet_name(self):
        return "Risk >= " + str(self.cancer_risk_threshold) + "-in-1-million"

    def get_risk_bins(self, data):
        # Note: this map corresponds to the bin assignments that happen in the DataModel#tabulate_mir_data() method.
        cancer_risk_map = {
            "1" : 1, "5" : 2, "10" : 3, "20" : 4, "30" : 5, "40" : 6, "50" : 7, "100" : 8, "200" : 9, "300" : 10
        }

        return data[cancer_risk_map[self.cancer_risk_threshold]:11]
    
    def get_notes(self):
        notes_dict = {
                      'a':"The demographic percentages are based on the 2020 Decennial Census' block populations, which are linked to the Census’ 2018-2022 American Community Survey (ACS) five-year demographic averages at the block group level. To derive"
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
                      'd':'A person is identified as one of six racial/ethnic categories: White, Black, American Indian or Alaska Native, Asian, Other and Multiracial, or Hispanic/Latino. The People of Color population is the total population minus the White population.'
                      ,
                      'e':'To avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category. A person who identifies as Hispanic or Latino is counted only as Hispanic/Latino for this analysis (regardless of other racial identifiers).'
                      ,
                      'f':'The demographic percentages for people living below the poverty line or below twice the poverty line are based on Census ACS surveys at the block group level that do not include people in group living situations such as'
                      ,
                      'note1_f':'  dorms, prisons, nursing homes, and military barracks. To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation and then divided by the total U.S. population'
                      ,
                      'note2_f':"  based on the 2018-2022 ACS. The study area's facility-specific and run group-wide population counts are based on the methodology noted in footnote 'a' to derive block-level demographic population counts for the study area,"
                      ,
                      'note3_f':'  which are then divided by the respective total block-level population (facility-specific and run group-wide) to derive the study area demographic percentages shown.'
                      ,
                      'g':'The demographic percentage for people >= 25 years old without a high school diploma is based on Census ACS data for the total population 25 years old and older at '
                          'the block group level, which is used as the denominator when calculating this demographic percentage.'
                      ,
                      'h':'The Limited English Speaking population is estimated at the block group level by taking the product of the block group population and the fraction of '
                          'Limited English Speaking households in the block group, assuming that the number of individuals '
                      ,
                      'note1_h':'  per household is the same for Limited English Speaking households '
                                'as for the general population, and summed over all block groups.'
                      ,
                      'i':'The demographic percentages for people with one or more disabilities are based on Census ACS surveys at the block group level of civilian '
                          'non-institutionalized people (i.e., all U.S. civilians not residing in institutional group quarters facilities such as '
                      ,
                      'note1_i':'  correctional institutions, juvenile facilities, skilled nursing facilities, and other long-term care living arrangements). '
                                'To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation '
                      ,
                      'note2_i':'  and then divided by the total U.S. population based on the 2018-2022 ACS. The study areas’ facility-specific and '
                                'run group-wide population counts are based on the methodology noted in footnote 1 to derive block-level demographic population counts'
                      ,
                      'note3_i':'  for the study area, which are then divided by the respective total block-level population (facility-specific and run group-wide) to '
                                'derive the study area demographic percentages shown.'
                      ,
                      'j':"The total nationwide population includes all 50 states, the District of Columbia, and Puerto Rico. The state and county populations include any states and counties, respectively, with census blocks within the radius of the modeled area."
                      }
        return notes_dict    