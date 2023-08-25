from com.sca.hem4.upload.UserReceptors import rec_type
from com.sca.hem4.writer.csv.AllOuterReceptors import *
from com.sca.hem4.FacilityPrep import *
import pandas as pd

blk_type = 'blk_type';


class BlockSummaryChronicNonCensus(CsvWriter, InputFile):
    """
    Provides the risk and each TOSHI for every census block modeled, as well as additional block information.
    """

    def __init__(self, targetDir=None, facilityId=None, model=None, plot_df=None,
                 filenameOverride=None, createDataframe=False, outerAgg=None):
        # Initialization for CSV reading/writing. If no file name override, use the
        # default construction.
        self.targetDir = targetDir
        filename = facilityId + "_block_summary_chronic.csv" if filenameOverride is None else filenameOverride
        path = os.path.join(self.targetDir, filename)

        CsvWriter.__init__(self, model, plot_df)
        InputFile.__init__(self, path, createDataframe)

        self.filename = path

        # Local cache for URE/RFC values
        self.riskCache = {}

        # Local cache for organ endpoint values
        self.organCache = {}

        self.outerAgg = outerAgg

    def getHeader(self):
        return ['Latitude', 'Longitude', 'Overlap', 'Elevation (m)', 'Receptor ID', 'X', 'Y', 'Hill',
                'Population', 'MIR', 'Respiratory HI', 'Liver HI', 'Neurological HI', 'Developmental HI',
                'Reproductive HI', 'Kidney HI', 'Ocular HI', 'Endocrine HI', 'Hematological HI',
                'Immunological HI', 'Skeletal HI', 'Spleen HI', 'Thyroid HI', 'Whole body HI', 
                'Discrete/Interpolated Receptor', 'Receptor Type']

    def getColumns(self):
        return [lat, lon, overlap, elev, rec_id, utme, utmn, hill, population,
                mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol, 
                blk_type, rec_type]

    def generateOutputs(self):
        """
        plot_df is not needed. Instead, the allinner and allouter receptor
        outputs are used to compute cancer risk and HI's at each block receptor.
        """
        
        allinner_df = self.model.all_inner_receptors_df.copy()

        # Sum the All Inner concs to fips/block/lat/lon/pollutant
        sumcols = [rec_id, lat, lon, pollutant, overlap, population, conc]
        aggs = {rec_id:'first', lat:'first', lon:'first', pollutant:'first', 
                overlap:'first', population:'first', conc:'sum'}        
        allinner_sum = allinner_df.groupby([rec_id, lat, lon, pollutant],
                                           as_index=False).agg(aggs)[sumcols]

        innerblocks = self.model.innerblks_df[[lat, lon, utme, utmn, elev, hill]]

        # join inner receptor df with the inner block df and then select columns
        columns = [pollutant, conc, lat, lon, rec_id, overlap, elev,
                   utme, utmn, population, hill]
        innermerged = allinner_sum.merge(innerblocks, on=[lat, lon])[columns]

        #=========== New way =============================================
        
        unique_pollutants = innermerged[pollutant].unique().tolist()
        
        # Get the dose response data for all the pollutants
        drdata_df = self.getUreRfc(unique_pollutants)
        
        # Compute risk and HI
        risk_df = innermerged[[pollutant, conc, lat, lon]].merge(drdata_df, on=pollutant)
        risk_df[mir] = risk_df[conc] * risk_df[ure]
        risk_df[hi_resp] = (risk_df[conc] * risk_df['invrfc'] * risk_df['resp']) / 1000
        risk_df[hi_live] = (risk_df[conc] * risk_df['invrfc'] * risk_df['live']) / 1000
        risk_df[hi_neur] = (risk_df[conc] * risk_df['invrfc'] * risk_df['neur']) / 1000
        risk_df[hi_deve] = (risk_df[conc] * risk_df['invrfc'] * risk_df['deve']) / 1000
        risk_df[hi_repr] = (risk_df[conc] * risk_df['invrfc'] * risk_df['repr']) / 1000
        risk_df[hi_kidn] = (risk_df[conc] * risk_df['invrfc'] * risk_df['kidn']) / 1000
        risk_df[hi_ocul] = (risk_df[conc] * risk_df['invrfc'] * risk_df['ocul']) / 1000
        risk_df[hi_endo] = (risk_df[conc] * risk_df['invrfc'] * risk_df['endo']) / 1000
        risk_df[hi_hema] = (risk_df[conc] * risk_df['invrfc'] * risk_df['hema']) / 1000
        risk_df[hi_immu] = (risk_df[conc] * risk_df['invrfc'] * risk_df['immu']) / 1000
        risk_df[hi_skel] = (risk_df[conc] * risk_df['invrfc'] * risk_df['skel']) / 1000
        risk_df[hi_sple] = (risk_df[conc] * risk_df['invrfc'] * risk_df['sple']) / 1000
        risk_df[hi_thyr] = (risk_df[conc] * risk_df['invrfc'] * risk_df['thyr']) / 1000
        risk_df[hi_whol] = (risk_df[conc] * risk_df['invrfc'] * risk_df['whol']) / 1000
        
        # Put risk and HI into innermerged
        riskcols = [pollutant, lat, lon, mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, 
                    hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, 
                    hi_thyr, hi_whol]
        innermerged = innermerged.merge(risk_df[riskcols], on=[pollutant,lat,lon])
        

        #=========== Old way =============================================
        
        # # compute cancer and noncancer values for each Inner rececptor row
        # innermerged[[mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, hi_endo,
        #              hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]] = \
        #     innermerged.apply(lambda row: self.calculateRisks(row[pollutant], row[conc]), axis=1)

        # For the Inner and Outer receptors, group by lat,lon and then aggregate each group by summing the mir and hazard index fields
        aggs = {pollutant:'first', lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first',
                utmn:'first', hill:'first', conc:'first', rec_id:'first', population:'first',
                mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}

        newcolumns = [lat, lon, overlap, elev, rec_id, utme, utmn, hill, population,
                      mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul,
                      hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]

        inneragg = innermerged.groupby([lat, lon]).agg(aggs)[newcolumns]

        # Add a column to indicate type of census block. D => discrete, I => interpolated
        inneragg[blk_type] = "D"
        if self.outerAgg is not None:
            self.outerAgg[blk_type] = "I"

        # append the inner and outer values and write
        if self.outerAgg is not None:
            self.dataframe = pd.concat([inneragg, self.outerAgg], ignore_index=True).sort_values(by=[rec_id])
        else:
            self.dataframe = inneragg
    
        # Assign receptor type to block summary chronic DF from the inner and outer census DFs.
        if not self.model.outerblks_df.empty:
            allrectype = pd.concat([self.model.innerblks_df[[utme,utmn,rec_type]], 
                                 self.model.outerblks_df[[utme,utmn,rec_type]]], ignore_index=True)
        else:
            allrectype = self.model.innerblks_df[[utme,utmn,rec_type]]
        self.dataframe = pd.merge(self.dataframe, allrectype, how="left", on=[utme, utmn])   

        
        self.data = self.dataframe.values
        yield self.dataframe

    def calculateRisks(self, pollutant_name, conc):
        URE = None
        RFC = None

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
                URE = 0
                RFC = 0
            else:
                URE = row.iloc[0][ure]
                RFC = row.iloc[0][rfc]

            self.riskCache[pollutant_name] = {ure : URE, rfc : RFC}

        organs = None
        if pollutant_name in self.organCache:
            organs = self.organCache[pollutant_name]
        else:
            row = self.model.organs.dataframe.loc[
                self.model.organs.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if row.size == 0:
                # Couldn't find the pollutant...set values to 0 and log message
                listed = []
            else:
                listed = row.values.tolist()

            # Note: sometimes there is a pollutant with no effect on any organ (RFC == 0). In this case it will
            # not appear in the organs library, and therefore 'listed' will be empty. We will just assign a
            # dummy list in this case...
            organs = listed[0] if len(listed) > 0 else [0]*16
            self.organCache[pollutant_name] = organs

        risks = []
        MIR = conc * URE
        risks.append(MIR)

        # Note: indices 2-15 correspond to the organ response value columns in the organs library...
        for i in range(2, 16):
            hazard_index = (0 if RFC == 0 else (conc/RFC/1000)*organs[i])
            risks.append(hazard_index)
        return Series(risks)


    def getUreRfc(self, pollist):
        # Take a unique list of pollutant names and find their URE, RFC (inverted) and target organs
        URE = None
        invRFC = None
        organs = None
        
        drlist = []
        
        for pol in pollist:
            risks = [pol]
            pattern = '^' + re.escape(pol) + '$'
            
            drrow = self.model.haplib.dataframe.loc[
                self.model.haplib.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]
            
            if drrow.size == 0:
                URE = 0
                invRFC = 0
            else:
                URE = drrow.iloc[0][ure]
                invRFC = 0 if drrow.iloc[0][rfc] == 0 else 1/drrow.iloc[0][rfc]
            
            risks.extend([URE, invRFC])
                        
            targetrow = self.model.organs.dataframe.loc[
                self.model.organs.dataframe[pollutant].str.contains(pattern, case=False, regex=True)]

            if targetrow.size == 0:
                organs = [0]*14
            else:
                organs = targetrow.values.tolist()[0][2:]

            risks.extend(organs)
            
            drlist.append(risks)
                   
        DR_df = pd.DataFrame(drlist, columns=[pollutant,'ure','invrfc','resp','live','neur','deve','repr',
                                              'kidn','ocul','endo','hema','immu','skel','sple',
                                              'thyr','whol'])
        
        return DR_df
    
    
    def createDataframe(self):
        # Type setting for CSV reading
        self.numericColumns = [lat, lon, elev, utme, utmn, population, hill, mir, hi_resp, hi_live, hi_neur, hi_deve,
                               hi_repr, hi_kidn, hi_ocul, hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol]
        self.strColumns = [rec_id, overlap, blk_type, rec_type]

        df = self.readFromPathCsv(self.getColumns())
        return df.fillna("")
