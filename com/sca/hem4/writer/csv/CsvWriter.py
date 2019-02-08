import csv
from com.sca.hem4.writer.Writer import Writer

class CsvWriter(Writer):

    def __init__(self, model, plot_df):
        Writer.__init__(self)

        self.model = model
        self.plot_df = plot_df

    def appendToFile(self, dataframe):
        """
        Append the given data to a CSV file which is presumed to already exist.
        """
        data = dataframe.values
        with open(self.filename, 'a', encoding='UTF-8', newline='') as csvarchive:
            writer = csv.writer(csvarchive, quoting=csv.QUOTE_NONNUMERIC)
            self.writeFormatted(writer, data)

    def writeHeader(self):
        with open(self.filename, 'w', encoding='UTF-8', newline='') as csvarchive:
            writer = csv.writer(csvarchive, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(self.getHeader())

    def analyze(self, data):
        pass

    def writeFormatted(self, writer, data):
        """
        Write a row of data using preset formatting.
        """
        for row in data:
            writer.writerow([float('{:6.12}'.format(x)) if isinstance(x, float) else x for x in row])