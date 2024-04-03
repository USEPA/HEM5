from copy import deepcopy
import numpy as np
from com.sca.hem4.ej.data.DataModel import DataModel


# A base class from which most other classes in this package inherit. This class provides default functionality for
# creating worksheet cells that is common to most or all tables.
class WorksheetTable:

    def __init__(self, radius, source_category, facility=None):
        self.radius = str(int(radius) if radius.is_integer() else radius)
        self.facility = facility

        # The identifier controls the table name (and sheet) prefix. It depends on cancer (or not) and radius.
        if self.name and self.prefix:
            self.identifier = 'D' if radius < 50 else 'C'
        else:
            self.identifier = 'B' if radius < 50 else 'A'

        self.source_category = source_category

    # Create the main cell structure with headings and names, but no data.
    def create_table(self, workbook, formats, values):
        worksheet = workbook.add_worksheet(name=self.get_sheet_name())
        self.worksheet = worksheet

        column_headers = self.get_columns()

        firstcol = 'A'
        lastcol = chr(ord(firstcol) + len(column_headers))
        top_header_coords = firstcol+'1:'+lastcol+'1'
        top_header_coords_wo_A = 'B1:'+lastcol+'1'

        # Increase the cell size of the merged cells to highlight the formatting.
        worksheet.set_column(0, 0, 40)
        worksheet.set_column(top_header_coords_wo_A, 20)
        worksheet.set_row(0, 55)
        worksheet.set_row(1, 60)
        # worksheet.set_row(2, 28)
        # worksheet.set_row(3, 36)
        # worksheet.set_row(4, 36)
        # worksheet.set_row(17, 30)
        # worksheet.set_row(18, 30)
        # worksheet.set_row(19, 30)
        # worksheet.set_row(20, 30)
        # worksheet.set_row(21, 30)
        # worksheet.set_row(22, 30)

        # Create top level header
        worksheet.merge_range(top_header_coords, self.get_table_name(),  formats['top_header'])

        # Create sub header 1
        worksheet.write('A2', self.get_sub_header_1(),  formats['sub_header_1'])

        # # Create sub header 2
        # firstcol = 'C'
        # lastcol = chr(ord(firstcol) + len(column_headers) - 1)
        # sub_header_coords = firstcol+'2:'+lastcol+'3'
        # worksheet.merge_range(sub_header_coords, self.get_sub_header_2(),  formats['sub_header_2'])

        # Create column headers
        col = 'B'
        for header in column_headers:
            header_coords = col+'2'
            worksheet.write(header_coords, header,  formats['sub_header_3'])
            # worksheet.set_column(top_header_coords, 12)
            col = chr(ord(col) + 1)

        # Add bin headers and data
        bins = self.get_bin_headers()

        row = 3
        for b in bins:
            coords = 'A'+str(row)
            self.worksheet.write(coords, b, formats['sub_header_1'])
            row += 1

        # totals and average headers...
        coords = 'A'+str(row)
        self.worksheet.write(coords, "Total Number", formats['sub_header_1'])
        row += 1
        coords = 'A'+str(row)
        self.worksheet.write(coords, self.get_average_header(), formats['sub_header_1'])

        last_data_row = self.append_data(values=values, worksheet=worksheet, formats=formats)
        
        # Create notes
        first_notes_row = last_data_row + 1
        notes_dict = self.get_notes()
        for note in notes_dict:
            first_notes_row+=1
            if 'note' in note:
                worksheet.write_rich_string('A'+str(first_notes_row), formats['notes'], 
                                            notes_dict[note], ' ')                
            elif note == '*':
                worksheet.write_rich_string('A'+str(first_notes_row), formats['asterik'],
                                            note, ' ', formats['notes'], notes_dict[note])
            else:
                worksheet.write_rich_string('A'+str(first_notes_row), formats['superscript'],
                                            note, ' ', formats['notes'], notes_dict[note])
            
        # worksheet.merge_range(notes_coords, self.get_notes(),  formats['notes'])

        self.optional_format(worksheet)

    # Append the actual data.
    def append_data(self, values, worksheet, formats):

        data = deepcopy(values)

        # First, select the columns that are relevant
        row_idx = np.array([i for i in range(0, len(data))])
        col_idx = np.array(self.active_columns)
        slice = np.array(data)[row_idx[:, None], col_idx]

        startrow = 2
        startcol = 1

        numrows = len(slice)
        numcols = len(slice[0])
        for row in range(0, numrows):
            for col in range(0, numcols):

                # Most values in the table are rounded to the nearest integer, but the average risk / HI is
                # rounded to preserve one sig fig. Note that Excel number formatting seems to do weird things
                # for the value 0, so we're only using it when we get into the thousands or bigger.
                if row == numrows-1:
                    value = DataModel.round_to_sigfig(slice[row][col], 1)
                    floated = float(value)
                else:
                    value = slice[row][col]
                    floated = float(value)
                    if floated < 1:
                        value = '=ROUND(' + str(value) + ', 0)'

                format = formats['number'] if floated > 1 else None
                worksheet.write(startrow+row, startcol+col, value, format)

        return startrow + numrows

    # This is a method that does nothing in the base class, but can be implemented in sub classes to perform formatting
    # that is specific to their table. It is called in the base class and will be a no-op if not implemented.
    def optional_format(self, worksheet):
        pass
