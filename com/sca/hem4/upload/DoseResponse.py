from tkinter import messagebox

from com.sca.hem4.log import Logger
from com.sca.hem4.upload.InputFile import InputFile
from com.sca.hem4.model.Model import *

ure = 'ure';
rfc = 'rfc';
aegl_1_1h = 'aegl_1_1h';
aegl_2_1h = 'aegl_2_1h';
erpg_1 = 'erpg_1';
erpg_2 = 'erpg_2';
rel = 'rel';
cas_no = 'cas_no';

class DoseResponse(InputFile):

    def __init__(self):
        InputFile.__init__(self, "resources/Dose_Response_Library.xlsx")

    def clean(self, df):

        cleaned = df.fillna(0)

        # lower case the pollutant name for easier merging later
        cleaned[pollutant] = cleaned[pollutant].str.lower()

        return cleaned

    def validate(self, df):

        # ----------------------------------------------------------------------------------
        # Strict: Invalid values in these columns will cause the upload to fail immediately.
        # ----------------------------------------------------------------------------------
        duplicates = self.duplicates(df, [pollutant])
        if len(duplicates) > 0:
            Logger.logMessage("One or more records are duplicated in the Dose Response file (key=pollutant):")
            for d in duplicates:
                Logger.logMessage(d)

            Logger.logMessage("Please remove the duplicate records and restart HEM.")
            return None
        else:
            return df

    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [ure, rfc,aegl_1_1h,aegl_2_1h,erpg_1,erpg_2,rel]
        self.strColumns = [pollutant,group,cas_no]

        # DOSE RESPONSE excel to dataframe
        # HEADER----------------------
        # pollutant|pollutant group|cas no|URE 1/(µg/m3)|RFC (mg/m3)|aegl_1 (1-hr) (mg/m3)|
        # aegl_2 (1 hr) (mg/m3)|erpg_1 (mg/m3)|erpg_2 (mg/m3)|rel
        
        # columns to remove on 11/18/24: aegl_1_8h, aegl_2_8h, mrl, idlh_10, teel_0, teel_1, comments,
        #                                drvalues,group_ure,tef,acute_con
        self.dataframe = self.readFromPath(
            (pollutant,group,cas_no,ure,rfc,aegl_1_1h,aegl_2_1h,erpg_1,erpg_2,rel))
