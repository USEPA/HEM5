import csv
import os

import pandas as pd
from decimal import *

from com.sca.hem4.log.Logger import Logger
import traceback

from com.sca.hem4.upload.CensusChanges import CensusChanges
from com.sca.hem4.upload.CensusDF import CensusDF
from tkinter import messagebox
from com.sca.hem4.support.ElevHill import ElevHill
from datetime import datetime
from datetime import date


class CensusUpdater():

    def __init__(self, changeData, changeDataPath):

        self.changeset_df = changeData
        self.changeset_path = changeDataPath
        
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
        Function to Move, Delete, Zero, or Update a census block or Add a new block
        """

        #debug
        import pdb; pdb.set_trace() 
        
        try:
            
            # Separate the changeset DF into DFs of additions, changes, and elevhill
            additions_df = self.changeset_df[self.changeset_df['change'].str.upper() == 'ADD'].copy()
            elevhill_df = self.changeset_df[self.changeset_df['change'].str.upper() == 'ELEVHILL'].copy()
            changes_df = self.changeset_df[(self.changeset_df['change'].str.upper() == 'ZERO')
                                           | (self.changeset_df['change'].str.upper() == 'MOVE')
                                           | (self.changeset_df['change'].str.upper() == 'DELETE')]

            
            #----------- Changes ---------------------------------------------------
            # Iterrate over the changes DF and make all updates. Plus update status column.
            if len(changes_df) > 0:
                changesStatus = []
                for index,row in changes_df.iterrows():
    
                    blockid = row["blockid"]
                    operation = row["change"].strip().upper()
    
                    # find the row in the census data containing the block to be changed
                    census_row_df = self.census_df.loc[self.census_df['blockid'] == blockid]
                    if len(census_row_df) == 0:
                        Logger.logMessage("\nCould not find block " + blockid + " in the census file."
                                          + "\nChanges will not be made to that block.")
                        changesStatus.append('Warning. Block not found in Census')
                        continue
                    else:
                        census_row = census_row_df.iloc[0,:]
                        census_idx = census_row_df.index.values[0]
                        
                    if operation == "DELETE":
                        Logger.logMessage("\nDeleted block " + blockid)
                        self.census_df = self.census_df.drop(census_idx)
                        changesStatus.append('Successfully deleted')
                        continue
    
                    # Make sure moved lat/lon does not create a duplicate in the census
                    if operation == "MOVE":
                        match_found = ((self.census_df['lat'] == row['lat']) & 
                                       (self.census_df['lon'] == row['lon'])).any()
                        if match_found:
                            errmsg = ("\nThe moved lat/lon for block " + blockid +
                                      " is already in the Census data. Please move to a different lat/lon " +
                                      "and rerun this tool.")
                            Logger.logMessage(errmsg)
                            changesStatus.append('Warning. Block cannot be moved because it creates a duplicate lat/lon in the Census.')
                            continue
                        else:
                            changesStatus.append('Successfully moved')
                            
                    if operation == "ZERO":
                        changesStatus.append('Successfully zeroed')
                        
                    # Mutate for 'MOVE' and 'ZERO' operations
                    replaced = self.mutate(census_row, operation, row)
                    self.census_df.loc[census_idx] = replaced
                    
                changes_df['status'] = changesStatus


            #----------- Additions ---------------------------------------------------
            # Add user supplied blocks
            if len(additions_df) > 0:
                
                Logger.logMessage("\nAdding user receptors to the Census data...")
                
                # If necessary, fill Block ID column to 15 with trailing zeros
                # Also create the FIPs column
                additions_df.loc[:,"blockid"] = additions_df["blockid"].str.pad(width=15, fillchar="0", side="right")
                additions_df.loc[:,"fips"] = additions_df["blockid"].str[:5]
                                    
                additions_df, returnmsg = self.generateAdditions(additions_df)
                Logger.logMessage(returnmsg)

            
            #----------- ELEVHILL ---------------------------------------------------
            # If there are elevhill changes, then compute elevation and hill height of that block
            elevhillStatus = []
            if len(elevhill_df) > 0:
                Logger.logMessage("\nElevations and hill heights being computed for selected blocks...")
                for index,row in elevhill_df.iterrows():
    
                    update_block = row["blockid"]
                    update_lat = row["lat"]
                    update_lon = row["lon"]
                    
                    # Find the row in the census data containing the block to be updated.
                    # Change file blockid and lat/lon must match row in the census file.
                    census_row_df = self.census_df.loc[(self.census_df['blockid'] == update_block)
                                                       & (self.census_df['lat'] == update_lat)
                                                       & (self.census_df['lon'] == update_lon)]
                    if len(census_row_df) == 0:
                        Logger.logMessage("\nCould not find block " + update_block + " in the census file."
                                          + "\nElevation and hill height will not be computed for that block.")
                        elevhillStatus.append('Warning. Block not found in Census. Elevation/hill height not computed.')
                        continue
                    else:
                        census_row = census_row_df.iloc[0,:]
                        census_idx = census_row_df.index.values[0]
                                                
                        # Get elevation for this lat/lon
                        # Note: getElev returns a list; only need one value
                        try:
                            block_elev = ElevHill.getElev([(update_lon, update_lat)])[0]
                            Logger.logMessage("\nElevation computed for block " + update_block)
                        except BaseException as ex:
                            if str(ex) == "USGS elevation server unavailable":
                                Logger.logMessage("\nUSGS elevation server is unavailable to compute elevation for block id " + update_block)
                                elevhillStatus.append('Warning. Skipped because USGS server unavailable for elevation')
                            continue
                        
                        # Get hill height for this lat/lon
                        try:
                            block_hill = ElevHill.getHill_onerec(update_lon, update_lat, block_elev)
                            Logger.logMessage("\nHill height computed for block " + update_block)
                        except BaseException as ex:
                            if str(ex) == "USGS elevation server unavailable":
                                Logger.logMessage("\nUSGS elevation server is unavailable to compute hill height for block id " + update_block)
                                elevhillStatus.append('Warning. Skipped because USGS server unavailable for hill height')
                            continue
                            
                        # Update the elevation and hill height in the census DF
                        # and update the elev/hill values in elevhill_df
                        self.census_df.loc[census_idx, 'elev'] = block_elev
                        self.census_df.loc[census_idx, 'hill'] = block_hill
                        elevhill_df.loc[index, 'elev'] = block_elev
                        elevhill_df.loc[index, 'hill'] = block_hill
                        elevhillStatus.append('Successfully computed elevation and hill height.')

                Logger.logMessage("\nFinished computing elevations and hill heights for selected blocks.")
                elevhill_df['status'] = elevhillStatus


            #----------- Complete set of changes ---------------------------------------------------
            # Create resulting changes DF from the 3 specific change DFs. This will include status.
            dataframes_to_concat = [changes_df, additions_df, elevhill_df]                    
            resultChanges_df = pd.concat([df for df in dataframes_to_concat if not df.empty])

            # Remove from resultChanges_df those rows where "Warning" appears in the status column.
            # This will result in a DF of successfull changes and this will be written
            # to the Census Log.
            mask = resultChanges_df['status'].str.contains('Warning', regex=False)
            success_changes = resultChanges_df[~mask]

            # Write to the Census Log if there are successful changes
            if not success_changes.empty:
                self.writeCensusLog(success_changes)

            # Write updated change file back to the folder where the change file originated.
            # This updated change file includes the status for all changes.
            self.writeChangeFile(resultChanges_df, self.changeset_path)
            
            # Write updated Census file
            self.writeCensusFile(self.census_df)
                        
            Logger.logMessage("\nFinished making census changes.")

            return

        except BaseException as e:
            fullStackInfo = traceback.format_exc()
            Logger.logMessage("Error running the Census Updater: " + fullStackInfo)
            return


    def generateAdditions(self, additions):
        """
        Function to add receptors to the census file.
        """
        
        block_adds = additions.copy()
        
        try:
            
            # Create empty DF that will hold the additions that will actually be added
            real_adds = pd.DataFrame(columns = block_adds.columns)
            
            # Iterate over the additions and make sure they can be added.
            status = []
            for index,row in block_adds.iterrows():
                
                row_to_add = row.copy(deep=True)
                
                dup_latlon = ((self.census_df['lat'] == row['lat']) & 
                               (self.census_df['lon'] == row['lon'])).any()
                if dup_latlon:
                    status.append('Warning. Skipped because the lat/lon is the duplicate of one already in the Census data.')
                    Logger.logMessage("\nThe lat/lon for user receptor " + row['blockid'] + " is already in the Census data " +
                                      "so the receptor will not be added.")
                    continue
                
                dup_blockid = (self.census_df['blockid'] == row['blockid']).any()
                if dup_blockid:
                    status.append('Warning. Skipped because the block id is the duplicate of one already in the Census data.')
                    Logger.logMessage("\nUser receptor id " + row['blockid'] + " is already in the Census data " +
                                      "so the receptor will not be added.")
                    continue
                
                # If this addition needs elevation, then compute it
                if pd.isnull(row['elev']):
                    try:
                        block_elev = ElevHill.getElev([(row['lon'], row['lat'])])[0]
                        row_to_add['elev'] = block_elev
                        block_adds.at[index,'elev'] = block_elev
                        Logger.logMessage("\nElevation computed for user provided receptor " + row['blockid'])
                    except BaseException as ex:
                        if str(ex) == "USGS elevation server unavailable":
                            Logger.logMessage("\nUSGS elevation server is unavailable to compute elevation for user receptor " + row['blockid']
                                              + "\nThis user receptor will not be added. You can manually add the elevation and rerun this tool.")
                            status.append('Warning. Skipped because USGS server unavailable for elevation')
                        continue
                else:
                    block_elev = row['elev']

                # If this addition needs hill height, then compute it
                if pd.isnull(row['hill']):
                    try:
                        block_hill = ElevHill.getHill_onerec(row['lon'], row['lat'], block_elev)
                        row_to_add['hill'] = block_hill
                        block_adds.at[index,'hill'] = block_hill
                        Logger.logMessage("\nHill height computed for user provided receptor " + row['blockid'])
                    except BaseException as ex:
                        if str(ex) == "USGS elevation server unavailable":
                            Logger.logMessage("\nUSGS elevation server is unavailable to compute hill height for user receptor " + row['blockid']
                                              + "\nThis user receptor will not be added. You can manually add the hill height and rerun this tool.")
                            status.append('Warning. Skipped because USGS server unavailable for hill height')
                        continue
                                    
                # This receptor is fine to add
                real_adds = pd.concat([real_adds, pd.DataFrame([row_to_add])], ignore_index=True)
                status.append('Successfully added')
                Logger.logMessage("\nUser receptor " + row['blockid'] + " was successfully added.")

            # Append all acceptable additions to the census DF
            # First drop come columns not needed by the census file
            real_adds.drop(['change', 'facid', 'category'], axis=1, inplace=True)

            self.census_df = pd.concat([self.census_df, real_adds], ignore_index=True)
            self.census_df = self.census_df.sort_values(by=['fips', 'blockid'])
            
            block_adds['status'] = status

            msg = "Finished processing user receptors."
            return block_adds, msg               

        except BaseException as e:
            
            fullStackInfo = traceback.format_exc()
            msg = "Error adding user receptors to the Census file: " + fullStackInfo
            return status, msg
        

    def writeCensusFile(self, census_df):
        """
        Write out the US census df to a new CSV file. Take note that all data
        was read in as dtype String and is maintained that way to preserve the
        format of the original data.
        """
        
        # Rename the original census to "-old-date".
        today_date = date.today().strftime("%Y-%m-%d")
        updatedFilepath = self.censusFilepath.replace(".csv", "-old-"+today_date+".csv") 
        # keep adding "-old-date(count)" until file does not exist
        version = 2
        while os.path.exists(updatedFilepath):
            updatedFilepath = updatedFilepath.replace(".csv", "-old-"+today_date+"("+str(version)+").csv")
            version+=1

        os.rename(self.censusFilepath, updatedFilepath)
        
        Logger.logMessage("\nWriting updates to the Census file...")
        
        # Put quotation marks around FIPs and Block ID columns for csv compatability
        census_df.update('"' + census_df[['fips','blockid']] + '"')
        headerlist = ['"fips"','"blockid"','"population"','"lat"','"lon"','"elev"',
                      '"hill"']
        census_df.to_csv(self.censusFilepath, header=headerlist, mode="w", index=False, 
                         chunksize=1000, quoting=csv.QUOTE_NONE, quotechar='"')
        Logger.logMessage("\nFinished writing updates to the census file. The original census file " +
                          "was maintained and is located in the census folder with a filename of:\n"
                          + updatedFilepath)


    def writeCensusLog(self, changes_df):
        """
        Write the census changes that succeeded to the Census Log file. It the log file
        does not exist, create it and write.

        Parameters
        ----------
        changes_df - Dataframe of user changes with a status indicator column.

        Returns
        -------
        None.

        """

        # Remove the fips and status columns
        changes_df.drop(['fips','status'], axis=1, inplace=True)
        
        changes_df['date_time'] = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

        # Insert blank column to separate date/time from original columns
        changes_df.insert(loc=9, column='', value='')
        
        log_file = os.path.join('census', 'User-Census-Change.xlsx')
        
        if os.path.exists(log_file):
            # If the file exists, append the data
            # 'a' mode for append, 'overlay' for if_sheet_exists to write on top
            with pd.ExcelWriter(log_file, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                # Read the existing data to determine the startrow for appending
                existing_df = pd.read_excel(log_file)
                startrow = len(existing_df) + 1  # Start writing after the last row of existing data
                changes_df.to_excel(writer, startrow=startrow, index=False, header=False)
            Logger.logMessage('\nAppended changes to the "User-Census-Change.xlsx" file.')
        else:
            # If the file does not exist, create a new one
            with pd.ExcelWriter(log_file, engine='xlsxwriter') as writer:
                changes_df.to_excel(writer, index=False)
            Logger.logMessage('\nCreated the "User-Census-Change.xlsx" file and added the changes.')
        return
                

    def writeChangeFile(self, allchanges_df, changes_path):
        """
        Write the census changes back to the folder where the change file originated. 
        This new change file is the same as the one chosen by the user but includes a status column
        showing the status of each requested change.

        Parameters
        ----------
        allchanges_df - Dataframe of user changes with a status indicator column.
        changes_path  - Pathname to the change file chosen by the user.

        Returns
        -------
        None.

        """
        
        # Remove the fips column
        allchanges_df.drop('fips', axis=1, inplace=True)
        
        allchanges_df['date_time'] = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        
        # Insert blank column to separate status and date/time from original columns
        allchanges_df.insert(loc=9, column='', value='')
 
        today_date = date.today().strftime("%Y-%m-%d")            
        out_file = changes_path.replace(".xlsx", "-status-"+today_date+".xlsx")
        version = 2
        while os.path.exists(out_file):
            out_file = out_file.replace(".xlsx", "-status-"+today_date+"("+str(version)+").xlsx")
            version+=1
            
        # Write the file
        with pd.ExcelWriter(out_file, engine='xlsxwriter') as writer:
            allchanges_df.to_excel(writer, index=False)
        
        Logger.logMessage('\nWrote the census update "status" file.'
                          + '\nFull filename is: "' + out_file + '"')
            
        return

        
    def mutate(self, record, operation, row):
        if operation == 'MOVE':
            Logger.logMessage("\nMoved block " + record["blockid"] + " to [" + str(row['lat']) + "," + str(row['lon']) + "]")
            record['lat'] = row['lat']
            record['lon'] = row['lon']
        elif operation == 'ZERO':
            Logger.logMessage("\nZeroed population for block " + record["blockid"])
            record['population'] = '0'

        return record


    def lookForDupLatLon(self, df):
        # Look for duplicate lat/lons in the census dataframe                
        latlondups = df[df.duplicated(['lat', 'lon'])][['lat', 'lon']]
        if not latlondups.empty:
            return latlondups
        else:
            return None
 
        

