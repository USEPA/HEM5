from copy import deepcopy
import numpy as np
from com.sca.hem4.ej.data.DataModel import DataModel


class FacilitySummary():

    # Class level data structures that allow for appending facility data to an existing worksheet in the right place.
    sheets = {}
    lines = {}

    def __init__(self, facilityId, radius, cancer_risk_threshold, hi_risk_threshold, source_category):
        self.facilityId = facilityId
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.source_category = source_category
        self.active_columns = [0, 14, 2, 3, 4, 5, 6, 7, 8, 11, 10, 13]

    @staticmethod
    def init_sheets():
        FacilitySummary.sheets = {}
        FacilitySummary.lines = {}

    def create_summary(self, workbook, formats, national_values, values, run_group_values, hazard_name=None):

        self.hazard_name = hazard_name

        # If there is no sheet with this name, create it (and add the current facility info).
        # If there is a sheet but it already has this facility, skip it.
        # If there is a sheet without this facility, add it.
        sheet_name = self.get_sheet_name()
        sheets_key = sheet_name + str(self.radius) + (hazard_name if hazard_name is not None else "cancer")
        lines_key = sheets_key + str(self.facilityId)
        if sheets_key in FacilitySummary.sheets.keys():
            if lines_key in FacilitySummary.lines.keys():
                return
            else:
                worksheet = FacilitySummary.sheets[sheets_key]

                # Get the next line for this sheet. Note that the lines data structure holds the next line for
                # all sheets across all workbooks, so we have to specifically get the next line for -this- sheet.
                max_line_this_sheet = 0
                for key in FacilitySummary.lines.keys():
                    if sheets_key in key:
                        value = FacilitySummary.lines[key]
                        if value > max_line_this_sheet:
                            max_line_this_sheet = value

                next_line = max_line_this_sheet + 1
        else:
            worksheet = workbook.add_worksheet(name=sheet_name)

            column_headers = self.get_columns()

            firstcol = 'A'
            lastcol = chr(ord(firstcol) + len(column_headers))
            top_header_coords = firstcol+'1:'+lastcol+'1'

            # Increase the cell size of the merged cells to highlight the formatting.
            worksheet.set_column(top_header_coords, 12)
            worksheet.set_row(0, 30)
            worksheet.set_row(2, 24)

            # Create top level header
            worksheet.merge_range(top_header_coords, self.get_table_name(), formats['top_header'])

            # Create column headers
            worksheet.merge_range("A2:A3", 'Population Basis',  formats['sub_header_2'])
            worksheet.write(3, 0, 'Nationwide')
            worksheet.merge_range("B2:N2", 'Demographic Group',  formats['sub_header_3'])

            worksheet.set_row(2, 60, formats['sub_header_2'])
            for col_num, data in enumerate(column_headers):
                worksheet.write(2, col_num+1, data)

            worksheet.merge_range("A5:N5", '')

            worksheet.merge_range("A6:A7", self.source_category, formats['sub_header_1'])
            worksheet.write(5, 1, 'Proximity')
            worksheet.write(6, 1, self.get_risk_label())

            next_line = 6
            self.append_data(run_group_values, worksheet, formats, next_line-1)

            worksheet.merge_range("A8:N8", '')

            self.append_national_data(national_values, worksheet, formats)

            FacilitySummary.sheets[sheets_key] = worksheet
            next_line = 9

        # Update the worksheet with current facility info on next line
        facility_range = 'A' + str(next_line) + ':A' + str(next_line+1)
        worksheet.merge_range(facility_range, self.facilityId, formats['sub_header_3'])
        worksheet.write(next_line-1, 1, 'Proximity')
        worksheet.write(next_line, 1, self.get_risk_label())

        self.append_data(values, worksheet, formats, next_line-1)

        FacilitySummary.lines[lines_key] = next_line + 1

    def get_risk_label(self):
        return ''

    def get_table_name(self):
        return ''

    def get_columns(self):
        return ['', 'Total', 'Minority', 'African American', 'Native American',
                'Other and Multiracial', 'Hispanic or Latino', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'Below the Poverty Level', 'Over 25 Without a High School Diploma',
                'Linguistically Isolated']

    def get_sheet_name(self):
        return "Facility Summary"

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

    def append_data(self, values, worksheet, formats, startrow):

        # First line is same as DGSummary...
        data = deepcopy(values)
        dg_data = data[-2:]
        dg_data.insert(1, [0]*15)

        for index in range(1, 15):
            # Education is a special case..we want the population over 25 as the denominator, not the total population!
            if index == 10:
                dg_data[1][index] = (dg_data[0][index] / dg_data[0][9]) if dg_data[0][9] > 0 else 0
            else:
                dg_data[1][index] = (dg_data[0][index] / dg_data[0][0]) if dg_data[0][0] > 0 else 0

        dg_data[1][0] = ""

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(dg_data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(dg_data)[row_idx[:, None], col_idx]

        startcol = 2

        row = 0
        numcols = len(slice[0])
        for col in range(0, numcols):

            # Most values in the table are rounded to the nearest integer, but the average risk / HI is
            # rounded to preserve one sig fig.
            value = slice[row][col] if col == 0 else slice[1][col]
            if value != "":
                value = float(value)

                format = None
                if col == 0:
                    format = formats['number']
                else:
                    format = formats['percentage']

                worksheet.write_number(startrow+row, startcol+col, value, format)
            else:
                worksheet.write(startrow+row, startcol+col, value)

        # Second line is same as KCSummary...
        # We need only one row, which will be the sum of all bins except the first n (depending on risk threshold and
        # excluding total and avg...)
        dg_data = self.get_risk_bins(data)
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

        startrow += 1
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
