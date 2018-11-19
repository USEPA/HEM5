import os
import re

from pandas import Series
from numpy import float64

from log import Logger
from writer.csv.CsvWriter import CsvWriter


class BlockSummaryChronic(CsvWriter):
    """
    Provides the risk and each TOSHI for every census block modeled, as well as additional block information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_block_summary_chronic.csv")

        # Local cache for URE/RFC values
        self.riskCache = {}

        # Local cache for organ endpoint values
        self.organCache = {}

    def calculateOutputs(self):
        """
        plot_df is not needed. Instead, the allinner and allouter receptor
        outputs are used to compute cancer risk and HI's at each block receptor.
        """

        self.headers = ['lat', 'lon', 'overlap', 'elevation', 'fips', 'block', 'x', 'y', 'hill', 'population',
                        'mir', 'hi_resp', 'hi_live', 'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul',
                        'hi_endo', 'hi_hema', 'hi_immu', 'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol', 'rectype']

        allinner_df = self.model.all_inner_receptors_df.copy()
        allouter_df = self.model.all_outer_receptors_df.copy()
        
        innerblocks = self.model.innerblks_df[['LAT', 'LON', 'utme', 'utmn', 'HILL']]
        outerblocks = self.model.outerblks_df[['LAT', 'LON', 'utme', 'utmn', 'HILL']]        

        # rename and retype various columns to make them joinable
        allinner_df.rename(columns=self.lowercase, inplace=True)
        allouter_df.rename(columns=self.lowercase, inplace=True)
        allinner_df['lat'] = allinner_df['lat'].astype(float64)
        allinner_df['lon'] = allinner_df['lon'].astype(float64)
        allouter_df['lat'] = allouter_df['lat'].astype(float64)
        allouter_df['lon'] = allouter_df['lon'].astype(float64)
        allinner_df['elevation'] = allinner_df['elevation'].astype(float64)
        allouter_df['elevation'] = allouter_df['elevation'].astype(float64)
        innerblocks.rename(columns=self.lowercase, inplace=True)
        outerblocks.rename(columns=self.lowercase, inplace=True)

        # join inner receptor df with the inner block df and then select columns
        columns = ['pollutant', 'conc_ug_m3', 'lat', 'lon', 'fips', 'block', 'overlap', 'elevation', 
                   'utme', 'utmn', 'population', 'hill']
        innermerged = allinner_df.merge(innerblocks, on=['lat', 'lon'])[columns]

        # join outer receptor df with the outer block df and then select columns
        outermerged = allouter_df.merge(outerblocks, on=['lat', 'lon'])[columns]

        # compute cancer and noncancer values for each Inner rececptor row
        innermerged[['mir', 'hi_resp', 'hi_live', 'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul', 'hi_endo',
                'hi_hema', 'hi_immu', 'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol']] =\
            innermerged.apply(lambda row: self.calculateRisks(row['pollutant'], row['conc_ug_m3']), axis=1)

        # compute cancer and noncancer values for each Outer rececptor row
        outermerged[['mir', 'hi_resp', 'hi_live', 'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul', 'hi_endo',
                'hi_hema', 'hi_immu', 'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol']] =\
            outermerged.apply(lambda row: self.calculateRisks(row['pollutant'], row['conc_ug_m3']), axis=1)
        
#        print('inner merged size = ' + str(innermerged.size))
#        print('outer merged size = ' + str(outermerged.size))

        # For the Inner and Outer receptors, group by lat,lon and then aggregate each group by summing the mir and hazard index fields
        aggs = {'pollutant':'first', 'lat':'first', 'lon':'first', 'overlap':'first', 'elevation':'first', 'utme':'first',
                'utmn':'first', 'hill':'first', 'conc_ug_m3':'first', 'fips':'first', 'block':'first', 'population':'first',
                'mir':'sum', 'hi_resp':'sum', 'hi_live':'sum', 'hi_neur':'sum', 'hi_deve':'sum',
                'hi_repr':'sum', 'hi_kidn':'sum', 'hi_ocul':'sum', 'hi_endo':'sum', 'hi_hema':'sum',
                'hi_immu':'sum', 'hi_skel':'sum', 'hi_sple':'sum', 'hi_thyr':'sum', 'hi_whol':'sum'}

        newcolumns = ['lat', 'lon', 'overlap', 'elevation', 'fips', 'block', 'utme', 'utmn', 'hill', 'population',
                      'mir', 'hi_resp', 'hi_live', 'hi_neur', 'hi_deve', 'hi_repr', 'hi_kidn', 'hi_ocul', 
                      'hi_endo', 'hi_hema', 'hi_immu', 'hi_skel', 'hi_sple', 'hi_thyr', 'hi_whol']

        inneragg = innermerged.groupby(['lat', 'lon']).agg(aggs)[newcolumns]
        outeragg = outermerged.groupby(['lat', 'lon']).agg(aggs)[newcolumns]

        # add a receptor type column to note if inner or outer. I => inner, O => outer
        inneragg["rectype"] = "I"
        outeragg["rectype"] = "O"
                                
        # append the inner and outer values and write
        self.data = inneragg.append(outeragg, ignore_index = True).sort_values(by=['fips', 'block']).values
        

    def calculateRisks(self, pollutant, conc):
        URE = None
        RFC = None

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant) + '$'

        # Since it's relatively expensive to get these values from their respective libraries, cache them locally.
        # Note that they are cached as a pair (i.e. if one is in there, the other one will be too...)
        if pollutant in self.riskCache:
            URE = self.riskCache[pollutant]['URE']
            RFC = self.riskCache[pollutant]['RFC']
        else:
            row = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe["pollutant"].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                msg = 'Could not find pollutant ' + pollutant + ' in the haplib!'
                Logger.logMessage(msg)
                Logger.log(msg, self.model.haplib.dataframe, False)
                URE = 0
                RFC = 0
            else:
                URE = row.iloc[0]["ure"]
                RFC = row.iloc[0]["rfc"]

            self.riskCache[pollutant] = {'URE' : URE, 'RFC' : RFC}
#            print('Added cached values... ' + pollutant + ': ' + str(URE) + ', ' + str(RFC))

        organs = None
        if pollutant in self.organCache:
            organs = self.organCache[pollutant]
        else:
            row = self.model.organs.dataframe.loc[
                self.model.organs.dataframe["pollutant"].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                # Couldn't find the pollutant...set values to 0 and log message
                Logger.logMessage('Could not find pollutant ' + pollutant + ' in the target organs.')
                listed = []
            else:
                listed = row.values.tolist()

            # Note: sometimes there is a pollutant with no effect on any organ (RFC == 0). In this case it will
            # not appear in the organs library, and therefore 'listed' will be empty. We will just assign a
            # dummy list in this case...
            organs = listed[0] if len(listed) > 0 else list(range(16))
            self.organCache[pollutant] = organs
#            print('Added cached values... ' + pollutant + ': ' + str(organs))

        risks = []
        mir = conc * URE
        risks.append(mir)

        # Note: indices 2-15 correspond to the organ response value columns in the organs library...
        for i in range(2, 16):
            hazard_index = (0 if RFC == 0 else (conc/RFC/1000)*organs[i])
            risks.append(hazard_index)
        return Series(risks)

    def lowercase(self, col):

        if col == 'Elev_m':
            return 'elev';
        else:
            return col.lower()
        