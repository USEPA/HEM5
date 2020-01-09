from com.sca.hem4.writer.excel.InputSelectionOptions import InputSelectionOptions


class AltRecAwareSummary:

    def __init__(self):
        pass

    def determineAltRec(self, targetDir, facilityId):

        # Open InputSelectionOptions to determine if alternate receptors were used for this output
        inputops = InputSelectionOptions(targetDir=targetDir, facilityId=facilityId)
        inputops_df = inputops.createDataframe()
        return inputops_df['alt_rec'].iloc[0]

