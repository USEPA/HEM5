from copy import deepcopy

import numpy as np

from com.sca.ej.data.DataModel import DataModel


class KCSummary():

    def __init__(self, radius, source_category):
        self.radius = str(radius)
        self.source_category = source_category
        self.active_columns = [0, 14, 2, 3, 4, 5, 6, 7, 8, 11, 10, 13]

    def create_summary(self, workbook, formats, national_values, values, max_value, hazard_name=None):
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
        worksheet.set_row(3, 30)
        worksheet.set_row(5, 30)
        worksheet.set_row(6, 30)
        worksheet.set_row(10, 30)
        worksheet.set_row(11, 30)
        worksheet.set_row(12, 30)
        worksheet.set_row(13, 30)
        worksheet.set_row(14, 30)
        worksheet.set_row(15, 30)

        # Create top level header
        worksheet.merge_range(top_header_coords, self.get_table_name(),  formats['top_header'])

        # Create column headers
        worksheet.merge_range("A2:A3", 'Population Basis',  formats['sub_header_2'])
        worksheet.write(3, 0, 'Nationwide')
        worksheet.merge_range("B2:N2", 'Demographic Group',  formats['sub_header_3'])

        worksheet.set_row(2, 60, formats['sub_header_2'])
        for col_num, data in enumerate(column_headers):
            worksheet.write(2, col_num+1, data)

        worksheet.write(5, 1, self.get_max_risk_header(), formats['sub_header_3'])
        worksheet.write(6, 0, 'Source Category')
        worksheet.write(6, 1, max_value)
        worksheet.merge_range("A5:N5", '')
        worksheet.merge_range("C6:N6", self.get_risk_header(),  formats['sub_header_3'])

        # Create notes
        worksheet.merge_range("A9:H12", self.get_notes(),  formats['notes'])

        self.append_national_data(national_values, worksheet, formats)
        self.append_data(values, worksheet, formats)

    def get_table_name(self):
        return 'Table 2. Summary of Demographic Assessment of ' + self.hazard_name + ' Hazard Index Results for the ' + \
               self.source_category + ' Source Category - ' + self.radius + ' km Study Area Radius'

    def get_columns(self):
        return ['', 'Total', 'Minority', 'African American', 'Native American',
                'Other and Multiracial', 'Hispanic or Latino', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'Below the Poverty Level', 'Over 25 Without a High School Diploma',
                'Linguistically Isolated']

    def get_sheet_name(self):
        return "KC Summary"

    def append_national_data(self, national_values, worksheet, formats):

        data = deepcopy(national_values)

        # For this summary, we only want the percentages, which are in the second row.
        for index in range(1, 15):
            data[0][index] = data[1][index]

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(data)[row_idx[:, None], col_idx]

        startrow = 3
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

        # We need only one row, which will be the sum of all bins except the first one (excluding total and avg...)
        dg_data = data[1:11]
        row_totals = [sum(x) for x in zip(*dg_data)]

        saved_edu_pop = None
        for index in range(1, 15):
            # Education is a special case...we want the population over 25 as the denominator, not the total population!!
            if index == 9:
                saved_edu_pop = row_totals[index]

            if index == 10:
                row_totals[index] = (row_totals[index] / saved_edu_pop) if saved_edu_pop > 0 else 0
            else:
                row_totals[index] = (row_totals[index] / row_totals[0]) if row_totals[0] > 0 else 0

        # First, select the columns that are relevant
        slice = []
        for c in self.active_columns:
            slice.append(row_totals[c])

        startrow = 6
        startcol = 2

        numcols = len(slice)

        for col in range(0, numcols):

            # total pop kept as raw number, but we're using percentages for the breakdowns...
            value = slice[col]
            if value != "":
                value = float(value)
                format = formats['percentage'] if col > 0 else formats['number']
                worksheet.write_number(startrow, startcol+col, value, format)
            else:
                worksheet.write(startrow, startcol+col, value)

        return startrow + 1
