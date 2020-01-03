import importlib
import os, glob

import com.sca.hem4.writer.excel.summary.MaxRisk as maxRiskReportModule
import com.sca.hem4.writer.excel.summary.CancerDrivers as cancerDriversReportModule
import com.sca.hem4.writer.excel.summary.HazardIndexDrivers as hazardIndexDriversReportModule
import com.sca.hem4.writer.excel.summary.Histogram as histogramModule
import com.sca.hem4.writer.excel.summary.HI_Histogram as hiHistogramModule
import com.sca.hem4.writer.excel.summary.IncidenceDrivers as incidenceDriversReportModule
import com.sca.hem4.writer.excel.summary.AcuteImpacts as acuteImpactsReportModule
import com.sca.hem4.writer.excel.summary.SourceTypeRiskHistogram as sourceTypeRiskHistogramModule
import com.sca.hem4.writer.excel.summary.MultiPathway as multiPathwayModule


class SummaryManager():

    def __init__(self, targetDir, facilitylist):
        
        self.categoryFolder = targetDir
        self.facilityIds = facilitylist

        self.availableReports = {'MaxRisk' : maxRiskReportModule,
                                 'CancerDrivers' : cancerDriversReportModule,
                                 'HazardIndexDrivers' : hazardIndexDriversReportModule,
                                 'Histogram' : histogramModule,
                                 'HI_Histogram' : hiHistogramModule,
                                 'IncidenceDrivers' : incidenceDriversReportModule,
                                 'AcuteImpacts' : acuteImpactsReportModule,
                                 'SourceTypeRiskHistogram' : sourceTypeRiskHistogramModule,
                                 'MultiPathway' : multiPathwayModule}

        # Get modeling group name from the Facililty Max Risk and HI file
        skeleton = os.path.join(self.categoryFolder, '*_facility_max_risk_and_hi.xlsx')
        fname = glob.glob(skeleton)
        if fname:
            head, tail = os.path.split(glob.glob(skeleton)[0])
            self.grpname = tail[:tail.find('facility_max_risk_and_hi')-1]
        else:
            print("Problem. There is no Facility Max Risk and HI file")
            return 

        # Define the arguments needed for each summary module
        self.reportArgs = {'MaxRisk' : None,
                        'CancerDrivers' : None,
                        'HazardIndexDrivers' : None,
                        'Histogram' : None,
                        'HI_Histogram' : None,
                        'IncidenceDrivers' : None,
                        'AcuteImpacts' : None,
                        'SourceTypeRiskHistogram' : [0,2],
                        'MultiPathway' : [self.grpname]}


        
    def createReport(self, categoryFolder, reportName, arguments=None):

        print("\r\n Starting report: " + reportName)
                
        module = self.availableReports[reportName]
        if module is None:
            print("Oops. HEM4 couldn't find your report module.")
            return
        
        arguments = self.reportArgs[reportName]        
        reportClass = getattr(module, reportName)
        instance = reportClass(categoryFolder, self.facilityIds, arguments)
        instance.writeWithTimestamp()

        print("Finished report: " + reportName)

