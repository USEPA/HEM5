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
        worksheet.set_column("A:A", 24)
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
        worksheet.write(5, 0, 'African American')
        worksheet.write(6, 0, 'Native American')
        worksheet.write(7, 0, 'Other and Multiracial')
        worksheet.write(8, 0, 'Hispanic or Latino \u1D47')

        worksheet.write("D10", 'Income by Percent', formats['sub_header_5'])
        worksheet.write(10, 0, 'Below Poverty Level')
        worksheet.write(11, 0, 'Above Poverty Level')
        worksheet.write(12, 0, 'Below Twice Poverty Level')
        worksheet.write(13, 0, 'Above Twice Poverty Level')

        worksheet.write("D15", 'Education by Percent', formats['sub_header_5'])
        worksheet.write(15, 0, 'Over 25 and without a High School Diploma',  formats['wrap'])
        worksheet.write(16, 0, 'Over 25 and with a High School Diploma',  formats['wrap'])

        worksheet.write("D18", 'Linguistically Isolated by Percent', formats['sub_header_5'])
        worksheet.write(18, 0, 'Linguistically Isolated')

        # Create notes
        notes_dict = self.get_notes()
        notes_row = 21
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
        notes_dict = {'a':"The results are based on a HEM5 run using 2020 Decennial Census block populations linked to the Census’ 2018-2022"
                      ,
                      'note1_a':"American Community Survey five-year demographic averages at the block group level."
                      ,
                      'b':'In order to avoid double counting, the "Hispanic or Latino" category is treated as a distinct demographic category for these analyses.'
                      ,
                      'note1_b':"A person is identified as one of five racial/ethnic categories: White, African American, Native American, Other and Multiracial, or Hispanic/Latino."
                     }
        return notes_dict

    def get_sheet_name(self):
        return "Preamble Summary"

    def append_aggregated_data(self, values, worksheet, formats, startcol):
        data = deepcopy(values)

        # For this summary, we only want the percentages, which are in the second row.
        for index in range(1, 15):
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

        # other
        value = float(data[0][4])
        format = formats['percentage']
        worksheet.write_number(7, startcol, value, format)

        # hispanic
        value = float(data[0][5])
        format = formats['percentage']
        worksheet.write_number(8, startcol, value, format)

        # below poverty level
        value = float(data[0][11])
        format = formats['percentage']
        worksheet.write_number(10, startcol, value, format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(11, startcol, value, format)

        # below 2x poverty level
        value = float(data[0][12])
        format = formats['percentage']
        worksheet.write_number(12, startcol, value, format)

        # above 2x poverty level
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(13, startcol, value, format)

        # without high school diploma
        value = float(data[0][10])
        format = formats['percentage']
        worksheet.write_number(15, startcol, value, format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage']
        worksheet.write_number(16, startcol, value, format)

        # linguistically isolated
        value = float(data[0][13])
        format = formats['percentage']
        worksheet.write_number(18, startcol, value, format)

    def append_data(self, values, worksheet, formats):
        data = deepcopy(values)

        # We need only one row, which will be the sum of all bins except the first one (excluding total and avg...)
        dg_data = self.get_risk_bins(data)
        row_totals = [sum(x) for x in zip(*dg_data)]

        saved_edu_pop = None
        for index in range(1, 15):
            # Education is a special case...we want the population over 25 as the denominator, not the total population!
            if index == 9:
                saved_edu_pop = row_totals[index]

            if index == 10:
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

        # other
        value = float(row_totals[4])
        worksheet.write_number(7, 4, value, format)

        # hispanic
        value = float(row_totals[5])
        worksheet.write_number(8, 4, value, format)

        # below poverty level
        value = float(row_totals[11])
        worksheet.write_number(10, 4, value, format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(11, 4, value, format)

        # below 2x poverty level
        value = float(row_totals[12])
        worksheet.write_number(12, 4, value, format)

        # above 2x poverty level
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(13, 4, value, format)

        # without high school diploma
        value = float(row_totals[10])
        worksheet.write_number(15, 4, value, format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(16, 4, value, format)

        # linguistically isolated
        value = float(row_totals[13])
        worksheet.write_number(18, 4, value, format)
