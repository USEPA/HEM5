import csv
import os

import pandas as pd
from decimal import *

from com.sca.hem4.log.Logger import Logger
import traceback

from com.sca.hem4.upload.CensusChanges import CensusChanges
from com.sca.hem4.upload.CensusDF import CensusDF
from tkinter import messagebox


class CensusUpdater():

    def __init__(self, changeData):

        self.changeset_df = changeData
        
        # Get the Census data
        Logger.logMessage("Loading the Census data...")
        censusdf = CensusDF()
        self.censusFilepath = censusdf.censusPath
        self.census_df = censusdf.dataframe
        if self.census_df.empty:
            messagebox.showinfo("Census not uploaded", "The census file, census/Census2020.csv, was not uploaded. Please confirm that it exists.")            
            return

        
    def generateChanges(self):
        """
        Function to Move, Delete, or Zero a census block or Add a new block
        """

        try:
            
            # Separate the changeset DF into a DF of additions and a DF of changes
            additions_df = self.changeset_df[self.changeset_df['change'].str.upper() == 'ADD'].copy()
            changes_df = self.changeset_df[self.changeset_df['change'].str.upper() != 'ADD'].copy()
                        
            # Iterrate over the changes DF and make all updates
            if len(changes_df) > 0:
                for index,row in changes_df.iterrows():
    
                    blockid = row["blockid"]
                    operation = row["change"].strip().upper()
    
                    # find the row in the census data containing the block to be changed
                    census_row_df = self.census_df.loc[self.census_df['blockid'] == blockid]
                    if len(census_row_df) == 0:
                        Logger.logMessage("Could not find block " + blockid + " in the census file.")
                        continue
                    else:
                        census_row = census_row_df.iloc[0,:]
                        census_idx = census_row_df.index.values[0]
                        
                    if operation == "DELETE":
                        Logger.logMessage("Deleting block " + blockid)
                        self.census_df = self.census_df.drop(census_idx)
                        continue
    
                    # Mutate for 'MOVE' and 'ZERO' operations
                    replaced = self.mutate(census_row, operation, row)
                    self.census_df.loc[census_idx] = replaced
                
            # If there are additions, then incoporate them.
            if len(additions_df) > 0:
                
                additions_df.drop(['change', 'facid', 'category'], axis=1, inplace=True)
                
                # If necessary, fill Block ID column to 15 with trailing zeros
                # Also create the FIPs column
                additions_df.loc[:,"blockid"] = additions_df["blockid"].str.pad(width=15, fillchar="0", side="right")
                additions_df.loc[:,"fips"] = additions_df["blockid"].str[:5]
                returnmsg = self.generateAdditions(additions_df)
                if returnmsg is not None:
                    Logger.logMessage(returnmsg)
                    return
                
            # All updates are done. Make sure no duplicate lat/lons have been created.
            all_latlons = self.census_df[['lat', 'lon']]
            all_latlons = all_latlons.apply(pd.to_numeric)
            dups = self.lookForDupLatLon(all_latlons)
            if type(dups) is not type(None):
                dups = dups.astype(str)
                dupslist = dups.values.tolist()
                dups2print = '\n'.join(', '.join(sub) for sub in dupslist)
                errmsg = ("\nAfter the updates were applied, duplicate lat/lons " +
                                  "now occur in the updated census data. Please correct " +
                                  "the update file and rerun this tool. Duplicates lat/lons are: \n" +
                                  dups2print)
                Logger.logMessage(errmsg)
                return

            Logger.logMessage("\nFinished making census changes.")
            
            # Write updated file
            self.writeCensusFile(self.census_df)
            return

        except BaseException as e:
            fullStackInfo = traceback.format_exc()
            Logger.logMessage("Error running the Census Updater: " + fullStackInfo)
            return


    def generateAdditions(self, additions):
        """
        Function to add receptors to the census file.
        """
        
        try:            
            # Make sure Block IDs of the added receptors are not already present in the census data
            intersection = pd.merge(self.census_df, additions, how='inner', on=['blockid'])
            if not intersection.empty:
                dupslist = intersection['blockid'].values.tolist()
                dups2print = '\n'.join(dupslist)
                errmsg = ("\nAborting user receptor additions because some user supplied block IDs" +
                        " are already present in the census file. Duplicates Block IDs are: \n" +
                        dups2print)                
                return errmsg

            # Append all additions to the census DF
            self.census_df = pd.concat([self.census_df, additions], ignore_index=True)
            self.census_df = self.census_df.sort_values(by=['fips', 'blockid'])
            
            Logger.logMessage("Finished adding user receptors to the census file.")
            return None

        except BaseException as e:
            fullStackInfo = traceback.format_exc()
            Logger.logMessage("Error adding user receptors to the census file: " + fullStackInfo)
            return fullStackInfo

    def writeCensusFile(self, census_df):
        """
        Write out the US census df to a new CSV file. Take note that all data
        was read in as dtype String and is maintained that way to preserve the
        format of the original data.
        """
        
        updatedFilepath = self.censusFilepath.replace(".csv", "-updated.csv")
        
        Logger.logMessage("Writing updated Census file...")
        
        # Put quotation marks around FIPs and Block ID columns for csv compatability
        census_df.update('"' + census_df[['fips','blockid']] + '"')
        headerlist = ['"fips"','"blockid"','"population"','"lat"','"lon"','"elev"',
                      '"hill"']
        census_df.to_csv(updatedFilepath, header=headerlist, mode="w", index=False, 
                         chunksize=1000, quoting=csv.QUOTE_NONE, quotechar='"')
        Logger.logMessage("\nFinished writing the updated census file. The revised census file " +
                          "is located in the census folder and filename contains the extension '-updated'")


    def mutate(self, record, operation, row):
        if operation == 'MOVE':
            Logger.logMessage("Moving block " + record["blockid"] + " to [" + str(row['lat']) + "," + str(row['lon']) + "]")
            record['lat'] = row['lat']
            record['lon'] = row['lon']
        elif operation == 'ZERO':
            Logger.logMessage("Zeroing population for block " + record["blockid"])
            record['population'] = '0'

        return record


    def lookForDupLatLon(self, df):
        # Look for duplicate lat/lons in the census dataframe                
        latlondups = df[df.duplicated(['lat', 'lon'])][['lat', 'lon']]
        if not latlondups.empty:
            return latlondups
        else:
            return None
 
        

