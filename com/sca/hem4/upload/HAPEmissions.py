from upload.InputFile import InputFile
from tkinter import messagebox
import os
from datetime import datetime
from model.Model import *

emis_tpy = 'emis_tpy';
part_frac = 'part_frac';
particle = 'particle';
gas = 'gas';

class HAPEmissions(InputFile):

    def __init__(self, path, haplib):
        self.haplib = haplib

        InputFile.__init__(self, path)

    def createDataframe(self):

        # Specify dtypes for all fields
        self.numericColumns = [emis_tpy,part_frac]
        self.strColumns = [fac_id,source_id,pollutant]

        #HAP EMISSIONS excel to dataframe
        # HEADER------------------------
        # FacilityID|SourceID|HEM3chem|SumEmissionTPY|FractionParticulate
        hapemis_df = self.readFromPath((fac_id,source_id,pollutant,emis_tpy,part_frac))

        #fill Nan with 0
        hapemis_df.fillna(0)

        #turn part_frac into a decimal
        hapemis_df[part_frac] = hapemis_df[part_frac] / 100

        #create additional columns, one for particle mass and the other for gas/vapor mass...
        hapemis_df[particle] = hapemis_df[emis_tpy] * hapemis_df[part_frac]
        hapemis_df[gas] = hapemis_df[emis_tpy] * (1 - hapemis_df[part_frac])

        #get list of pollutants from dose library
        master_list = list(self.haplib.dataframe[pollutant])
        lower = [x.lower() for x in master_list]

        user_haps = set(hapemis_df[pollutant])
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
                #clear hap emis upload area, how to do this from separate thread...
                file_path = ''

            #if no, remove them from dataframe
            elif fix_pollutants is False:
                missing = missing_pollutants
                remove = set(missing)
                print(remove)


                #remove them from data frame
                # to seperate log file the non-modeled HAP Emissions
                fileDir = os.path.dirname(os.path.realpath('__file__'))
                filename = os.path.join(fileDir, "output\HAP_ignored.log")
                logfile = open(filename, 'w')

                logfile.write(str(datetime.now()) + ":\n")

                for p in remove:

                    hapemis_df = hapemis_df[hapemis_df[pollutant] != str(p)]

                    #record upload in log
                    #add another essage to say the following pollutants were assigned a generic value...
                    self.log.append("Removed " + p + " from hap emissions file\n")



                    #get row so we can write facility and other info
                    ignored = hapemis_df[hapemis_df[pollutant] == p]

                    logfile.write("Removed: " + str(ignored))


                logfile.close()



        else:
            #record upload in log
            hap_num = set(hapemis_df[fac_id])
            self.log.append("Uploaded HAP emissions file for " + str(len(hap_num)) +
                            " facilities\n")

        self.dataframe = hapemis_df