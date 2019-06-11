import importlib

class SummaryManager():

    def __init__(self):
        self.facilityIds = []

        maxRiskReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MaxRisk")
        cancerDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.CancerDrivers")
        hazardIndexDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.HazardIndexDrivers")
        histogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.Histogram")

        self.availableReports = {'MaxRisk' : maxRiskReportModule,
                                 'CancerDrivers' : cancerDriversReportModule,
                                 'HazardIndexDrivers' : hazardIndexDriversReportModule,
                                 'Histogram' : histogramModule}

    def createReport(self, categoryFolder, reportName):

        # Figure out which facilities will be included in the report
        self.facilityIds = self.findFacilities(categoryFolder)

        print("Running report with ids: " + str(self.facilityIds))

        module = self.availableReports[reportName]
        if module is None:
            print("Oops. HEM4 couldn't find your report module.")
            return

        reportClass = getattr(module, reportName)
        instance = reportClass(categoryFolder, self.facilityIds)
        instance.write()

    def findFacilities(self, folder):

        # TODO
        # consult an xls file in the given folder to get the list dynamically...

        # ALDT
        return ['01101110017378372','01121110012234251','01125110000367246','06001110000482898','13285110038902015',
                '17007110000436314','17031110000435191','17113110000438223','18003110000792786','18031110031113202',
                '18051110007363129','18157110000404205','20209110001307924','21111110000378671','21111110001374094',
                '21209110000378840','21227110000568350','26045110025333388','26049110017406216','26065110013287380',
                '26099110000405393','26099110017425375','26125110000404759','26163110000405696','26163110000406837',
                '26163110000605685','26163110012385285','26163110050297718','28145110038878550','29047110017435783',
                '29183110018010365','39091110000382979','39093110000385164','39095110000384156','39095110022477416',
                '39155110009631988','39159110043812158','45083110000587650','47065110046123805','47119110000370768',
                '47149110000370688','48029110020572389','48439110001868658']

        # HCL2
        # return ['01097110017408296', '01129110000605051', '06013110000602544', '17041110040961965', '17091110043972207',
        #         '21111110040920242', '21157110000380061', '22005110000597364', '22005110000597373', '22005110012818745',
        #         '22033110003266849', '22047110001244724', '22089110013662009', '26111110027360629', '34015110000582003',
        #         '36091110000324435', '39153110041418338', '48039110008170237', '54107110000586081']

manager = SummaryManager()
manager.createReport("output/ALDT", "Histogram")