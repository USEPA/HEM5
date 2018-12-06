import os
import re

from math import log10

from json_census_blocks import population
from log import Logger
from upload.DoseResponse import ure
from writer.csv.AllInnerReceptors import ems_type
from writer.excel.ExcelWriter import ExcelWriter
from model.Model import *

inc = 'inc';
inc_rnd = 'inc_rnd';

class Incidence(ExcelWriter):
    """
    Provides the incidence value for the total of all sources and all modeled pollutants as well
    as the incidence value for each source and each pollutant.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_incidence.xlsx")

        # Local cache for URE values
        self.riskCache = {}

    def calculateOutputs(self):
        """
        Do something with the model and plot data, setting self.headers and self.data in the process.
        """
        self.headers = ['Source ID', 'Pollutant', 'Emission type', 'Incidence', 'Incidence rounded']

        allinner_df = self.model.all_inner_receptors_df.copy()
        allouter_df = self.model.all_outer_receptors_df.copy()


        # compute incidence for each Inner rececptor row and then sum incidence by source_id and pollutant
        allinner_df[inc] = allinner_df.apply(lambda row: self.calculateRisk(row[pollutant],
                   row[conc]) * row[population]/70, axis=1)
        inner_inc = allinner_df.groupby([source_id, pollutant, ems_type], as_index=False)[[inc]].sum()

        # compute incidence for each Outer rececptor row and then sum incidence by source_id and pollutant
        allouter_df['inc'] = allouter_df.apply(lambda row: self.calculateRisk(row[pollutant],
                   row[conc]) * row[population]/70, axis=1)
        outer_inc = allouter_df.groupby([source_id, pollutant, ems_type], as_index=False)[[inc]].sum()

        # append inner_inc and outer_inc, and re-sum by source_id and pollutant
        all_inc = inner_inc.append(outer_inc, ignore_index=True).groupby(
                [source_id, pollutant, ems_type], as_index=False)[[inc]].sum()
        
        # sum incidence by pollutant
        poll_inc = all_inc.groupby([pollutant, ems_type], as_index=False)[[inc]].sum()
        poll_inc[source_id] = "Total"
         
        # sum incidence by source id
        sourceid_inc = all_inc.groupby([source_id, ems_type], as_index=False)[[inc]].sum()
        sourceid_inc[pollutant] = "All modeled pollutants"

        # sum incidence by emission type
        emistype_inc = all_inc.groupby([ems_type], as_index=False)[[inc]].sum()
        emistype_inc[source_id] = "Total"
        emistype_inc[pollutant] = "All modeled pollutants"
        
        # combine all, poll, sourceid, and emistype incidence dfs into one and store in data
        combined_inc = emistype_inc.append([all_inc, poll_inc, sourceid_inc], ignore_index=True)
        combined_inc = combined_inc[[source_id, pollutant, ems_type, inc]]
        
        # compute a rounded incidence value
        combined_inc[inc_rnd] = combined_inc[inc].apply(self.roundIncidence)
        
        # Put final df into array
        self.data = combined_inc.values
 
    
    def roundIncidence(self, inc):
        # Round incidence to two significant figures
        if inc > 0:
            exp = int(log10(inc)+99)-99
            rndinc = round(inc, 1 - exp)
        else:
            rndinc = 0
        return rndinc
    
       
    def calculateRisk(self, pollutant_name, conc):
        URE = None

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant_name) + '$'

        # Since it's relatively expensive to get this from the dose response library, cache them locally.
        if pollutant_name in self.riskCache:
            URE = self.riskCache[pollutant_name][ure]
        else:
            row = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                msg = 'Could not find pollutant ' + pollutant_name + ' in the haplib!'
                Logger.logMessage(msg)
                Logger.log(msg, self.model.haplib.dataframe, False)
                URE = 0
            else:
                URE = row.iloc[0][ure]

            self.riskCache[pollutant_name] = {ure : URE}


        mir = conc * URE
        return mir
        