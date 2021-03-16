from copy import deepcopy

import numpy as np

from com.sca.hem4.ej.data.DataModel import DataModel


class ElaineSummary():

    def __init__(self, radius, cancer_risk_threshold, hi_risk_threshold, source_category):
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.active_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 10, 13, 14]

    def create_summary(self, workbook, formats, national_values, state_values, county_values, values):
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())

        # Increase the cell sizes to match expected content.
        worksheet.set_column("A:A", 24)
        worksheet.set_column("B:B", 16)
        worksheet.set_column("C:C", 24)
        worksheet.set_row(1, 48)
        worksheet.set_row(3, 48)
        worksheet.set_row(23, 30)
        worksheet.set_row(24, 30)
        worksheet.set_row(25, 48)

        worksheet.write(0, 0, 'Table for Preamble')

        # Create top level header
        worksheet.merge_range("A2:E2", self.get_table_header(),  formats['sub_header_2'])

        worksheet.merge_range("A3:E3", '')
        worksheet.write(3, 4, self.get_risk_header(), formats['sub_header_3'])
        worksheet.write(4, 1, 'Nationwide', formats['sub_header_3'])
        worksheet.write(4, 2, 'State', formats['sub_header_3'])
        worksheet.write(4, 3, 'County', formats['sub_header_3'])
        worksheet.write(4, 4, 'Source Category' if self.facility is None else 'Facility', formats['sub_header_3'])
        worksheet.write(5, 0, 'Total Population')

        worksheet.merge_range("C7:D7", 'White and Minority by Percent',  formats['sub_header_3'])

        worksheet.write(7, 0, 'White')
        worksheet.write(8, 0, 'Minority')

        worksheet.merge_range("C10:D10", 'Minority by Percent',  formats['sub_header_3'])
        worksheet.write(10, 0, 'African American')
        worksheet.write(11, 0, 'Native American')
        worksheet.write(12, 0, 'Other and Multiracial')
        worksheet.write(13, 0, 'Hispanic or Latino \u1D43')

        worksheet.merge_range("C15:D15", 'Income by Percent',  formats['sub_header_3'])
        worksheet.write(15, 0, 'Below Poverty Level')
        worksheet.write(16, 0, 'Above Poverty Level')

        worksheet.merge_range("C18:D18", 'Education by Percent',  formats['sub_header_3'])
        worksheet.write(18, 0, 'Over 25 and without a High School Diploma', formats['notes'])
        worksheet.write(19, 0, 'Over 25 and with a High School Diploma', formats['notes'])

        worksheet.merge_range("C21:D21", 'Linguistically Isolated by Percent', formats['sub_header_3'])
        worksheet.write(21, 0, 'Linguistically Isolated')

        # Create notes
        worksheet.merge_range("A23:E27", self.get_notes(),  formats['notes'])

        self.append_aggregated_data(national_values, worksheet, formats, 1)
        self.append_aggregated_data(state_values, worksheet, formats, 2)
        self.append_aggregated_data(county_values, worksheet, formats, 3)
        self.append_data(values, worksheet, formats)

    def get_notes(self):
        return 'Notes:\n\n' + \
               '\u1D43To avoid double counting, the Hispanic or Latino demographic is treated as a distinct category ' + \
               'and is not included in the African American, Native American, or Other and Multiracial demographic categories.'

    def get_sheet_name(self):
        return "OMB Elaine Summary"

    def append_aggregated_data(self, values, worksheet, formats, startcol):
        data = deepcopy(values)

        # For this summary, we only want the percentages, which are in the second row.
        for index in range(1, 15):
            data[0][index] = data[1][index]

        # total pop kept as raw number, but we're using percentages for the breakdowns...
        exposure_value = float(data[0][0])
        worksheet.write_number(5, startcol, exposure_value, formats['number'])

        # white
        value = float(data[0][1])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(7, startcol, DataModel.round_to_sigfig(value, 2), format)

        # non white
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(8, startcol, DataModel.round_to_sigfig(value, 2), format)

        # african american
        value = float(data[0][2])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(10, startcol, DataModel.round_to_sigfig(value, 2), format)

        # native american
        value = float(data[0][3])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(11, startcol, DataModel.round_to_sigfig(value, 2), format)

        # other
        value = float(data[0][4])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(12, startcol, DataModel.round_to_sigfig(value, 2), format)

        # hispanic
        value = float(data[0][5])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(13, startcol, DataModel.round_to_sigfig(value, 2), format)

        # below poverty level
        value = float(data[0][11])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(15, startcol, DataModel.round_to_sigfig(value, 2), format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(16, startcol, DataModel.round_to_sigfig(value, 2), format)

        # without high school diploma
        value = float(data[0][10])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(18, startcol, DataModel.round_to_sigfig(value, 2), format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(19, startcol, DataModel.round_to_sigfig(value, 2), format)

        # linguistically isolated
        value = float(data[0][13])
        format = formats['percentage'] if value < 0.01 else formats['int_percentage']
        worksheet.write_number(21, startcol, DataModel.round_to_sigfig(value, 2), format)

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
        worksheet.write_number(5, 4, exposure_value, formats['number'])

        # from here on out they are all percentages....
        format = formats['percentage']

        # white
        value = float(row_totals[1])
        worksheet.write_number(7, 4, value, format)

        # non white
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(8, 4, value, format)

        # african american
        value = float(row_totals[2])
        worksheet.write_number(10, 4, value, format)

        # native american
        value = float(row_totals[3])
        worksheet.write_number(11, 4, value, format)

        # other
        value = float(row_totals[4])
        worksheet.write_number(12, 4, value, format)

        # hispanic
        value = float(row_totals[5])
        worksheet.write_number(13, 4, value, format)

        # below poverty level
        value = float(row_totals[11])
        worksheet.write_number(15, 4, value, format)

        # above poverty level
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(16, 4, value, format)

        # without high school diploma
        value = float(row_totals[10])
        worksheet.write_number(18, 4, value, format)

        # with high school diploma
        value = 1 - value if exposure_value > 0 else 0
        worksheet.write_number(19, 4, value, format)

        # linguistically isolated
        value = float(row_totals[13])
        worksheet.write_number(21, 4, value, format)
