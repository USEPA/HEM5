import xlsxwriter


class OutputWriter():

    def __init__(self, targetDir):

        self.targetDir = targetDir

    def write(self, name, headers, data):

        workbook = xlsxwriter.Workbook(self.targetDir + name, {'constant_memory': True})

        worksheet = workbook.add_worksheet()

        self.write_header(worksheet, headers)
        self.write_data(worksheet, data)

        workbook.close

    def write_header(self, worksheet, headers):
        """
         Write the header (column names) in the given Excel worksheet.

         :param str worksheet: An Excel worksheet, created by xlsxwriter
         :param str[] headers: An array of column header names
         :return: void
        """

        for i in range(0, len(headers)):
            worksheet.write(0, i, headers[i])

    def write_data(self, worksheet, data):

        # With 'constant_memory' you must write data in row by column order.
        for row in range(0, data.shape[0]):
            for col in range(0, data.shape[1]):
                worksheet.write(row + 1, col, data[row][col])
