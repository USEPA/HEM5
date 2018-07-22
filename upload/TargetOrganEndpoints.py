from upload.InputFile import InputFile


class TargetOrganEndpoints(InputFile):

    def __init__(self):
        InputFile.__init__(self, "resources/Target_Organ_Endpoints.xlsx")

    def createDataframe(self):

        # TARGET ORGAN ENDPOINTS excel to dataframe
        # HEADER----------------------
        # pollutant|epa_woe	|resp|liver|neuro|dev|reprod|kidney|ocular|endoc|hemato|immune|skeletal|spleen|thyroid|wholebod
        self.dataframe = self.readFromPath(
            ("pollutant","epa_woe","resp","liver","neuro","dev","reprod","kidney","ocular","endoc","hemato",
             "immune","skeletal","spleen","thyroid","wholebod"))