import csv
import glob
import os

import pandas as pd
import polars as pl
from decimal import *
import numpy as np

from com.sca.hem4.log.Logger import Logger
import traceback


class CensusUpdater():

    def __init__(self):

        self.previousValue = None
        self.censusFilepath = os.path.join('census', 'Census2020.csv')


    def generateChanges(self, changesetFilepath):
        """
        Function to Move, Delete, or Zero a census block or Add a new block
        """

        try:

            self.census_df = self.readCensusFromPath(self.censusFilepath)
            self.changeset_df = self.readChangesFromPath(changesetFilepath)
            
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
                    Logger.LogMessage(returnmsg)
                    return
                
            # All updates are done. Make sure no duplicate lat/lons have been created.
            dups = self.lookForDupLatLon(self.census_df)
            if type(dups) is not type(None):
                dupslist = dups.values.tolist()
                dups2print = '\n'.join(', '.join(sub) for sub in dupslist)
                errmsg = ("\nAfter the updates were applied, duplicate lat/lons " +
                                  "now occur in the updated census data. Please correct " +
                                  "the update file and rerun this tool. Duplicates are: \n" +
                                  dups2print)
                Logger.logMessage(errmsg)
                return
            
            # Write updated file
            self.writeCensusFile(self.census_df)
            Logger.logMessage("Finished making census changes. Revised census file " +
                              "is located in the census folder and filename contains the extension '-updated'")
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
                dups2print = '\n'.join(', '.join(sub) for sub in dupslist)
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
                      '"hill"','"urban_pop"']
        census_df.to_csv(updatedFilepath, header=headerlist, mode="w", index=False, 
                         chunksize=1000, quoting=csv.QUOTE_NONE, quotechar='"')


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
 
        
    def readChangesFromPath(self, filepath):
        colnames = ["change", "facid", "category", "blockid", "lat", "lon", 
                    "population", "elev", "hill", "urban_pop"]
        dtypes = {"change":str, "facid":str, "category":str, "blockid":str, 
                  "lat":np.float64, "lon":np.float64, "population":"Int64", 
                  "elev":np.float64, "hill":np.float64, "urban_pop":"Int64"}

        with open(filepath, "rb") as f:
            df = pd.read_excel(f, skiprows=0, names=colnames, dtype=dtypes, 
                               na_values=[''], keep_default_na=False)
            df[['population', 'elev', 'hill', 'urban_pop']] = \
                      df[['population', 'elev', 'hill', 'urban_pop']].fillna(value=0)
            return df

    # def readAdditionsFromPath(self, filepath):
    #     colnames = ["change", "facid", "category", "blockid", "lat", "lon", 
    #                 "population", "elev", "hill", "urban_pop"]
    #     with open(filepath, "rb") as f:
    #         df = pd.read_excel(f, skiprows=0, names=colnames, dtype=str, na_values=[''], keep_default_na=False)
    #         return df

    def readCensusFromPath(self, filepath):
        # datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'population':pl.Int64, 
        #                   'lat':pl.Float64, 'lon':pl.Float64, 'elev':pl.Float64, 
        #                   'hill':pl.Float64, 'urban_pop':pl.Int64}
        datatypes = {'fips':pl.Utf8, 'blockid':pl.Utf8, 'population':pl.Utf8, 
                          'lat':pl.Utf8, 'lon':pl.Utf8, 'elev':pl.Utf8, 
                          'hill':pl.Utf8, 'urban_pop':pl.Utf8}
        with open(filepath, "rb") as f:
            plf = pl.scan_csv(f.name, has_header=True, dtypes=datatypes, null_values=[''])
            df = plf.collect().to_pandas()
            return df


