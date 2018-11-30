import csv
from writer.Writer import Writer

class CsvWriter(Writer):

    def __init__(self, model, plot_df):
        Writer.__init__(self)

        self.model = model
        self.plot_df = plot_df

    def writeToFile(self):
        """

        Write an array to a CSV file.

        :param str name: Name of CSV file
        :param list headers: A list of column names
        :param array data: An array of data to write

        """

        if self.filename is None:
            raise RuntimeError("No file name set. Cannot write to file.")

        fobj = open(self.filename, 'w', newline='')
        writer = csv.writer(fobj, delimiter=',', lineterminator='\r\n', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(self.headers)
        for row in self.data:
            # writer.writerow(row)
            writer.writerow([float('{:6.12}'.format(x)) if isinstance(x, float) else x for x in row])
        
        fobj.close()
        