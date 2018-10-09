import os

from numpy import float64
from pandas import Series

from writer.csv.CsvWriter import CsvWriter

class RingSummaryChronic(CsvWriter):
    """
    Provides the risk and each TOSHI for every census block modeled, as well as additional block information.
    """

    def __init__(self, targetDir, facilityId, model, plot_df):
        CsvWriter.__init__(self, model, plot_df)

        self.filename = os.path.join(targetDir, facilityId + "_ring_summary_chronic.csv")

        # Local cache for URE/RFC values
        self.riskCache = {}

        # Local cache for organ endpoint values
        self.organCache = {}

    def calculateOutputs(self):
        """
        Note that this implementation does NOT use the plot file data, because the polar receptor concentrations have
        already been processed and stored in the model (see model.all_polar_receptors)
        """

        self.headers = ['Lat', 'Lon', 'Overlap', 'Elevation', 'X', 'Y', 'Hill', 'Mir', 'Hi_resp', 'Hi_liver', 'Hi_neuro',
                        'Hi_devel', 'Hi_repro', 'Hi_kidney', 'Hi_ocular', 'Hi_endoc', 'Hi_hemato', 'Hi_immune', 'Hi_skel',
                        'Hi_spleen', 'Hi_thyroid', 'Hi_whol_bo', 'Distance', 'Angle', 'Sector']

        allpolar_df = self.model.all_polar_receptors_df.copy()

        # rename and retype various columns to make them joinable
        allpolar_df.rename(columns=self.lowercase, inplace=True)
        allpolar_df['lat'] = allpolar_df['lat'].astype(float64)
        allpolar_df['lon'] = allpolar_df['lon'].astype(float64)
        allpolar_df['elev'] = allpolar_df['elev'].astype(float64)
        allpolar_df['angle'] = allpolar_df['angle'].astype(float64)

        # join with the polar grid df and then select columns
        columns = ['pollutant', 'conc_ug_m3', 'lat', 'lon', 'overlap', 'elev', 'utme', 'utmn', 'hill', 'distance', 'angle',
                   'sector']
        merged = allpolar_df.merge(self.model.polargrid, on=['lat', 'lon', 'elev', 'angle', 'overlap'])[columns]

        # get a URE value for each row, by joining with the dose response library (on pollutant)
        merged[['Mir', 'Hi_resp', 'Hi_liver', 'Hi_neuro', 'Hi_devel', 'Hi_repro', 'Hi_kidney', 'Hi_ocular', 'Hi_endoc',
                'Hi_hemato', 'Hi_immune', 'Hi_skel', 'Hi_spleen', 'Hi_thyroid', 'Hi_whol_bo']] =\
            merged.apply(lambda row: self.calculateRisks(row['pollutant'], row['conc_ug_m3']), axis=1)

        # last step: group by lat,lon and then aggregate each group by summing the mir and hazard index fields
        aggs = {'pollutant':'first', 'lat':'first', 'lon':'first', 'overlap':'first', 'elev':'first', 'utme':'first',
                'utmn':'first', 'hill':'first', 'conc_ug_m3':'first', 'distance':'first', 'angle':'first',
                'sector':'first', 'Mir':'sum', 'Hi_resp':'sum', 'Hi_liver':'sum', 'Hi_neuro':'sum', 'Hi_devel':'sum',
                'Hi_repro':'sum', 'Hi_kidney':'sum', 'Hi_ocular':'sum', 'Hi_endoc':'sum', 'Hi_hemato':'sum',
                'Hi_immune':'sum', 'Hi_skel':'sum', 'Hi_spleen':'sum', 'Hi_thyroid':'sum', 'Hi_whol_bo':'sum'}

        newcolumns = ['lat', 'lon', 'overlap', 'elev', 'utme', 'utmn', 'hill', 'Mir', 'Hi_resp', 'Hi_liver', 'Hi_neuro',
                      'Hi_devel', 'Hi_repro', 'Hi_kidney', 'Hi_ocular', 'Hi_endoc', 'Hi_hemato', 'Hi_immune', 'Hi_skel',
                      'Hi_spleen', 'Hi_thyroid', 'Hi_whol_bo', 'distance', 'angle', 'sector']
        self.data = merged.groupby(['lat', 'lon']).agg(aggs)[newcolumns].values

    def calculateRisks(self, pollutant, conc):
        URE = None
        RFC = None

        # Since it's relatively expensive to get these values from their respective libraries, cache them locally.
        # Note that they are cached as a pair (i.e. if one is in there, the other one will be too...)
        if pollutant in self.riskCache:
            URE = self.riskCache[pollutant]['URE']
            RFC = self.riskCache[pollutant]['RFC']
        else:
            row = self.model.haplib.dataframe.loc[self.model.haplib.dataframe["pollutant"] == pollutant]
            URE = row.iloc[0]["ure"]
            RFC = row.iloc[0]["rfc"]
            self.riskCache[pollutant] = {'URE' : URE, 'RFC' : RFC}
            print('Added cached values... ' + pollutant + ': ' + str(URE) + ', ' + str(RFC))

        organs = None
        if pollutant in self.organCache:
            organs = self.organCache[pollutant]
        else:
            row = self.model.organs.dataframe.loc[self.model.organs.dataframe["pollutant"] == pollutant]
            organs = row.values.tolist()[0]
            self.organCache[pollutant] = organs
            print('Added cached values... ' + pollutant + ': ' + str(organs))

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