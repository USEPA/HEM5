from copy import deepcopy

import numpy as np

from com.sca.hem4.ej.data.DataModel import DataModel


class DGSummary():

    def __init__(self, radius, source_category, facility):
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.source_category = source_category
        self.facility = facility
        self.active_columns = [0, 1, 14, 2, 3, 4, 5, 6, 7, 8, 11, 9, 10, 13]

    def create_summary(self, workbook, formats, national_values, state_values, county_values, values, hazard_name=None):

        self.hazard_name = hazard_name
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())

        column_headers = self.get_columns()

        firstcol = 'A'
        lastcol = chr(ord(firstcol) + len(column_headers))
        top_header_coords = firstcol+'1:'+lastcol+'1'

        # Increase the cell size of the merged cells to highlight the formatting.
        worksheet.set_column(top_header_coords, 12)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 24)
        worksheet.set_row(5, 24)
        worksheet.set_row(8, 24)
        worksheet.set_row(16, 30)
        worksheet.set_row(17, 30)
        worksheet.set_row(18, 30)
        worksheet.set_row(19, 30)
        worksheet.set_row(20, 30)
        worksheet.set_row(21, 30)
        worksheet.set_row(22, 30)
        worksheet.set_row(23, 30)
        worksheet.set_row(24, 30)

        # Create top level header
        worksheet.merge_range(top_header_coords, self.get_table_name(),  formats['top_header'])

        # Create column headers
        worksheet.merge_range("A2:B2", '',  formats['sub_header_2'])

        worksheet.set_row(1, 72, formats['sub_header_2'])
        for col_num, data in enumerate(column_headers):
            worksheet.write(1, col_num+1, data)

        # Create sub header 1 (national)
        worksheet.merge_range("A3:P3", 'Nationwide Demographic Breakdown',  formats['sub_header_4'])
        worksheet.merge_range("A4:B4", 'Total population\u1D43')
        worksheet.merge_range("A5:B5", 'Percentage of total')

        # state...
        worksheet.merge_range("A6:P6", 'State Demographic Breakdown',  formats['sub_header_4'])
        worksheet.merge_range("A7:B7", 'Total population\u1D43')
        worksheet.merge_range("A8:B8", 'Percentage of total')

        # county...
        worksheet.merge_range("A9:P9", 'County Demographic Breakdown',  formats['sub_header_4'])
        worksheet.merge_range("A10:B10", 'Total population\u1D43')
        worksheet.merge_range("A11:B11", 'Percentage of total')

        # Create sub header 2
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        worksheet.merge_range("A12:P12", 'Proximity Results plus Modeled ' + self.get_risk_name() + ' from ' + scope,
                              formats['sub_header_4'])

        article = 'any' if self.facility is None else 'the'
        worksheet.merge_range("A13:B13", 'Total population within ' + self.radius + ' km of ' + article + ' facility',
                              formats['sub_header_3'])
        worksheet.merge_range("A14:B14", 'Percentage of total')
        worksheet.merge_range("A15:B15", self.get_risk_header())

        # Create notes
        worksheet.merge_range("A17:H26", self.get_notes(),  formats['notes'])

        self.append_aggregated_data(national_values, worksheet, formats, 3)
        self.append_aggregated_data(state_values, worksheet, formats, 6)
        self.append_aggregated_data(county_values, worksheet, formats, 9)
        self.append_data(values, worksheet, formats)

    def get_columns(self):
        return ['', 'Total Population', 'White', 'Minority\u1D47', 'African American', 'Native American',
                'Other and Multiracial', 'Hispanic or Latino\u1D9C', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'People Living Below the Poverty Level', 'Total Number >= 25 Years Old',
                'Number >= 25 Years Old without a High School Diploma', 'People Living in Linguistic Isolation']

    def get_sheet_name(self):
        return "DG Summary"

    def append_aggregated_data(self, values, worksheet, formats, startrow):

        data = deepcopy(values)

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(data)[row_idx[:, None], col_idx]

        startcol = 2

        numrows = len(slice)
        numcols = len(slice[0])
        for row in range(0, numrows):
            for col in range(0, numcols):

                # total pop kept as raw number, but we're using percentages for the breakdowns...
                value = slice[row][col]
                if value != "":
                    value = float(value)
                    format = formats['percentage'] if value <= 1 else formats['number']
                    worksheet.write_number(startrow+row, startcol+col, value, format)
                else:
                    worksheet.write(startrow+row, startcol+col, value)

        return startrow + numrows

    def append_data(self, values, worksheet, formats):

        data = deepcopy(values)

        # We need three rows, two of which have already been calculated....
        dg_data = data[-2:]
        dg_data.insert(1, [0]*15)

        for index in range(1, 15):
            # Education is a special case...we want the population over 25 as the denominator, not the total population!
            if index == 10:
                dg_data[1][index] = (dg_data[0][index] / dg_data[0][9]) if dg_data[0][9] > 0 else 0
            else:
                dg_data[1][index] = (dg_data[0][index] / dg_data[0][0]) if dg_data[0][0] > 0 else 0

        dg_data[1][0] = ""

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(dg_data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(dg_data)[row_idx[:, None], col_idx]

        startrow = 12
        startcol = 2

        numrows = len(slice)
        numcols = len(slice[0])
        for row in range(0, numrows):
            for col in range(0, numcols):

                value = slice[row][col]
                if value != "":
                    value = float(value)

                    format = formats['percentage'] if row == 1 else formats['number']
                    if row > 1:
                        value = DataModel.round_to_sigfig(value, 2)

                    worksheet.write_number(startrow+row, startcol+col, value, format)
                else:
                    worksheet.write(startrow+row, startcol+col, value)

        return startrow + numrows
