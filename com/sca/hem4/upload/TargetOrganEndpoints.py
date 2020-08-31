from com.sca.hem4.model.Model import pollutant
from com.sca.hem4.upload.InputFile import InputFile

epa_woe = 'epa_woe';
resp = 'resp';
liver = 'liver';
neuro = 'neuro';
dev = 'dev';
reprod = 'reprod';
kidney = 'kidney';
ocular = 'ocular';
endoc = 'endoc';
hemato = 'hemato';
immune = 'immune';
skeletal = 'skeletal';
spleen = 'spleen';
thyroid = 'thyroid';
wholebod = 'wholebod';

class TargetOrganEndpoints(InputFile):

    def __init__(self):
        InputFile.__init__(self, "resources/Target_Organ_Endpoints.xlsx")

    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [resp,liver,neuro,dev,reprod,kidney,ocular,endoc,hemato,
                               immune,skeletal,spleen,thyroid,wholebod]
        self.strColumns = [pollutant,epa_woe]

        # TARGET ORGAN ENDPOINTS excel to dataframe
        # HEADER----------------------
        # pollutant|epa_woe	|resp|liver|neuro|dev|reprod|kidney|ocular|endoc|hemato|immune|skeletal|spleen|thyroid|wholebod
        self.dataframe = self.readFromPath(
            (pollutant,epa_woe,resp,liver,neuro,dev,reprod,kidney,ocular,endoc,hemato,
             immune,skeletal,spleen,thyroid,wholebod))
        
        # Replace NaN's with 0
        self.dataframe.fillna(0, inplace=True)
        
        # Lower case the pollutant name for easier merging later
        self.dataframe[pollutant] = self.dataframe[pollutant].str.lower()

