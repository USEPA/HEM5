from upload.InputFile import InputFile
from tkinter import messagebox
import os
from datetime import datetime


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



        self.log = []
        #if there are any missing pollutants
        if len(missing_pollutants) > 0:
            fix_pollutants = messagebox.askyesno("Missing Pollutants in Dose "+
                                                 "Response Library", "The "+ 
                                                 "following pollutants were "+
                                                 "not found in HEM4's Dose "+ 
                                                 "Response Library: " + 
                                                 ', '.join(missing_pollutants) + 
                                                 ".\n Would you like to amend "+
                                                 "your HAP EMissions file?"+
                                                 "(they will be removed "+
                                                 "otherwise). ")
            #if yes, clear box and empty dataframe

            if fix_pollutants is True:
                #clear hap emis upload area
                file_path = ''

            #if no, remove them from dataframe
            elif fix_pollutants is False:
                missing = list(missing_pollutants.values())
                remove = set(missing[0].split(', '))


                #remove them from data frame
                # to seperate log file the non-modeled HAP Emissions
                fileDir = os.path.dirname(os.path.realpath('__file__'))
                filename = os.path.join(fileDir, 'output/HAP_ignored_'+str(datetime.now())+'.log')
                logfile = open(filename, 'w')

                for p in remove:

                    hapemis_df = hapemis_df[hapemis_df.pollutant != str(p)]

                    #record upload in log
                    #add another essage to say the following pollutants were assigned a generic value...
                    self.log.append("Removed " + p + " from hap emissions file\n")
                    
                    
                    
                    #get row so we can write facility and other info
                    ignored = hapemis_df[hapemis_df.pollutant == p]
                    
                    logfile.append(ignored)
                    
                
                logfile.close()
                    


        else:
            #record upload in log
            hap_num = set(hapemis_df['fac_id'])
            self.log.append("Uploaded HAP emissions file for " + str(len(hap_num)) +
                            " facilities\n")

        self.dataframe = hapemis_df
