import xlsxwriter

from writer.Writer import Writer

class ExcelWriter(Writer):

    def __init__(self, model, plot_df):
        Writer.__init__(self)

        self.model = model
        self.plot_df = plot_df

    def writeToFile(self):

        if self.filename is None:
            raise RuntimeError("No file name set. Cannot write to file.")

        workbook = xlsxwriter.Workbook(self.filename, {'constant_memory': True})

        worksheet = workbook.add_worksheet()

        self.write_header(worksheet)
        self.write_data(worksheet)

        workbook.close()

    def write_header(self, worksheet):
        """
         Write the header (column names) in the given Excel worksheet.

         :param str worksheet: An Excel worksheet, created by xlsxwriter
         :param str[] headers: An array of column header names
         :return: void
        """

        for i in range(0, len(self.headers)):
            worksheet.write(0, i, self.headers[i])

    def write_data(self, worksheet):

        # With 'constant_memory' you must write data in row by column order.
        for row in range(0, self.data.shape[0]):
            for col in range(0, self.data.shape[1]):
               worksheet.write(row + 1, col, self.data[row][col])
