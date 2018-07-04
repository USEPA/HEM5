from upload.InputFile import InputFile
from tkinter import messagebox

class HAPEmissions(InputFile):

    def __init__(self, path):
        InputFile.__init__(self, path)

    def createDataframe(self):

        #HAP EMISSIONS excel to dataframe
        # HEADER------------------------
        # FacilityID|SourceID|HEM3chem|SumEmissionTPY|FractionParticulate
        hapemis_df = self.readFromPath(
            ("fac_id","source_id","pollutant","emis_tpy","part_frac"),
            {0:str,1:str,2:str,3:float,4:float})

        #fill Nan with 0
        hapemis_df.fillna(0)

        #turn part_frac into a decimal
        hapemis_df['part_frac'] = hapemis_df['part_frac'] / 100

        #create additional columns, one for particle mass and the other for gas/vapor mass...
        hapemis_df['particle'] = hapemis_df['emis_tpy'] * hapemis_df['part_frac']
        hapemis_df['gas'] = hapemis_df['emis_tpy'] * (1 - hapemis_df['part_frac'])

        #get list of pollutants from dose library
        dose = self.read('resources/Dose_Response_Library.xlsx')
        master_list = list(dose['Pollutant'])
        lower = [x.lower() for x in master_list]

        user_haps = set(hapemis_df['pollutant'])
        missing_pollutants = []

        for hap in user_haps:
            if hap.lower() not in lower:
                missing_pollutants.append(hap)


        #                missing_pollutants = {}
        #                for row in self.hapemis_df.itertuples():
        #
        #                    if row[3].lower() not in lower:
        #
        #                        if row[1] in missing_pollutants.keys():
        #
        #                            missing_pollutants[row[1]].append(row[3])
        #
        #                        else:
        #                            missing_pollutants[row[1]] = [row[3]]
        #
        #                for key in missing_pollutants.keys():
        #                    missing_pollutants[key] = ', '.join(missing_pollutants[key])


        self.log = []
        #if there are any missing pollutants
        if len(missing_pollutants) > 0:
            fix_pollutants = messagebox.askyesno("Missing Pollutants in dose response library", "The following pollutants were not found in HEM4's Dose Response Library: " + ', '.join(missing_pollutants) + ".\n Would you like to add them to the dose response library in the resources folder (they will be removed otherwise). ")
            #if yes, clear box and empty dataframe

            if fix_pollutants:
                #clear hap emis upload area
                file_path = ''

            #if no, remove them from dataframe
            else:
                missing = list(missing_pollutants.values())
                remove = set(missing[0].split(', '))


                #remove them from data frame

                for p in remove:

                    hapemis_df = hapemis_df[hapemis_df.pollutant != str(p)]

                    #record upload in log
                    #add another essage to say the following pollutants were assigned a generic value...
                    self.log.append("Removed " + p + " from hap emissions file\n")


        else:
            #record upload in log
            hap_num = set(hapemis_df['fac_id'])
            self.log.append("Uploaded HAP emissions file for " + str(len(hap_num)) + " facilities\n")

        self.dataframe = hapemis_df
