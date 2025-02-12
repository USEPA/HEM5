import os
import csv

from decimal import ROUND_HALF_UP, Decimal, getcontext

from math import *
from pandas import isna

from com.sca.hem4.CensusBlocks import fips
from com.sca.hem4.log import Logger

class DataModel():

    def __init__(self, missing_block_path, mir_rec_df, acs_df, levels_df, toshis, radius, facility):

        self.toshis = toshis
        self.radius = radius
        self.facility = facility
        self.cancer_bins = None
        self.toshi_bins = None
        self.max_risk = {}
        self.missing_block_groups = []
        self.missing_block_group_path = missing_block_path

        self.risk_column_map = {
            'Resp':'hi_resp', 'Live':'hi_live','Neur':'hi_neur', 'Deve':'hi_deve', 'Repr':'hi_repr',
            'Kidn':'hi_kidn', 'Ocul':'hi_ocul','Endo':'hi_endo', 'Hema':'hi_hema', 'Immu':'hi_immu','Skel':'hi_skel',
            'Sple':'hi_sple', 'Thyr':'hi_thyr', 'Whol':'hi_whol'
        }

        self.hazards_df = mir_rec_df

        # Prepare the county and state info...
        Logger.logMessage("Indexing county and state information...")
        
        # Start by filtering out county records...we only want block groups with the 5 digit county codes.
        county_list = self.hazards_df[fips].unique()
        self.county_df = acs_df[acs_df["STCNTRBG"].str[:5].isin(county_list)]

        # Now get all block groups starting with the 2 digit state codes.
        state_list = list(set([county[:2] for county in county_list]))
        self.state_df = acs_df[acs_df["STCNTRBG"].str[:2].isin(state_list)]
        
        self.acs_df = acs_df
        self.acs_df.index = self.acs_df['STCNTRBG']
        self.acs_dict = self.acs_df.to_dict(orient='index')
        
        self.levels_df = levels_df
        self.levels_df.index = self.levels_df['TCT']
        self.levels_dict = self.levels_df.to_dict(orient='index')

        self.create_national_bin()
        self.create_state_bin()
        self.create_county_bin()
        self.create_bins()
        self.write_missing_block_groups()

    def create_national_bin(self):
        # Create national bin and tabulate population weighted demographic stats for each sub group.
        self.national_bin = [ [0]*18 for _ in range(2) ]
        self.acs_df.apply(lambda row: self.tabulate_national_data(row), axis=1)

        # Calculate population percentages by dividing population for each sub group
        for index in range(1, 18):
            self.national_bin[1][index] = self.national_bin[1][index] / (100 * self.national_bin[0][index])
            # if index == 11:
            #     self.national_bin[1][index] = self.national_bin[1][index] / (100 * self.national_bin[0][0])
            # else:
            #     self.national_bin[1][index] = self.national_bin[1][index] / (100 * self.national_bin[0][index])

        # Calculate population counts
        for index in range(1, 18):
            self.national_bin[0][index] = self.national_bin[0][index] * self.national_bin[1][index]
        
        self.national_bin[1][0] = ""


    def create_state_bin(self):
        # Create state bin and tabulate population weighted demographic stats for each sub group.
        self.state_bin = [ [0]*18 for _ in range(2) ]
        self.state_df.apply(lambda row: self.tabulate_state_data(row), axis=1)
        
        # Calculate state population percentages by dividing population for each sub group
        for index in range(1, 18):
            self.state_bin[1][index] = self.state_bin[1][index] / (100 * self.state_bin[0][index])
        
        # Calculate state population counts
        for index in range(1, 18):
            self.state_bin[0][index] = self.state_bin[0][index] * self.state_bin[1][index]

        self.state_bin[1][0] = ""

    def create_county_bin(self):
        # Create county bin and tabulate population weighted demographic stats for each sub group.
        self.county_bin = [ [0]*18 for _ in range(2) ]
        self.county_df.apply(lambda row: self.tabulate_county_data(row), axis=1)

        # Calculate county population percentages by dividing population for each sub group
        for index in range(1, 18):
            self.county_bin[1][index] = self.county_bin[1][index] / (100 * self.county_bin[0][index])

        # Calculate county population counts
        for index in range(1, 18):
            self.county_bin[0][index] = self.county_bin[0][index] * self.county_bin[1][index]

        self.county_bin[1][0] = ""
        
    def create_bins(self):
        # Create cancer bins and tabulate the risk based on the mir column. Note that there are 18 sub groups (columns)
        # and 13 rows, which correspond to 11 risk bins + total + average.
        self.cancer_bins = [ [0]*18 for _ in range(13) ]
        self.max_risk['mir'] = 0

        self.total_missing_pop = 0

        Logger.logMessage("Tabulating data...")
        self.hazards_df.apply(lambda row: self.tabulate_mir_data(row), axis=1)
        
        # Calculate averages by dividing population for each sub group
        for index in range(18):
            if self.cancer_bins[11][index] == 0:
                self.cancer_bins[12][index] = 0
            else:
                self.cancer_bins[12][index] /= self.cancer_bins[11][index]

        Logger.logMessage("Done with MIR tabulation.")

        # Next create toshi bins and tabulate risk for each requested toshi. Note that there are 18 sub groups (columns)
        # and 13 rows, which correspond to 11 risk bins + total + average.
        if len(self.toshis.items()) > 0:
            self.toshi_bins = {}
            for key,value in self.toshis.items():
                self.max_risk[key] = 0
                self.toshi_bins[key] = [ [0]*18 for _ in range(13) ]

            Logger.logMessage("Tabulating toshi data...")
            self.hazards_df.apply(lambda row: self.tabulate_toshi_data(row), axis=1)

            # Calculate averages by dividing population for each sub group
            for key, bin in self.toshi_bins.items():
                for index in range(18):
                    if bin[11][index] == 0:
                        bin[12][index] = 0
                    else:
                        bin[12][index] /= bin[11][index]

            Logger.logMessage("Done with toshi tabulation.")

    def tabulate_national_data(self, row):

        population = row['TOTALPOP']
        pct_minority = row['PCT_MINORITY']
        pct_white = row['PCT_WHITE']
        pct_black = row['PCT_BLACK']
        pct_amerind = row['PCT_AMIND']
        pct_asian = row['PCT_ASIAN']
        pct_other = row['PCT_OTHER_RACE']
        pct_hisp = row['PCT_HISP']
        pct_age_lt18 = row['PCT_AGE_LT18']
        pct_age_gt64 = row['PCT_AGE_GT64']
        edu_universe = row['EDU_UNIVERSE']
        pct_edu_lths = row['PCT_EDU_LTHS']
        pov_universe = row['POV_UNIVERSE']
        pct_lowinc = row['PCT_LOWINC']
        pct_lingiso = row['PCT_LINGISO']
        pct_pov = row['PCT_POV']
        pct_dis = row['PCT_DIS']
        dis_universe = row['DIS_UNIVERSE']

        self.national_bin[0][0] += population
        if not isna(pct_minority):
            self.national_bin[1][1] += pct_white * population
            self.national_bin[0][1] += population
        if not isna(pct_black):
            self.national_bin[1][2] += pct_black * population
            self.national_bin[0][2] += population
        if not isna((pct_amerind)):
            self.national_bin[1][3] += pct_amerind * population
            self.national_bin[0][3] += population
        if not isna((pct_asian)):
            self.national_bin[1][4] += pct_asian * population
            self.national_bin[0][4] += population
        if not isna(pct_other):
            self.national_bin[1][5] += pct_other * population
            self.national_bin[0][5] += population
        if not isna(pct_hisp):
            self.national_bin[1][6] += pct_hisp * population
            self.national_bin[0][6] += population
        if not isna(pct_age_lt18):
            self.national_bin[1][7] += pct_age_lt18 * population
            self.national_bin[0][7] += population
        if not isna(pct_age_gt64):
            self.national_bin[1][9] += pct_age_gt64 * population
            self.national_bin[0][9] += population
        if not isna(pct_age_lt18) and not isna(pct_age_gt64):
            self.national_bin[1][8] += (100 - pct_age_gt64 - pct_age_lt18) * population
            self.national_bin[0][8] += population
        if not isna(edu_universe):
            self.national_bin[1][10] += edu_universe * 100
            self.national_bin[0][10] += population
        if not isna(pov_universe):
            self.national_bin[1][16] += pov_universe * 100
            self.national_bin[0][16] += population
        if not isna(edu_universe) and not isna(pct_edu_lths):
            self.national_bin[1][11] += pct_edu_lths * edu_universe
            self.national_bin[0][11] += edu_universe
        if not isna(pov_universe):
            self.national_bin[1][12] += pct_pov * pov_universe
            self.national_bin[0][12] += population
        if not isna(pov_universe) and not isna(pct_lowinc):
            self.national_bin[1][13] += pct_lowinc * pov_universe
            self.national_bin[0][13] += population
        if not isna(pct_lingiso):
            self.national_bin[1][14] += pct_lingiso * population
            self.national_bin[0][14] += population
        if not isna(pct_minority):
            self.national_bin[1][15] += pct_minority * population
            self.national_bin[0][15] += population
        if not isna(pct_dis) and not isna(dis_universe):
            self.national_bin[1][17] += pct_dis * dis_universe
            self.national_bin[0][17] += population

    def tabulate_state_data(self, row):

        population = row['TOTALPOP']
        pct_minority = row['PCT_MINORITY']
        pct_white = row['PCT_WHITE']
        pct_black = row['PCT_BLACK']
        pct_amerind = row['PCT_AMIND']
        pct_asian = row['PCT_ASIAN']
        pct_other = row['PCT_OTHER_RACE']
        pct_hisp = row['PCT_HISP']
        pct_age_lt18 = row['PCT_AGE_LT18']
        pct_age_gt64 = row['PCT_AGE_GT64']
        edu_universe = row['EDU_UNIVERSE']
        pct_edu_lths = row['PCT_EDU_LTHS']
        pov_universe = row['POV_UNIVERSE']
        pct_lowinc = row['PCT_LOWINC']
        pct_lingiso = row['PCT_LINGISO']
        pct_pov = row['PCT_POV']
        pct_dis = row['PCT_DIS']
        dis_universe = row['DIS_UNIVERSE']

        self.state_bin[0][0] += population
        if not isna(pct_minority):
            self.state_bin[1][1] += pct_white * population
            self.state_bin[0][1] += population
        if not isna(pct_black):
            self.state_bin[1][2] += pct_black * population
            self.state_bin[0][2] += population
        if not isna((pct_amerind)):
            self.state_bin[1][3] += pct_amerind * population
            self.state_bin[0][3] += population
        if not isna((pct_asian)):
            self.state_bin[1][4] += pct_asian * population
            self.state_bin[0][4] += population
        if not isna(pct_other):
            self.state_bin[1][5] += pct_other * population
            self.state_bin[0][5] += population
        if not isna(pct_hisp):
            self.state_bin[1][6] += pct_hisp * population
            self.state_bin[0][6] += population
        if not isna(pct_age_lt18):
            self.state_bin[1][7] += pct_age_lt18 * population
            self.state_bin[0][7] += population
        if not isna(pct_age_gt64):
            self.state_bin[1][9] += pct_age_gt64 * population
            self.state_bin[0][9] += population
        if not isna(pct_age_lt18) and not isna(pct_age_gt64):
            self.state_bin[1][8] += (100 - pct_age_gt64 - pct_age_lt18) * population
            self.state_bin[0][8] += population
        if not isna(edu_universe):
            self.state_bin[1][10] += edu_universe * 100
            self.state_bin[0][10] += population
        if not isna(pov_universe):
            self.state_bin[1][16] += pov_universe * 100
            self.state_bin[0][16] += population
        if not isna(edu_universe) and not isna(pct_edu_lths):
            self.state_bin[1][11] += pct_edu_lths * edu_universe
            self.state_bin[0][11] += edu_universe
        if not isna(pov_universe):
            self.state_bin[1][12] += pct_pov * pov_universe
            self.state_bin[0][12] += population
        if not isna(pov_universe) and not isna(pct_lowinc):
            self.state_bin[1][13] += pct_lowinc * pov_universe
            self.state_bin[0][13] += population
        if not isna(pct_lingiso):
            self.state_bin[1][14] += pct_lingiso * population
            self.state_bin[0][14] += population
        if not isna(pct_minority):
            self.state_bin[1][15] += pct_minority * population
            self.state_bin[0][15] += population
        if not isna(pct_dis) and not isna(dis_universe):
            self.state_bin[1][17] += pct_dis * dis_universe
            self.state_bin[0][17] += population

    def tabulate_county_data(self, row):

        population = row['TOTALPOP']
        pct_minority = row['PCT_MINORITY']
        pct_white = row['PCT_WHITE']
        pct_black = row['PCT_BLACK']
        pct_amerind = row['PCT_AMIND']
        pct_asian = row['PCT_ASIAN']
        pct_other = row['PCT_OTHER_RACE']
        pct_hisp = row['PCT_HISP']
        pct_age_lt18 = row['PCT_AGE_LT18']
        pct_age_gt64 = row['PCT_AGE_GT64']
        edu_universe = row['EDU_UNIVERSE']
        pct_edu_lths = row['PCT_EDU_LTHS']
        pov_universe = row['POV_UNIVERSE']
        pct_lowinc = row['PCT_LOWINC']
        pct_lingiso = row['PCT_LINGISO']
        pct_pov = row['PCT_POV']
        pct_dis = row['PCT_DIS']
        dis_universe = row['DIS_UNIVERSE']

        self.county_bin[0][0] += population
        if not isna(pct_minority):
            self.county_bin[1][1] += pct_white * population
            self.county_bin[0][1] += population
        if not isna(pct_black):
            self.county_bin[1][2] += pct_black * population
            self.county_bin[0][2] += population
        if not isna((pct_amerind)):
            self.county_bin[1][3] += pct_amerind * population
            self.county_bin[0][3] += population
        if not isna((pct_asian)):
            self.county_bin[1][4] += pct_asian * population
            self.county_bin[0][4] += population
        if not isna(pct_other):
            self.county_bin[1][5] += pct_other * population
            self.county_bin[0][5] += population
        if not isna(pct_hisp):
            self.county_bin[1][6] += pct_hisp * population
            self.county_bin[0][6] += population
        if not isna(pct_age_lt18):
            self.county_bin[1][7] += pct_age_lt18 * population
            self.county_bin[0][7] += population
        if not isna(pct_age_gt64):
            self.county_bin[1][9] += pct_age_gt64 * population
            self.county_bin[0][9] += population
        if not isna(pct_age_lt18) and not isna(pct_age_gt64):
            self.county_bin[1][8] += (100 - pct_age_gt64 - pct_age_lt18) * population
            self.county_bin[0][8] += population
        if not isna(edu_universe):
            self.county_bin[1][10] += edu_universe * 100
            self.county_bin[0][10] += population
        if not isna(pov_universe):
            self.county_bin[1][16] += pov_universe * 100
            self.county_bin[0][16] += population
        if not isna(edu_universe) and not isna(pct_edu_lths):
            self.county_bin[1][11] += pct_edu_lths * edu_universe
            self.county_bin[0][11] += edu_universe
        if not isna(pov_universe):
            self.county_bin[1][12] += pct_pov * pov_universe
            self.county_bin[0][12] += population
        if not isna(pov_universe) and not isna(pct_lowinc):
            self.county_bin[1][13] += pct_lowinc * pov_universe
            self.county_bin[0][13] += population
        if not isna(pct_lingiso):
            self.county_bin[1][14] += pct_lingiso * population
            self.county_bin[0][14] += population
        if not isna(pct_minority):
            self.county_bin[1][15] += pct_minority * population
            self.county_bin[0][15] += population
        if not isna(pct_dis) and not isna(dis_universe):
            self.county_bin[1][17] += pct_dis * dis_universe
            self.county_bin[0][17] += population
            
    def tabulate_toshi_data(self, row):

        # Identify the block group corresponding to this row.
        group_id = row['fips'] + row['block'][:7]

        # Get all demographic data for this row. If we don't have values we may need to fall back on tract/county
        # level data.
        block_group = self.acs_dict[group_id] if group_id in self.acs_dict else None
        population = row['population']
        
        total_pop = self.get_value(block_group, group_id, 'TOTALPOP', False)
        pct_minority = self.get_value(block_group, group_id, 'PCT_MINORITY')
        pct_white = self.get_value(block_group, group_id, 'PCT_WHITE')
        pct_black = self.get_value(block_group, group_id, 'PCT_BLACK')
        pct_amerind = self.get_value(block_group, group_id, 'PCT_AMIND')
        pct_asian = self.get_value(block_group, group_id, 'PCT_ASIAN')
        pct_other = self.get_value(block_group, group_id, 'PCT_OTHER_RACE')
        pct_hisp = self.get_value(block_group, group_id, 'PCT_HISP')
        pct_age_lt18 = self.get_value(block_group, group_id, 'PCT_AGE_LT18')
        pct_age_gt64 = self.get_value(block_group, group_id, 'PCT_AGE_GT64')
        edu_universe = self.get_value(block_group, group_id, 'EDU_UNIVERSE', False)
        pct_edu_lths = self.get_value(block_group, group_id, 'PCT_EDU_LTHS')
        pov_universe = self.get_value(block_group, group_id, 'POV_UNIVERSE', False)
        pct_2xpov = self.get_value(block_group, group_id, 'PCT_LOWINC')
        pct_lingiso = self.get_value(block_group, group_id, 'PCT_LINGISO')
        pct_pov = self.get_value(block_group, group_id, 'PCT_POV')
        pct_dis = self.get_value(block_group, group_id, 'PCT_DIS')
        dis_universe = self.get_value(block_group, group_id, 'DIS_UNIVERSE', False)

        if pct_white is None or pct_black is None or pct_amerind is None or pct_asian is None or pct_other is None or pct_hisp is None \
                or pct_age_lt18 is None \
                or pct_age_gt64 is None or pct_edu_lths is None \
                or pct_2xpov is None or pct_lingiso is None or pov_universe is None or edu_universe is None\
                or pct_minority is None or pct_pov is None or pct_dis is None or dis_universe is None:
            print("Unable to compile enough data to include this record: " + group_id)
            return

        pct_edu_universe = edu_universe / total_pop if total_pop > 0 else 0
        pct_pov_universe = pov_universe / total_pop if total_pop > 0 else 0
        pct_dis_universe = dis_universe / total_pop if total_pop > 0 else 0
        
        for key, item in self.toshis.items():
            tab_column = self.risk_column_map[key]
            bins = self.toshi_bins[key]

            risk_raw = row[tab_column]
            risk = self.round_to_sigfig(row[tab_column], 1)

            # Update the max risk for this toshi if necessary (using rounded risk)
            if risk > self.max_risk[key]:
                self.max_risk[key] = risk

            if risk <= 1:
                selected_bin = 0
            elif risk <= 2:
                selected_bin = 1
            elif risk <= 3:
                selected_bin = 2
            elif risk <= 4:
                selected_bin = 3
            elif risk <= 5:
                selected_bin = 4
            elif risk <= 6:
                selected_bin = 5
            elif risk <= 7:
                selected_bin = 6
            elif risk <= 8:
                selected_bin = 7
            elif risk <= 9:
                selected_bin = 8
            elif risk <= 10:
                selected_bin = 9
            else:
                selected_bin = 10

            # We have to update three rows here: the selected risk bin, the total, and the (eventual) average. Since
            # the average has to be weighted by the risk value, we will just use a "risk" of 1 for the other two to
            # unify the assignment code.
            # Note: non-rounded HIs are used here
            rows = [selected_bin, 11, 12]
            for r in rows:
                risk_value = risk_raw if r == 12 else 1
                bins[r][0] += population * risk_value
                bins[r][1] += population * pct_white * risk_value
                bins[r][2] += population * pct_black * risk_value
                bins[r][3] += population * pct_amerind * risk_value
                bins[r][4] += population * pct_asian * risk_value
                bins[r][5] += population * pct_other * risk_value
                bins[r][6] += population * pct_hisp * risk_value
                bins[r][7] += population * pct_age_lt18 * risk_value
                bins[r][8] += population * (1 - pct_age_gt64 - pct_age_lt18) * risk_value
                bins[r][9] += population * pct_age_gt64 * risk_value
                bins[r][10] += population * pct_edu_universe * risk_value
                bins[r][11] += population * pct_edu_universe * pct_edu_lths * risk_value
                bins[r][12] += population * pct_pov_universe * pct_pov * risk_value
                bins[r][13] += population * pct_pov_universe * pct_2xpov * risk_value
                bins[r][14] += population * pct_lingiso * risk_value
                bins[r][15] += population * pct_minority * risk_value
                bins[r][17] += population * pct_dis_universe * pct_dis * risk_value
            
    def tabulate_mir_data(self, row):

        # Identify the block group corresponding to this row.
        group_id = row['fips'] + row['block'][:7]
        block_group = self.acs_dict[group_id] if group_id in self.acs_dict else None

        population = row['population']

        total_pop = self.get_value(block_group, group_id, 'TOTALPOP', False)
        pct_minority = self.get_value(block_group, group_id, 'PCT_MINORITY')
        pct_white = self.get_value(block_group, group_id, 'PCT_WHITE')
        pct_black = self.get_value(block_group, group_id, 'PCT_BLACK')
        pct_amerind = self.get_value(block_group, group_id, 'PCT_AMIND')
        pct_asian = self.get_value(block_group, group_id, 'PCT_ASIAN')
        pct_other = self.get_value(block_group, group_id, 'PCT_OTHER_RACE')
        pct_hisp = self.get_value(block_group, group_id, 'PCT_HISP')
        pct_age_lt18 = self.get_value(block_group, group_id, 'PCT_AGE_LT18')
        pct_age_gt64 = self.get_value(block_group, group_id, 'PCT_AGE_GT64')
        edu_universe = self.get_value(block_group, group_id, 'EDU_UNIVERSE', False)
        pct_edu_lths = self.get_value(block_group, group_id, 'PCT_EDU_LTHS')
        pov_universe = self.get_value(block_group, group_id, 'POV_UNIVERSE', False)
        pct_2xpov = self.get_value(block_group, group_id, 'PCT_LOWINC')
        pct_pov = self.get_value(block_group, group_id, 'PCT_POV')
        pct_lingiso = self.get_value(block_group, group_id, 'PCT_LINGISO')
        pct_dis = self.get_value(block_group, group_id, 'PCT_DIS')
        dis_universe = self.get_value(block_group, group_id, 'DIS_UNIVERSE', False)
        
        if pct_white is None or pct_black is None or pct_amerind is None or pct_asian is None or pct_other is None or pct_hisp is None \
                or pct_age_lt18 is None \
                or pct_age_gt64 is None or pct_edu_lths is None \
                or pct_2xpov is None or pct_lingiso is None or pov_universe is None or edu_universe is None \
                or pct_minority is None or pct_pov is None or pct_dis is None or dis_universe is None:
            print("Unable to compile enough data to include this record: " + group_id)
            return

        pct_edu_universe = edu_universe / total_pop if total_pop > 0 else 0
        pct_pov_universe = pov_universe / total_pop if total_pop > 0 else 0
        pct_dis_universe = dis_universe / total_pop if total_pop > 0 else 0

        # Assign the block to a risk bin...this means not only giving the entire population represented by the block
        # to the total population column, but also giving a percentage of it to each sub group (based on the ACS
        # data.)
        risk = row['mir_rounded'] * 1000000
        risk_raw = row['mir'] * 1000000

        # Update the max risk for mir if necessary (using rounded risk)
        if risk > self.max_risk['mir']:
            self.max_risk['mir'] = risk

        if risk < 1:
            selected_bin = 0
        elif risk < 5:
            selected_bin = 1
        elif risk < 10:
            selected_bin = 2
        elif risk < 20:
            selected_bin = 3
        elif risk < 30:
            selected_bin = 4
        elif risk < 40:
            selected_bin = 5
        elif risk < 50:
            selected_bin = 6
        elif risk < 100:
            selected_bin = 7
        elif risk < 200:
            selected_bin = 8
        elif risk < 300:
            selected_bin = 9
        else:
            selected_bin = 10

        # We have to update three rows here: the selected risk bin, the total, and the (eventual) average. Since the
        # average has to be weighted by the risk value, we will just use a "risk" of 1 for the other two to unify
        # the assignment code.
        # Note: non-rounded risk is used here
        rows = [selected_bin, 11, 12]
        for r in rows:
            risk_value = risk_raw if r == 12 else 1
            self.cancer_bins[r][0] += population * risk_value
            self.cancer_bins[r][1] += population * pct_white * risk_value
            self.cancer_bins[r][2] += population * pct_black * risk_value
            self.cancer_bins[r][3] += population * pct_amerind * risk_value
            self.cancer_bins[r][4] += population * pct_asian * risk_value
            self.cancer_bins[r][5] += population * pct_other * risk_value
            self.cancer_bins[r][6] += population * pct_hisp * risk_value
            self.cancer_bins[r][7] += population * pct_age_lt18 * risk_value
            self.cancer_bins[r][8] += population * (1 - pct_age_gt64 - pct_age_lt18) * risk_value
            self.cancer_bins[r][9] += population * pct_age_gt64 * risk_value
            self.cancer_bins[r][10] += population * pct_edu_universe * risk_value
            self.cancer_bins[r][11] += population * pct_edu_universe * pct_edu_lths * risk_value
            self.cancer_bins[r][12] += population * pct_pov_universe * pct_pov * risk_value
            self.cancer_bins[r][13] += population * pct_pov_universe * pct_2xpov * risk_value
            self.cancer_bins[r][14] += population * pct_lingiso * risk_value
            self.cancer_bins[r][15] += population * pct_minority * risk_value
            self.cancer_bins[r][17] += population * pct_dis_universe * pct_dis * risk_value

    def write_missing_block_groups(self):
        if len(self.missing_block_groups) > 0:
            filepath = os.path.join(self.missing_block_group_path, str(int(self.radius)) +
                                    '_km_defaulted_block_groups.txt')
            Logger.logMessage("Writing defaulted block group file: " + str(filepath))
            
            with open(filepath, "w") as f:
                wr = csv.writer(f, delimiter="-")
                wr.writerows(self.missing_block_groups)
                
#            with open(filepath, 'w') as f:
#                for item in self.missing_block_groups:
#                    f.write("%s\n" % item)

    def get_value(self, block_group, block_group_id, subgroup, is_pct=True):

        if block_group is not None:
            value = block_group[subgroup]
        else:
            if not any(block_group_id in sublist for sublist in self.missing_block_groups):
                Logger.logMessage("Block group not found in ACS data will be defaulted: " + str(block_group_id))

        if block_group is None or isna(value):

            tract_id = block_group_id[:-1]

            # first search for missing block group ID in the default dictionary by using block group
            if block_group_id in self.levels_dict:
                bkgrp_def = self.levels_dict[block_group_id]
                value = bkgrp_def[subgroup]
                if not any(block_group_id in sublist for sublist in self.missing_block_groups):
                    self.missing_block_groups.append([block_group_id,'defaulted by Decennial Census block group'])
            
            # next look using the tract ID
            elif tract_id in self.levels_dict:
                tract_def = self.levels_dict[block_group_id] 
                value = tract_def[subgroup]
                if not any(block_group_id in sublist for sublist in self.missing_block_groups):
                    self.missing_block_groups.append([block_group_id,'defaulted by tract'])
        
            # now try county
            else:
                county_id = block_group_id[:5]
                if county_id in self.levels_dict:
                    county = self.levels_dict[county_id]
                    value = county[subgroup]
                    if not any(block_group_id in sublist for sublist in self.missing_block_groups):
                        self.missing_block_groups.append([block_group_id,'defaulted by county'])

                else:
                    Logger.logMessage("Couldn't resolve this record by block group, tract, or county! " + block_group_id)
                    return None

        return value / 100 if is_pct else value

    @staticmethod
    def round_to_sigfig(x, sig=1):
        # Convert float to decimal and set rounding definition
        dc = getcontext()
        dc.rounding = ROUND_HALF_UP
        str_x = str(x)
        d = Decimal(str_x)

        if x == 0:
            return 0;

        if isnan(x):
            return float('NaN')

        # Round using decimal definition then switch result back to float
        rounded = round(d, sig-int(floor(log10(abs(x))))-1)
        rounded = float(rounded)
        return rounded
