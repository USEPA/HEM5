import re
from com.sca.hem4.log import Logger
from com.sca.hem4.upload.DoseResponse import *
from com.sca.hem4.writer.excel.MaximumIndividualRisks import *

site_type = 'site_type';
conc_rnd = 'conc_rnd';

class RiskBreakdown(ExcelWriter):

    """
    Provides the max cancer risk and max TOSHI values at populated block (“MIR”) sites and at any (“max offsite impact”)
    sites broken down by source and pollutant, including total sources and all modeled pollutants combined, as well as
    the pollutant concentration, URE and RfC values.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        ExcelWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_risk_breakdown.xlsx")

        # Local cache for URE/RFC values
        self.riskCache = {}

        # Local cache for organ endpoint values
        self.organCache = {}


    def getHeader(self):
        return ['Site type', 'Parameter', 'Source ID', 'Pollutant', 'Emission type', 'Value', 'Value rounded',
                'Conc (µg/m3)', 'Conc rounded (µg/m3)', 'Emissions (tpy)',
                'URE 1/(µg/m3)', 'RFc (mg/m3)']

    def generateOutputs(self):
        """
        Compute the sourceid and pollutant breakdown of each maximum risk and HI location.
        """

        # Dictionary for mapping HI name to position in the target organ list
        self.hidict = {"Respiratory HI":2, "Liver HI":3, "Neurological HI":4,
                       "Developmental HI":5, "Reproductive HI":6, "Kidney HI":7,
                       "Ocular HI":8, "Endocrine HI":9, "Hematological HI":10,
                       "Immunological HI":11, "Skeletal HI":12, "Spleen HI":13,
                       "Thyroid HI":14, "Whole body HI":15}

        # Initialize output dataframe
        columns = [site_type, parameter, source_id, pollutant, ems_type, value, value_rnd, conc, conc_rnd, emis_tpy, ure, rfc]
        riskbkdn_df = pd.DataFrame(columns=columns)


        # Dictionary for mapping cancer and HI names used in max_indiv_risk df to
        # those used in risk_by_latlon df
        namemap = {"Cancer risk":"mir", "Respiratory HI":"hi_resp", "Liver HI":"hi_live",
                   "Neurological HI":"hi_neur", "Developmental HI":"hi_deve", "Reproductive HI":"hi_repr",
                   "Kidney HI":"hi_kidn", "Ocular HI":"hi_ocul", "Endocrine HI":"hi_endo",
                   "Hematological HI":"hi_hema", "Immunological HI":"hi_immu", "Skeletal HI":"hi_skel",
                   "Spleen HI":"hi_sple", "Thyroid HI":"hi_thyr", "Whole body HI":"hi_whol"}


        # Loop over the max inidividual risk dataframe
        for index, row in self.model.max_indiv_risk_df.iterrows():

            # ----------- First breakdown max individual risk for this parameter ---------------

            # If max cancer or noncancer is > 0, compute source/pollutant breakdown values, otherwise set breakdown to 0
            if row[value] > 0:

                # Get source and pollutant specific concs. Depends on receptor type.
                if row[notes] == "Discrete":
                    concdata = self.model.all_inner_receptors_df[[lat,lon,source_id,pollutant,ems_type,conc]] \
                        [(self.model.all_inner_receptors_df[lat]==row[lat]) &
                         (self.model.all_inner_receptors_df[lon]==row[lon])]
                elif row[notes] == "Polar":
                    concdata = self.model.all_polar_receptors_df[[lat,lon,source_id,pollutant,ems_type,conc]] \
                        [(self.model.all_polar_receptors_df[lat]==row[lat]) &
                         (self.model.all_polar_receptors_df[lon]==row[lon])]
                else:
                    concdata = self.model.all_outer_receptors_df[[lat,lon,source_id,pollutant,ems_type,conc]] \
                        [(self.model.all_outer_receptors_df[lat]==row[lat]) &
                         (self.model.all_outer_receptors_df[lon]==row[lon])]

                    # for consistency and ease of use, change some column names
                # concdata.rename(columns={source_id:"source_id", pollutant:"pollutant",
                #                          ems_type:ems_type, conc:conc}, inplace=True)

                # merge hapemis to get emis_tpy field
                bkdndata = pd.merge(concdata,self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]],
                                    on=[source_id,pollutant], how="left")

                # compute the value column (risk or HI)
                if row[parameter] == "Cancer risk":
                    bkdndata[value] = bkdndata.apply(lambda bkdnrow: self.calculateRisks(bkdnrow[pollutant],
                                                                                         bkdnrow[conc], "cancer"), axis=1)
                else:
                    bkdndata[value] = bkdndata.apply(lambda bkdnrow: self.calculateRisks(bkdnrow[pollutant],
                                                                                         bkdnrow[conc], row[parameter]), axis=1)

                # set the rounded value column
                bkdndata[value_rnd] = bkdndata[value].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

            else:

                # Max risk or HI value = 0. Get source/pollutant breakdown from hapemis.
                bkdndata = self.model.runstream_hapemis[["source_id","pollutant","emis_tpy"]].copy()
                bkdndata[value] = 0.0
                bkdndata[value_rnd] = 0.0
                bkdndata[conc] = 0.0
                bkdndata[conc_rnd] = 0.0
                bkdndata[ems_type] = "NA"

            # set the remaining columns in bkdndata
            bkdndata[ure], bkdndata[rfc] = zip(*bkdndata.apply(lambda row:
                                                               self.getRiskParms(row[pollutant])[0:2], axis=1))
            bkdndata[site_type] = "Max indiv risk"
            bkdndata[parameter] = row[parameter]
            bkdndata[conc_rnd] = bkdndata[conc].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

            # keep needed columns
            temp_df = bkdndata[columns]

            # append to riskbkdn_df
            riskbkdn_df = riskbkdn_df.append(temp_df, ignore_index=True)


            # ----------- Next, breakdown max offsite risk for this parameter ---------------

            # If max cancer or noncancer is > 0, then get max offsite breakdown, otherwise set breakdown to 0
            if row[value] > 0:

                # Find row with highest cancer or HI. This will occur at any inner or polar receptor that does not overlap.
                # The row[parameter] value indicates cancer or HI.
                io_idx = self.model.risk_by_latlon[(self.model.risk_by_latlon[rec_type] != "O") &
                                                   (self.model.risk_by_latlon[overlap] == "N")] \
                    [namemap[row[parameter]]].idxmax()

                # lat/lon and receptor type of max
                mr_lat = float(self.model.risk_by_latlon[lat].loc[io_idx])
                mr_lon = float(self.model.risk_by_latlon[lon].loc[io_idx])
                mr_rectype = self.model.risk_by_latlon[rec_type].loc[io_idx]

                # Get source and pollutant specific concs. Depends on receptor type.
                if mr_rectype == "I":
                    concdata = self.model.all_inner_receptors_df[[lat,lon,source_id,pollutant,ems_type,conc]] \
                        [(self.model.all_inner_receptors_df[lat] == mr_lat) &
                         (self.model.all_inner_receptors_df[lon] == mr_lon)]
                else:
                    concdata = self.model.all_polar_receptors_df[[lat,lon,source_id,pollutant,ems_type,conc]] \
                        [(self.model.all_polar_receptors_df[lat] == mr_lat) &
                         (self.model.all_polar_receptors_df[lon] == mr_lon)]
                
                # for consistency and ease of use, change some column names
                concdata.rename(columns={source_id:"source_id", pollutant:"pollutant",
                                         ems_type:ems_type, conc:conc}, inplace=True)

                # merge hapemis to get emis_tpy field
                bkdndata = pd.merge(concdata,self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]],
                                    on=[source_id,pollutant], how="left")

                # compute the value column (risk or HI)
                if row[parameter] == "Cancer risk":
                    bkdndata[value] = bkdndata.apply(lambda bkdnrow: self.calculateRisks(bkdnrow[pollutant],
                                                                                         bkdnrow[conc], "cancer"), axis=1)
                else:
                    bkdndata[value] = bkdndata.apply(lambda bkdnrow: self.calculateRisks(bkdnrow[pollutant],
                                                                                         bkdnrow[conc], row[parameter]), axis=1)

                # set the rounded value column
                bkdndata[value_rnd] = bkdndata[value].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

            else:

                # Max off-site risk or HI value = 0. Get source/pollutant breakdown from hapemis.
                bkdndata = self.model.runstream_hapemis[[source_id,pollutant,emis_tpy]].copy()
                bkdndata[value] = 0.0
                bkdndata[value_rnd] = 0.0
                bkdndata[conc] = 0.0
                bkdndata[conc_rnd] = 0.0
                bkdndata[ems_type] = "NA"

            # set the remaining columns in bkdndata
            bkdndata[ure], bkdndata[rfc] = zip(*bkdndata.apply(lambda row:
                                                               self.getRiskParms(row[pollutant])[0:2], axis=1))
            bkdndata[site_type] = "Max offsite impact"
            bkdndata[parameter] = row[parameter]
            bkdndata[conc_rnd] = bkdndata[conc].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

            # keep needed columns
            temp_df = bkdndata[columns]

            # append to riskbkdn_df
            riskbkdn_df = riskbkdn_df.append(temp_df, ignore_index=True)

        #TODO
        # Change dtype of conc. This will be done upstream later.
        riskbkdn_df[conc] = pd.to_numeric(riskbkdn_df[conc])
        
        
        #....... Create some aggregate rows ..................

        # Sum Value by site_type, parameter, and pollutant to get Total by pollutant
        riskbkdn_df[value] = pd.to_numeric(riskbkdn_df[value], errors='coerce')
        srctot = riskbkdn_df.groupby([site_type, parameter, pollutant, ure, rfc],
                                     as_index=False)[value, conc, emis_tpy].sum()
        srctot[source_id] = "Total by pollutant all sources"
        srctot[ems_type] = "NA"
        srctot[ure] = 0.0
        srctot[rfc] = 0.0
                
        srctot[value_rnd] = srctot[value].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)
        srctot[conc_rnd] = srctot[conc].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

        # Sum Value by site_type, parameter, and source_id to get Total by source_id
        polltot = riskbkdn_df.groupby([site_type, parameter, source_id],
                                      as_index=False)[value, conc, emis_tpy].sum()
        polltot[pollutant] = "All modeled pollutants"
        polltot[ems_type] = "NA"
        polltot[ure] = 0.0
        polltot[rfc] = 0.0
        polltot[value_rnd] = polltot[value].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)
        polltot[conc_rnd] = polltot[conc].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

        # Sum Value by site_type and parameter to get Total by parameter
        alltot = riskbkdn_df.groupby([site_type, parameter],
                                      as_index=False)[value, conc, emis_tpy].sum()
        alltot[source_id] = "Total"
        alltot[pollutant] = "All pollutants all sources"
        alltot[ems_type] = "NA"
        alltot[ure] = 0.0
        alltot[rfc] = 0.0
        alltot[value_rnd] = alltot[value].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)
        alltot[conc_rnd] = alltot[conc].apply(lambda x: round(x, -int(math.floor(math.log10(abs(x))))) if x > 0 else 0)

        # Append aggregates
        riskbkdn_df = riskbkdn_df.append(srctot, ignore_index=True)
        riskbkdn_df = riskbkdn_df.append(polltot, ignore_index=True)
        riskbkdn_df = riskbkdn_df.append(alltot, ignore_index=True)
        
        # Sort rows
        riskbkdn_df.sort_values([parameter, site_type, source_id, value],
                                ascending=[True, True, True, False], inplace=True)
        riskbkdn_df = riskbkdn_df[columns]
        
        # Done
        self.dataframe = riskbkdn_df
        self.data = self.dataframe.values
        yield self.dataframe


    def calculateRisks(self, pollutant_name, conc, risktype):
        URE, RFC, organs = self.getRiskParms(pollutant_name)

        if risktype == "cancer":
            risk = conc * URE
        else:
            # risktype is a non-cancer HI; use as an index to hidict
            risk = (0 if RFC == 0 else (conc/RFC/1000)*organs[self.hidict[risktype]])

        return risk


    def getRiskParms(self, pollutant_name):
        URE = 0.0
        RFC = 0.0

        # In order to get a case-insensitive exact match (i.e. matches exactly except for casing)
        # we are using a regex that is specified to be the entire value. Since pollutant names can
        # contain parentheses, escape them before constructing the pattern.
        pattern = '^' + re.escape(pollutant_name) + '$'

        # Since it's relatively expensive to get these values from their respective libraries, cache them locally.
        # Note that they are cached as a pair (i.e. if one is in there, the other one will be too...)
        if pollutant_name in self.riskCache:
            URE = self.riskCache[pollutant_name][ure]
            RFC = self.riskCache[pollutant_name][rfc]
        else:
            row = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                msg = 'Could not find pollutant ' + pollutant_name + ' in the haplib!'
                Logger.logMessage(msg)
                # Logger.log(msg, self.model.haplib.dataframe, False)
                URE = 0.0
                RFC = 0.0
            else:
                URE = row.iloc[0][ure]
                RFC = row.iloc[0][rfc]

            self.riskCache[pollutant_name] = {ure : URE, rfc : RFC}

        # organs is a list from the target organ table for one pollutant
        organs = None
        if pollutant_name in self.organCache:
            organs = self.organCache[pollutant_name]
        else:
            row = self.model.organs.dataframe.loc[
                self.model.organs.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                # Couldn't find the pollutant...set values to 0 and log message
                Logger.logMessage('Could not find pollutant ' + pollutant_name + ' in the target organs.')
                listed = []
            else:
                listed = row.values.tolist()

            # Note: sometimes there is a pollutant with no effect on any organ (RFC == 0). In this case it will
            # not appear in the organs library, and therefore 'listed' will be empty. We will just assign a
            # dummy list in this case...
            organs = listed[0] if len(listed) > 0 else list(range(16))
            self.organCache[pollutant_name] = organs

        return URE, RFC, organs
