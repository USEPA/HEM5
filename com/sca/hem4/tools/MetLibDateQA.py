import os
import pandas as pd
import sys

"""
This class will check the surface year stored in the MetLib Excel file to ensure
it matches the year in the surface data file and the upper air file.
"""

metlib_file = r"C:\Git_HEM4\HEM4\resources\metlib_aermod.xlsx"
metdir = r"C:\Git_HEM4\HEM4\aermod\MetData"

class MetLibDateQA():

    def __init__(self, metlib_path):

        # Read metlib file
        self.metlib_df = pd.read_excel(metlib_path)
        

    def checkDate(self, metdir):
        
        # Iterrate over metlib and confirm surfyear matches the year in the surface and upper air files
        for index, row in self.metlib_df.iterrows():
            sfc_file = os.path.join(metdir, row['metfname'])
            pfl_file = os.path.join(metdir, row['metfname2'])
            sfc_year = row['surfyear']
            
            sfc_df = pd.read_csv(
                sfc_file,
                sep='\s+',
                header=None,
                skiprows=1,
                nrows=1,
                usecols=[0]
            )

            pfl_df = pd.read_csv(
                pfl_file,
                sep='\s+',
                header=None,
                skiprows=1,
                nrows=1,
                usecols=[0]
            )

            sfcfile_year = sfc_df.iloc[0, 0]
            pflfile_year = pfl_df.iloc[0, 0]

            if sfcfile_year != sfc_year % 100:
                print("Wrong year for surface file ", row['metfname'])
                sys.exit(0)
                
            if sfcfile_year != pflfile_year:
                print("Year in the surface file does not match year in upper air file ", row['metfname'])
                sys.exit(0)
                
            print("Date correct in file ", row['metfname'])

qa = MetLibDateQA(metlib_path=metlib_file)
qa.checkDate(metdir=metdir)

