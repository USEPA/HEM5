from upload.InputFile import InputFile

class DoseResponse(InputFile):

    def __init__(self):
        InputFile.__init__(self, "resources/Dose_response_library.xlsx")

    def createDataframe(self):

        # DOSE RESPONSE excel to dataframe
        # HEADER----------------------
        # pollutant|pollutant group|cas no|URE 1/(µg/m3)|RFC (mg/m3)|aegl_1 (1-hr) (mg/m3)|aegl_1 (8-hr) (mg/m3)|
        # aegl_2 (1 hr) (mg/m3)|aegl_2 (8 hr) (mg/m3)|erpg_1 (mg/m3)|erpg_2 (mg/m3)|mrl (mg/m3)|rel  (mg/m3)|
        # idlh_10 (mg/m3)|teel_0 (mg/m3)|teel_1 (mg/m3)|comments|comments_on_D/R_values|group URE|Tef|minimum acute reference conc (mg/m3)
        self.dataframe = self.readFromPath(
            ("pollutant","group","cas_no","ure","rfc","aegl_1_1h","aegl_1_8h","aegl_2_1h","aegl_2_8h","erpg_1","erpg_2",
             "mrl","rel","idlh_10","teel_0","teel_1","comments","drvalues","group_ure","tef","acute_con"),
            {"pollutant":str,"group":str,"cas_no":str,"ure":float,"rfc":float,"aegl_1_1h":float,"aegl_1_8h":float,
             "aegl_2_1h":float,"aegl_2_8h":float,"erpg_1":float,"erpg_2":float,"mrl":float,"rel":float,"idlh_10":float,
             "teel_0":float,"teel_1":float,"comments":str,"drvalues":float,"group_ure":float,"tef":float,"acute_con":float})