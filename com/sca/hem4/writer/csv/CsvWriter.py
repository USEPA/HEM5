import csv
import os
import re

from com.sca.hem4.writer.Writer import Writer

class CsvWriter(Writer):

    def __init__(self, model, plot_df):
        Writer.__init__(self)

        self.model = model
        self.plot_df = plot_df

    def appendToFile(self, dataframe):
        """
        Append the given data to a CSV file which is presumed to already exist. If the file has gotten too big,
        start a new one before writing this data.
        """
        statinfo = os.stat(self.filename)
        size = statinfo.st_size # file size in bytes
        if self.fileTooBig(size):
            self.startNewFile()

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

    def fileTooBig(self, size):
        threshold = 1024 * 1024 * 1024 * 1.5
        return True if size >= threshold else False

    def startNewFile(self):
        filenameNoExtension = os.path.splitext(self.filename)[0]

        # Does the filename already end in a digit?
        m = re.search(r'\d+$', self.filename)
        part = m.group() if m is not None else 2

        self.filename = filenameNoExtension + "_part" + str(part) + ".csv"