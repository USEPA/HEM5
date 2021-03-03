from copy import deepcopy

import numpy as np

from com.sca.hem4.ej.data.DataModel import DataModel


class WorksheetTable:

    def __init__(self, radius, source_category, facility=None):
        self.radius = str(radius)
        self.facility = facility

        # The identifier controls the table name (and sheet) prefix. It depends on cancer (or not) and radius.
        if self.name and self.prefix:
            self.identifier = 'D' if radius < 50 else 'C'
        else:
            self.identifier = 'B' if radius < 50 else 'A'

        self.source_category = source_category

    def create_table(self, workbook, formats, values):
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())
        self.worksheet = worksheet

        column_headers = self.get_columns()

        firstcol = 'A'
        lastcol = chr(ord(firstcol) + len(column_headers) + 1)
        top_header_coords = firstcol+'1:'+lastcol+'1'

        # Increase the cell size of the merged cells to highlight the formatting.
        worksheet.set_column(top_header_coords, 12)
        worksheet.set_row(0, 36)
        worksheet.set_row(1, 28)
        worksheet.set_row(2, 28)
        worksheet.set_row(3, 36)
        worksheet.set_row(4, 36)
        worksheet.set_row(17, 30)
        worksheet.set_row(18, 30)
        worksheet.set_row(19, 30)
        worksheet.set_row(20, 30)
        worksheet.set_row(21, 30)
        worksheet.set_row(22, 30)

        # Create top level header
        worksheet.merge_range(top_header_coords, self.get_table_name(),  formats['top_header'])

        # Create sub header 1
        worksheet.merge_range('A2:B5', self.get_sub_header_1(),  formats['sub_header_1'])

        # Create sub header 2
        firstcol = 'C'
        lastcol = chr(ord(firstcol) + len(column_headers) - 1)
        sub_header_coords = firstcol+'2:'+lastcol+'3'
        worksheet.merge_range(sub_header_coords, self.get_sub_header_2(),  formats['sub_header_2'])

        # Create column headers
        col = 'C'
        for header in column_headers:
            header_coords = col+'4:'+col+'5'
            worksheet.merge_range(header_coords, header,  formats['sub_header_3'])
            worksheet.set_column(top_header_coords, 12)
            col = chr(ord(col) + 1)

        # Add bin headers and data
        bins = self.get_bin_headers()

        row = 6
        for b in bins:
            coords = 'A'+str(row)+':B'+str(row)
            self.worksheet.merge_range(coords, b, formats['sub_header_1'])
            row += 1

        # totals and average headers...
        coords = 'A'+str(row)+':B'+str(row)
        self.worksheet.merge_range(coords, "Total Number", formats['sub_header_1'])
        row += 1
        coords = 'A'+str(row)+':B'+str(row)
        self.worksheet.merge_range(coords, self.get_average_header(), formats['sub_header_1'])

        last_data_row = self.append_data(values=values, worksheet=worksheet, formats=formats)

        # Create notes
        first_notes_row = last_data_row + 1
        last_notes_row = first_notes_row + 4
        firstcol = 'A'
        lastcol = chr(ord(firstcol) + len(column_headers) + 1)
        notes_coords = firstcol+str(first_notes_row)+':'+lastcol+str(last_notes_row)
        worksheet.merge_range(notes_coords, self.get_notes(),  formats['notes'])

        self.optional_format(worksheet)

    def append_data(self, values, worksheet, formats):

        data = deepcopy(values)

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(data)[row_idx[:, None], col_idx]

        startrow = 5
        startcol = 2

        numrows = len(slice)
        numcols = len(slice[0])
        for row in range(0, numrows):
            for col in range(0, numcols):

                # Most values in the table are rounded to the nearest integer, but the average risk / HI is
                # rounded to preserve one sig fig. Note that Excel number formatting seems to do weird things
                # for the value 0, so we're only using it when we get into the thousands or bigger.
                value = DataModel.round_to_sigfig(slice[row][col], 2) if row == numrows-1 else slice[row][col]
                format = formats['number'] if value > 1 else None
                if value < 1:
                    value = '=ROUND(' + str(value) + ', 0)'

                worksheet.write(startrow+row, startcol+col, value, format)

        return startrow + numrows

    def optional_format(self, worksheet):
        pass
