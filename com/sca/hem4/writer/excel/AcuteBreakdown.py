import os, fnmatch
import pandas as pd
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.upload.HAPEmissions import *
from com.sca.hem4.upload.FacilityList import *
from com.sca.hem4.upload.DoseResponse import *
from com.sca.hem4.upload.UserReceptors import *
from com.sca.hem4.model.Model import *
from com.sca.hem4.support.UTM import *
from com.sca.hem4.FacilityPrep import *
from com.sca.hem4.writer.csv.AllInnerReceptors import *

notes = 'notes';
aconc_pop = 'aconc_pop';
aconc_all = 'aconc_all';
pop_interp = 'pop_interp';
all_interp = 'all_interp';


class AcuteBreakdown(ExcelWriter):
    """
    Provides the contribution of each emission source to the receptors (both populated and unpopulated) of maximum acute
    impact for each pollutant.
    """

    def __init__(self, targetDir, facilityId, model, plot_df, achempop_df, achemunpop_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_acute_bkdn.xlsx")
        self.achempop_df = achempop_df
        self.achemunpop_df = achemunpop_df

    def getHeader(self):
        return ['Pollutant', 'Source ID', 'Emission type', 'Max conc at populated receptor (µg/m3)', 
                'Is max populated receptor interpolated? (Y/N)', 'Max conc at any receptor (µg/m3)',
                'Is max conc at any receptor interpolated? (Y/N)']

    def generateOutputs(self):

        # First get breakdown info of max acute at a populated receptor
        for index, row in self.achempop_df.iterrows():
            if row[notes] == 'Discrete':
                # max acute is at an inner block
                flag1 = 'N'
                popinfo_df = self.model.all_inner_receptors_df[
                        (self.model.all_inner_receptors_df[lon] == row[lon]) & 
                        (self.model.all_inner_receptors_df[lat] == row[lat])][[pollutant,
                                                            source_id, ems_type, aconc]]
            else:
                # max acute is at an outer block
                flag1 = 'Y'
                popinfo_df = self.model.all_outer_receptors_df[
                        (self.model.all_outer_receptors_df[lon] == row[lon]) & 
                        (self.model.all_outer_receptors_df[lat] == row[lat])][[pollutant,
                                                            source_id, ems_type, aconc]]
            popinfo_df.rename(columns={aconc:aconc_pop}, inplace=True)
                            
        # Next get breakdown info of max acute at any receptor
        for index, row in self.achemunpop_df.iterrows():
            if row[notes] == 'Discrete':
                # max acute is at an inner block
                flag2 = 'N'
                unpopinfo_df = self.model.all_inner_receptors_df[
                        (self.model.all_inner_receptors_df[lon] == row[lon]) & 
                        (self.model.all_inner_receptors_df[lat] == row[lat])][[pollutant,
                                                            source_id, ems_type, aconc]]
            elif row[notes] == 'Interpolated':
                # max acute is at an outer block
                flag2 = 'Y'
                unpopinfo_df = self.model.all_outer_receptors_df[
                        (self.model.all_outer_receptors_df[lon] == row[lon]) & 
                        (self.model.all_outer_receptors_df[lat] == row[lat])][[pollutant,
                                                            source_id, ems_type, aconc]]
            else:
                # max acute is at a polar receptor
                flag2 = 'N'
                unpopinfo_df = self.model.all_polar_receptors_df[
                        (self.model.all_polar_receptors_df[lon] == row[lon]) & 
                        (self.model.all_polar_receptors_df[lat] == row[lat])][[pollutant,
                                                            source_id, ems_type, aconc]]
            unpopinfo_df.rename(columns={aconc:aconc_all}, inplace=True)
        
        # Combine pop and all breakdown dataframes into one
        temp_df = pd.merge(popinfo_df, unpopinfo_df, how='inner', on=[pollutant, source_id])
        temp_df[pop_interp] = flag1
        temp_df[all_interp] = flag2
        
        # Reorder columns for output purpose, reset the index, and sort by pollutant and source_id
        cols = [pollutant, source_id, ems_type, aconc_pop, pop_interp, aconc_all, all_interp]
        abkdn_df = temp_df.reindex(columns = cols)
        abkdn_df.reset_index(drop=True, inplace=True)
        abkdn_df.sort_values(by=[pollutant, source_id], inplace=True)
        
        
        # Return results
        self.dataframe = abkdn_df
        self.data = self.dataframe.values
        yield self.dataframe