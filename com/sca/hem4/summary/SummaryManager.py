
import traceback

import com.sca.hem4.writer.excel.summary.MaxRisk as maxRiskReportModule
import com.sca.hem4.writer.excel.summary.CancerDrivers as cancerDriversReportModule
import com.sca.hem4.writer.excel.summary.HazardIndexDrivers as hazardIndexDriversReportModule
import com.sca.hem4.writer.excel.summary.Histogram as histogramModule
import com.sca.hem4.writer.excel.summary.HI_Histogram as hiHistogramModule
import com.sca.hem4.writer.excel.summary.IncidenceDrivers as incidenceDriversReportModule
import com.sca.hem4.writer.excel.summary.AcuteImpacts as acuteImpactsReportModule
import com.sca.hem4.writer.excel.summary.SourceTypeRiskHistogram as sourceTypeRiskHistogramModule
import com.sca.hem4.writer.excel.summary.MultiPathway as multiPathwayModule
import com.sca.hem4.writer.excel.summary.MultiPathwayNonCensus as multiPathwayModuleNonCensus
import com.sca.hem4.writer.excel.summary.MaxConcentrationLocator as maxConcentrationLocatorModule
import com.sca.hem4.writer.excel.summary.SourcePollutantMaxRisk as sourcePollutantMaxRiskModule

from com.sca.hem4.log import Logger
from com.sca.hem4.visualize.AcuteImpactsVisualizer import AcuteImpactsVisualizer
from com.sca.hem4.writer.excel.summary.AltRecAwareSummary import AltRecAwareSummary

#maxRiskReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MaxRisk")
#cancerDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.CancerDrivers")
#hazardIndexDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.HazardIndexDrivers")
#histogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.Histogram")
#hiHistogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.HI_Histogram")
#incidenceDriversReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.IncidenceDrivers")
#acuteImpactsReportModule = importlib.import_module("com.sca.hem4.writer.excel.summary.AcuteImpacts")
#sourceTypeRiskHistogramModule = importlib.import_module("com.sca.hem4.writer.excel.summary.SourceTypeRiskHistogram")
#multiPathwayModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MultiPathway")
#multiPathwayModuleNonCensus = importlib.import_module("com.sca.hem4.writer.excel.summary.MultiPathwayNonCensus")
#maxConcentrationLocatorModule = importlib.import_module("com.sca.hem4.writer.excel.summary.MaxConcentrationLocator")
#sourcePollutantMaxRiskModule = importlib.import_module("com.sca.hem4.writer.excel.summary.SourcePollutantMaxRisk")


class SummaryManager(AltRecAwareSummary):

    def __init__(self, targetDir, groupName, facilitylist):
        
        self.status = False
        self.categoryFolder = targetDir
        self.grpname = groupName
        self.facilityIds = facilitylist

        self.availableReports = {'MaxRisk' : maxRiskReportModule,
                                 'CancerDrivers' : cancerDriversReportModule,
                                 'HazardIndexDrivers' : hazardIndexDriversReportModule,
                                 'Histogram' : histogramModule,
                                 'HI_Histogram' : hiHistogramModule,
                                 'IncidenceDrivers' : incidenceDriversReportModule,
                                 'AcuteImpacts' : acuteImpactsReportModule,
                                 'SourceTypeRiskHistogram' : sourceTypeRiskHistogramModule,
                                 'MultiPathway' : multiPathwayModule,
                                 'MultiPathwayNonCensus' : multiPathwayModuleNonCensus,
                                 'MaxConcentrationLocator' : maxConcentrationLocatorModule,
                                 'SourcePollutantMaxRisk' : sourcePollutantMaxRiskModule}

        self.afterReportRun = {'AcuteImpacts' : self.visualizeAcuteImpacts}
        
    def createReport(self, categoryFolder, reportName, arguments=None):

        # Multipathway and Max Conc have two implementation classes, one for the standard
        # case and one for when alternate receptors are used. But we don't expose that split
        # to users, therefore we run the alt rec summary when needed and determine that here. Since we can
        # assume that all facilities run in the same category used alternate receptors (or not...)
        # we only need to check the first one to decide.

        self.status = False
        
        try:
            # First determine if alternate receptors were used
            altrec = self.determineAltRec(categoryFolder)
            if altrec == 'Y' and reportName == 'MultiPathway':
                reportName = "MultiPathwayNonCensus"
            
            module = self.availableReports[reportName]
            if module is None:
                Logger.logMessage("Oops. HEM4 couldn't find your report module.")
                return
            
            reportClass = getattr(module, reportName)
            reportArgs = [self.grpname, arguments]
            instance = reportClass(categoryFolder, self.facilityIds, reportArgs)
            instance.writeWithTimestamp()
    
            if reportName in self.afterReportRun:
                Logger.logMessage("Running post-report action for " + reportName)
                action = self.afterReportRun[reportName]
                action(categoryFolder)
                Logger.logMessage("Finished post-report action for " + reportName)
                
        except Exception as e:
             var = traceback.format_exc()
             Logger.logMessage("An error occured while creating report: " + reportName)
             Logger.logMessage(var)            
             print(e)
             self.status = False
             
        else:
            self.status = True

    def visualizeAcuteImpacts(self, categoryFolder):
        visualizer = AcuteImpactsVisualizer(sourceDir=categoryFolder)
        visualizer.visualize()

