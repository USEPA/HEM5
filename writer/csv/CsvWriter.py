import csv


class CsvWriter():

    def __init__(self, targetDir):

        self.targetDir = targetDir

    def write(self, name, headers, data):
        
        """
        
        Write an array to a CSV file.
        
        :param str name: Name of CSV file
        :param list headers: A list of column names
        :param array data: An array of data to write
        
        """
        
        csvfile = self.targetDir + name
        fobj = open(csvfile, 'w')
        writer = csv.writer(fobj, delimiter=',', lineterminator='\r\n', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
        
        fobj.close()
        