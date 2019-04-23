from com.sca.hem4.summary.MaxRiskSummary import MaxRiskSummary
import importlib

class SummaryManager():

    def __init__(self):
        self.facilityIds = []

        maxRiskReportModule = importlib.import_module("com.sca.hem4.summary.MaxRiskSummary")

        self.availableReports = {'MaxRiskSummary' : maxRiskReportModule}
    def createReport(self, categoryFolder, reportName):

        # Figure out which facilities will be included in the report
        self.facilityIds = self.findFacilities(categoryFolder)

        print("Running report with ids: " + str(self.facilityIds))

        module = self.availableReports[reportName]
        if module is None:
            print("oops. couldn't find your report module.")
            return

        class_ = getattr(module, reportName)
        instance = class_()
        instance.create()

    def findFacilities(self, folder):

        # TODO
        # consult an xls file in the given folder to get the list dynamically...

        return ['01097110017408296', '01129110000605051', '06013110000602544', '17041110040961965', '17091110043972207',
                '21111110040920242', '21157110000380061', '22005110000597364', '22005110000597373', '22005110012818745',
                '22033110003266849', '22047110001244724', '22089110013662009', '26111110027360629', '34015110000582003',
                '36091110000324435', '39153110041418338', '48039110008170237', '54107110000586081']

manager = SummaryManager()
manager.createReport("HCL2", "MaxRiskSummary")