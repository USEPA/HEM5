from copy import deepcopy

import numpy as np

from com.sca.hem4.ej.data.DataModel import DataModel


class KCSummary():

    def __init__(self, radius, cancer_risk_threshold, hi_risk_threshold, source_category, facility):
        self.cancer_risk_threshold = str(cancer_risk_threshold)
        self.hi_risk_threshold = str(hi_risk_threshold)
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.source_category = source_category
        self.facility = facility
        self.active_columns = [0, 15, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 11, 14, 17]

    def create_summary(self, workbook, formats, national_values, state_values, county_values, values, max_value,
                       hazard_name=None):
        self.hazard_name = hazard_name
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())

        column_headers = self.get_columns()

        firstcol = 'A'
        lastcol = chr(ord(firstcol) + len(column_headers))
        title_header_coords = firstcol+'1:'+lastcol+'1'
        top_header_coords = 'B1:'+lastcol+'1'

        # Increase the cell size of the merged cells to highlight the formatting.
        worksheet.set_column(top_header_coords, 14)
        worksheet.set_column("A:A", 36)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 30)
        worksheet.set_row(3, 30)
        worksheet.set_row(4, 30)
        worksheet.set_row(6, 30)

        # Create top level header
        worksheet.merge_range(title_header_coords, self.get_table_name(),  formats['top_header'])

        # Row headers
        worksheet.write("A2", 'Population Basis',  formats['sub_header_2'])
        worksheet.write(2, 0, 'Nationwide \u02b0')
        worksheet.write(3, 0, 'State \u02b0')
        worksheet.write(4, 0, 'County \u02b0')
        worksheet.write(5, 0, ' ')
        worksheet.write_rich_string(6, 0, self.get_risk_header()
                                  , formats['superscript'], ' i, j', formats['wrap'])
        
  
        # Create column headers
        worksheet.set_row(1, 72, formats['sub_header_2'])
        for col_num, data in enumerate(column_headers):
            worksheet.write(1, col_num+1, data)


        # Write notes
        notes_dict = self.get_notes(max_value)
        notes_row = 9
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

        self.append_aggregated_data(national_values, worksheet, formats, 2)
        self.append_aggregated_data(state_values, worksheet, formats, 3)
        self.append_aggregated_data(county_values, worksheet, formats, 4)
        self.append_data(values, worksheet, formats)

    def get_table_name(self):
        scope = 'the ' + self.source_category + ' Source Category' if self.facility is None else \
            'Facility ' + self.facility
        return 'Demographic Assessment of ' + self.hazard_name + ' Hazard Index Results for ' + \
               scope + ' - ' + self.radius + ' km Study Area Radius \u1d43'

    def get_columns(self):
        return ['Total Population', 'People of Color \u1D47', 'Black', 'American Indian or Alaska Native', 'Asian',
                'Other and Multiracial', 'Hispanic or Latino \u1D9C', 'Age (Years)\n0-17', 'Age (Years)\n18-64',
                'Age (Years)\n>=65', 'Below the Poverty Level \u1d48', 'Below Twice the Poverty Level \u1d48',
                'Over 25 Without a High School Diploma \u1d49', 'People Living in Limited English Speaking Households \u1da0',
                'People with One or More Disabilities \u1d4d']

    def get_sheet_name(self):
        return "Pop. At Risk Summary"

    def append_aggregated_data(self, values, worksheet, formats, startrow):

        data = deepcopy(values)

        # For this summary, we only want the percentages, which are in the second row.
        for index in range(1, 18):
            data[0][index] = data[1][index]

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(data)[row_idx[:, None], col_idx]

        startcol = 1

        numrows = len(slice) - 1
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

        # We need only one row, which will be the sum of all bins except the first n (depending on risk threshold and
        # excluding total and avg...)
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

        # First, select the columns that are relevant
        slice = []
        for c in self.active_columns:
            slice.append(row_totals[c])

        startrow = 6
        startcol = 1

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

