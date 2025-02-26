from copy import deepcopy

import numpy as np

from com.sca.hem4.ej.data.DataModel import DataModel


class ElaineSummary():

    def __init__(self, radius, cancer_risk_threshold, hi_risk_threshold, source_category):
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.active_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 10, 13, 14]

    def create_summary(self, workbook, formats, national_values, state_values, county_values, values):
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())

        # Increase the cell sizes to match expected content.
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 16)
        worksheet.set_column("C:C", 16)
        worksheet.set_column("D:D", 16)
        worksheet.set_column("E:E", 24)
        worksheet.set_row(0, 48)
        worksheet.set_row(1, 58)

        # Create top level header
        worksheet.merge_range("A1:E1", self.get_table_header(),  formats['top_header'])

        worksheet.write(1, 1, 'Nationwide', formats['sub_header_3'])
        worksheet.write(1, 2, 'State', formats['sub_header_3'])
        worksheet.write(1, 3, 'County', formats['sub_header_3'])
        worksheet.write(1, 4, self.get_risk_header(), formats['sub_header_3'])

        worksheet.write(2, 0, 'Total Population')

        worksheet.write("D4", 'Race and Ethnicity by Percent', formats['sub_header_5'])

        worksheet.write(4, 0, 'White')
        worksheet.write(5, 0, 'Black')
        worksheet.write(6, 0, 'American Indian or Alaska Native')
        worksheet.write(7, 0, 'Asian')
        worksheet.write(8, 0, 'Other and Multiracial')
        worksheet.write(9, 0, 'Hispanic or Latino \u1D47')

        worksheet.write("D11", 'Income by Percent \u1d9c', formats['sub_header_5'])
        worksheet.write(11, 0, 'Below Poverty Level')
        worksheet.write(12, 0, 'Above Poverty Level')
        worksheet.write(13, 0, 'Below Twice Poverty Level')
        worksheet.write(14, 0, 'Above Twice Poverty Level')

        worksheet.write("D16", 'Education by Percent \u1d48', formats['sub_header_5'])
        worksheet.write(16, 0, 'Over 25 and without a High School Diploma', formats['wrap'])
        worksheet.write(17, 0, 'Over 25 and with a High School Diploma', formats['wrap'])

        worksheet.write("D19", 'Disabilities by Percent \u1d49', formats['sub_header_5'])
        worksheet.write(19, 0, 'One or More Disabilities', formats['wrap'])
        worksheet.write(20, 0, 'No Disabilities', formats['wrap'])

        worksheet.write("D22", 'People Living in Limited English Speaking Households by Percent \u1da0', formats['sub_header_5'])
        worksheet.write(22, 0, 'People Living in Limited English Speaking Households', formats['wrap_w_bottom'])

        # Create notes
        notes_dict = self.get_notes()
        notes_row = 25
        for note in notes_dict:
            if 'note' in note:
                worksheet.write_rich_string('A'+str(notes_row), formats['notes'], 
                                            notes_dict[note], ' ')                
            elif note == '*':
                worksheet.write_rich_string('A'+str(notes_row), formats['asterik'],
                                            note, ' ', formats['notes'], notes_dict[note])
            else:
                worksheet.write_rich_string('A'+str(notes_row), formats['superscript'],
                                            note, ' ', formats['notes'], notes_dict[note])
            notes_row+=1

        self.append_aggregated_data(national_values, worksheet, formats, 1)
        self.append_aggregated_data(state_values, worksheet, formats, 2)
        self.append_aggregated_data(county_values, worksheet, formats, 3)
        self.append_data(values, worksheet, formats)

    def get_notes(self):
        notes_dict = {
                      'a':"The demographic percentages are based on the 2020 Decennial Census' block populations, which are linked to the Census’ 2018-2022 American Community Survey (ACS) five-year demographic averages at the block group level. To derive"
                      ,
                      'note1_a':"  demographic percentages, it is assumed a block's demographics are the same as the block group in which it is contained. Demographics are tallied for all blocks falling within the indicated radius."
                      ,
                      'b':'To avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category. A person who identifies as Hispanic or Latino is counted only as Hispanic/Latino for this analysis (regardless of other racial identifiers).'
                      ,
                      'c':'The demographic percentages for people living below the poverty line or below twice the poverty line are based on Census ACS surveys at the block group level that do not include people in group living situations such as'
                      ,
                      'note1_c':'  dorms, prisons, nursing homes, and military barracks. To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation and then divided by the total U.S. population'
                      ,
                      'note2_c':"  based on the 2018-2022 ACS. The study area's population counts are based on the methodology noted in footnote \"a\" to derive block-level demographic population counts, which are then divided by the respective"
                      ,
                      'note3_c':'  total block-level population to derive the study area demographic percentages shown.'
                      ,
                      'd':'The demographic percentage for people >= 25 years old without a high school diploma is based on Census ACS data for the total population 25 years old and older at '
                          'the block group level, which is used as the denominator when calculating this demographic percentage.'
                      ,
                      'e':'The demographic percentages for people with one or more disabilities are based on Census ACS surveys at the tract level of civilian '
                          'non-institutionalized people (i.e., all U.S. civilians not residing in institutional group quarters facilities such as correctional institutions,'
                      ,
                      'note1_e':'  juvenile facilities, skilled nursing facilities, and other long-term care living arrangements). '
                                'To derive the nationwide demographic percentages shown, these block group level tallies are summed for all block groups in the nation '
                      ,
                      'note2_e':'  the 2018-2022 ACS. The study areas’ population counts are based on applying the Census tract level percentage of people with one or more disabilities to each block group and block within the respective tract. The methodology noted in footnote "a" is then used'
                      ,
                      'note3_e':'  to derive block-level demographic population counts, which are then divided by the respective total block-level population to derive the study area demographic percentages shown.'
                      ,
                      'f':'The Limited English Speaking population is estimated at the block group level by taking the product of the block group population and the fraction of '
                          'Limited English Speaking households in the block group, assuming that the number of individuals '
                      ,
                      'note1_f':'  per household is the same for Limited English Speaking households '
                                'as for the general population, and summed over all block groups.'
                     }
        return notes_dict

    def get_sheet_name(self):
        return "Preamble Summary"

    def append_aggregated_data(self, values, worksheet, formats, startcol):
        data = deepcopy(values)

        # For this summary, we only want the percentages, which are in the second row.
        for index in range(1, 18):
            data[0][index] = data[1][index]

        # total pop kept as raw number, but we're using percentages for the breakdowns...
        exposure_value = float(data[0][0])
        worksheet.write_number(2, startcol, exposure_value, formats['number'])

        # white
        value = float(data[0][1])
        format = formats['percentage']
        worksheet.write_number(4, startcol, value, format)

        # african american
        value = float(data[0][2])
        format = formats['percentage']
        worksheet.write_number(5, startcol, value, format)

        # native american
        value = float(data[0][3])
        format = formats['percentage']
        worksheet.write_number(6, startcol, value, format)

        # asian
        value = float(data[0][4])
        format = formats['percentage']
        worksheet.write_number(7, startcol, value, format)

        # other
        value = float(data[0][5])
        format = formats['percentage']
        worksheet.write_number(8, startcol, value, format)

        # hispanic
        value = float(data[0][6])
        format = formats['percentage']
        worksheet.write_number(9, startcol, value, format)

        # below poverty level
        value = float(data[0][12])
        format = formats['percentage']
        worksheet.write_number(11, startcol, value, format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(12, startcol, value, format)

        # below 2x poverty level
        value = float(data[0][13])
        format = formats['percentage']
        worksheet.write_number(13, startcol, value, format)

        # above 2x poverty level
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(14, startcol, value, format)

        # without high school diploma
        value = float(data[0][11])
        format = formats['percentage']
        worksheet.write_number(16, startcol, value, format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(17, startcol, value, format)

        # with disabilities
        value = float(data[0][17])
        format = formats['percentage']
        worksheet.write_number(19, startcol, value, format)

        # without disabilities
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(20, startcol, value, format)

        # linguistically isolated
        value = float(data[0][14])
        format = formats['percentage_w_bottom']
        worksheet.write_number(22, startcol, value, format)

    def append_data(self, values, worksheet, formats):
        data = deepcopy(values)

        # We need only one row, which will be the sum of all bins except the first one (excluding total and avg...)
        dg_data = self.get_risk_bins(data)
        row_totals = [sum(x) for x in zip(*dg_data)]

        saved_edu_pop = None
        for index in range(1, 18):
            # Education is a special case...we want the population over 25 as the denominator, not the total population!
            if index == 10:
                saved_edu_pop = row_totals[index]

            if index == 11:
                row_totals[index] = (row_totals[index] / saved_edu_pop) if saved_edu_pop > 0 else 0
            else:
                row_totals[index] = (row_totals[index] / row_totals[0]) if row_totals[0] > 0 else 0

        # total pop kept as raw number, but we're using percentages for the breakdowns...
        exposure_value = float(row_totals[0])
        worksheet.write_number(2, 4, exposure_value, formats['number'])

        # from here on out they are all percentages....
        format = formats['percentage']

        # white
        value = float(row_totals[1])
        worksheet.write_number(4, 4, value, format)

        # african american
        value = float(row_totals[2])
        worksheet.write_number(5, 4, value, format)

        # native american
        value = float(row_totals[3])
        worksheet.write_number(6, 4, value, format)

        # asian
        value = float(row_totals[4])
        worksheet.write_number(7, 4, value, format)

        # other
        value = float(row_totals[5])
        worksheet.write_number(8, 4, value, format)

        # hispanic
        value = float(row_totals[6])
        worksheet.write_number(9, 4, value, format)

        # below poverty level
        value = float(row_totals[12])
        worksheet.write_number(11, 4, value, format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(12, 4, value, format)

        # below 2x poverty level
        value = float(row_totals[13])
        worksheet.write_number(13, 4, value, format)

        # above 2x poverty level
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(14, 4, value, format)

        # without high school diploma
        value = float(row_totals[11])
        worksheet.write_number(16, 4, value, format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(17, 4, value, format)

        # with disabilities
        value = float(row_totals[17])
        format = formats['percentage']
        worksheet.write_number(19, 4, value, format)

        # without disabilities
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(20, 4, value, format)

        # linguistically isolated
        value = float(row_totals[14])
        format = formats['percentage_w_bottom']
        worksheet.write_number(22, 4, value, format)
