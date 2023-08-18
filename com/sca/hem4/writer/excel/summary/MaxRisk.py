from com.sca.hem4.writer.csv.BlockSummaryChronicNonCensus import BlockSummaryChronicNonCensus
from com.sca.hem4.writer.excel.ExcelWriter import ExcelWriter
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.FacilityPrep import *
from com.sca.hem4.writer.excel.summary.AltRecAwareSummary import AltRecAwareSummary

risktype = 'risktype'
risk = 'risk'
notes = 'notes'

class MaxRisk(ExcelWriter, AltRecAwareSummary):

    def __init__(self, targetDir, facilityIds, parameters=None):
        self.name = "Maximum Risk Summary"
        self.categoryName = parameters[0]
        self.categoryFolder = targetDir
        self.facilityIds = facilityIds
        self.filename = os.path.join(targetDir, self.categoryName + "_max_risk.xlsx")

        self.altrec = self.determineAltRec(targetDir)

    def getHeader(self):
        if self.altrec == 'N':
            return ['Risk Type', 'FIPS', 'Block', 'Population', 'Risk', 'Notes']
        else:
            return ['Risk Type', 'Receptor ID', 'Population', 'Risk', 'Notes']

    def generateOutputs(self):
        Logger.log("Creating " + self.name + " report...", None, False)
                
        blocksummary_df = pd.DataFrame()
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId
            dirlist = os.listdir(targetDir)
            # Check for empty folder
            if len(dirlist) > 0:
                blockSummaryChronic = BlockSummaryChronicNonCensus(targetDir=targetDir, facilityId=facilityId) if self.altrec == 'Y' else\
                    BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId)
    
                bsc_df = blockSummaryChronic.createDataframe()
                blocksummary_df = pd.concat([blocksummary_df, bsc_df])

        blocksummary_df.drop_duplicates(inplace=True)
        blocksummary_df.reset_index(drop=True, inplace=True)
                
        if self.altrec == 'N':
                        
            # Census data
            
            # Only keep receptors where pop > 0 or user receptors
            blocksummary_df = blocksummary_df.loc[(blocksummary_df[population] > 0) |
                                                  (blocksummary_df[rec_type] == 'P')]
            
    
            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', blk_type:'first',
                    rec_type:'first',
                    utmn:'first', hill:'first', fips:'first', block:'first', population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}
    
            # Aggregate mir/HI, grouped by FIPS/block
            risk_summed = blocksummary_df.groupby([fips, block]).agg(aggs)[blockSummaryChronic.getColumns()]
            
            mir_row = risk_summed.loc[risk_summed[mir].idxmax()]
            if mir_row[2] == 'N':
                mir_notes = ''
            else:
                mir_notes = 'Overlapped receptor'
            hi_resp_row = risk_summed.loc[risk_summed[hi_resp].idxmax()]
            if hi_resp_row[2] == 'N':
                resp_notes = ''
            else:
                resp_notes = 'Overlapped receptor'
            hi_live_row = risk_summed.loc[risk_summed[hi_live].idxmax()]
            if hi_live_row[2] == 'N':
                live_notes = ''
            else:
                live_notes = 'Overlapped receptor'
            hi_neur_row = risk_summed.loc[risk_summed[hi_neur].idxmax()]
            if hi_neur_row[2] == 'N':
                neur_notes = ''
            else:
                neur_notes = 'Overlapped receptor'
            hi_deve_row = risk_summed.loc[risk_summed[hi_deve].idxmax()]
            if hi_deve_row[2] == 'N':
                deve_notes = ''
            else:
                deve_notes = 'Overlapped receptor'
            hi_repr_row = risk_summed.loc[risk_summed[hi_repr].idxmax()]
            if hi_repr_row[2] == 'N':
                repr_notes = ''
            else:
                repr_notes = 'Overlapped receptor'
            hi_kidn_row = risk_summed.loc[risk_summed[hi_kidn].idxmax()]
            if hi_kidn_row[2] == 'N':
                kidn_notes = ''
            else:
                kidn_notes = 'Overlapped receptor'
            hi_ocul_row = risk_summed.loc[risk_summed[hi_ocul].idxmax()]
            if hi_ocul_row[2] == 'N':
                ocul_notes = ''
            else:
                ocul_notes = 'Overlapped receptor'
            hi_endo_row = risk_summed.loc[risk_summed[hi_endo].idxmax()]
            if hi_endo_row[2] == 'N':
                endo_notes = ''
            else:
                endo_notes = 'Overlapped receptor'
            hi_hema_row = risk_summed.loc[risk_summed[hi_hema].idxmax()]
            if hi_hema_row[2] == 'N':
                hema_notes = ''
            else:
                hema_notes = 'Overlapped receptor'
            hi_immu_row = risk_summed.loc[risk_summed[hi_immu].idxmax()]
            if hi_immu_row[2] == 'N':
                immu_notes = ''
            else:
                immu_notes = 'Overlapped receptor'
            hi_skel_row = risk_summed.loc[risk_summed[hi_skel].idxmax()]
            if hi_skel_row[2] == 'N':
                skel_notes = ''
            else:
                skel_notes = 'Overlapped receptor'
            hi_sple_row = risk_summed.loc[risk_summed[hi_sple].idxmax()]
            if hi_sple_row[2] == 'N':
                sple_notes = ''
            else:
                sple_notes = 'Overlapped receptor'
            hi_thyr_row = risk_summed.loc[risk_summed[hi_thyr].idxmax()]
            if hi_thyr_row[2] == 'N':
                thyr_notes = ''
            else:
                thyr_notes = 'Overlapped receptor'
            hi_whol_row = risk_summed.loc[risk_summed[hi_whol].idxmax()]
            if hi_whol_row[2] == 'N':
                whol_notes = ''
            else:
                whol_notes = 'Overlapped receptor'
    
            risks = [
                ['mir', mir_row[4], mir_row[5], mir_row[9], mir_row[10], mir_notes] if mir_row[10] > 0
                    else ['mir', '', '', 0, 0, ''],
                ['respiratory', hi_resp_row[4], hi_resp_row[5], hi_resp_row[9], hi_resp_row[11], resp_notes] if hi_resp_row[11] > 0
                    else ['respiratory', '', '', 0, 0, ''],
                ['liver', hi_live_row[4], hi_live_row[5], hi_live_row[9], hi_live_row[12], live_notes] if hi_live_row[12] > 0
                    else ['liver', '', '', 0, 0, ''],
                ['neurological', hi_neur_row[4], hi_neur_row[5], hi_neur_row[9], hi_neur_row[13], neur_notes] if hi_neur_row[13] > 0
                    else ['neurological', '', '', 0, 0, ''],
                ['developmental', hi_deve_row[4], hi_deve_row[5], hi_deve_row[9], hi_deve_row[14], deve_notes] if hi_deve_row[14] > 0
                    else ['developmental', '', '', 0, 0, ''],
                ['reproductive', hi_repr_row[4], hi_repr_row[5], hi_repr_row[9], hi_repr_row[15], repr_notes] if hi_repr_row[15] > 0
                    else ['reproductive', '', '', 0, 0, ''],
                ['kidney', hi_kidn_row[4], hi_kidn_row[5], hi_kidn_row[9], hi_kidn_row[16], kidn_notes] if hi_kidn_row[16] > 0
                    else ['kidney', '', '', 0, 0, ''],
                ['ocular', hi_ocul_row[4], hi_ocul_row[5], hi_ocul_row[9], hi_ocul_row[17], ocul_notes] if hi_ocul_row[17] > 0
                    else ['ocular', '', '', 0, 0, ''],
                ['endocrine', hi_endo_row[4], hi_endo_row[5], hi_endo_row[9], hi_endo_row[18], endo_notes] if hi_endo_row[18] > 0
                    else ['endocrine', '', '', 0, 0, ''],
                ['hematological', hi_hema_row[4], hi_hema_row[5], hi_hema_row[9], hi_hema_row[19], hema_notes] if hi_hema_row[19] > 0
                    else ['hematological', '', '', 0, 0, ''],
                ['immunological', hi_immu_row[4], hi_immu_row[5], hi_immu_row[9], hi_immu_row[20], immu_notes] if hi_immu_row[20] > 0
                    else ['immunological', '', '', 0, 0, ''],
                ['skeletal', hi_skel_row[4], hi_skel_row[5], hi_skel_row[9], hi_skel_row[21], skel_notes] if hi_skel_row[21] > 0
                    else ['skeletal', '', '', 0, 0, ''],
                ['spleen', hi_sple_row[4], hi_sple_row[5], hi_sple_row[9], hi_sple_row[22], sple_notes] if hi_sple_row[22] > 0
                    else ['spleen', '', '', 0, 0, ''],
                ['thyroid', hi_thyr_row[4], hi_thyr_row[5], hi_thyr_row[9], hi_thyr_row[23], thyr_notes] if hi_thyr_row[23] > 0
                    else ['thyroid', '', '', 0, 0, ''],
                ['whole body', hi_whol_row[4], hi_whol_row[5], hi_whol_row[9], hi_whol_row[24], whol_notes] if hi_whol_row[24] > 0
                    else ['whole body', '', '', 0, 0, ''],
            ]
            maxrisk_df = pd.DataFrame(risks, columns=[risktype, fips, block, population, risk, notes])
            
        else:

            # Alternate receptors
                                    
            aggs = {lat:'first', lon:'first', overlap:'first', elev:'first', utme:'first', blk_type:'first',
                    rec_type:'first',
                    utmn:'first', hill:'first', rec_id: 'first', population:'first',
                    mir:'sum', hi_resp:'sum', hi_live:'sum', hi_neur:'sum', hi_deve:'sum',
                    hi_repr:'sum', hi_kidn:'sum', hi_ocul:'sum', hi_endo:'sum', hi_hema:'sum',
                    hi_immu:'sum', hi_skel:'sum', hi_sple:'sum', hi_thyr:'sum', hi_whol:'sum'}
    
            # Aggregate mir/HI, grouped by receptor id
            risk_summed = blocksummary_df.groupby([rec_id]).agg(aggs)[blockSummaryChronic.getColumns()]
            
            mir_row = risk_summed.loc[risk_summed[mir].idxmax()]
            if mir_row[2] == 'N':
                mir_notes = ''
            else:
                mir_notes = 'Overlapped receptor'
            hi_resp_row = risk_summed.loc[risk_summed[hi_resp].idxmax()]
            if hi_resp_row[2] == 'N':
                resp_notes = ''
            else:
                resp_notes = 'Overlapped receptor'
            hi_live_row = risk_summed.loc[risk_summed[hi_live].idxmax()]
            if hi_live_row[2] == 'N':
                live_notes = ''
            else:
                live_notes = 'Overlapped receptor'
            hi_neur_row = risk_summed.loc[risk_summed[hi_neur].idxmax()]
            if hi_neur_row[2] == 'N':
                neur_notes = ''
            else:
                neur_notes = 'Overlapped receptor'
            hi_deve_row = risk_summed.loc[risk_summed[hi_deve].idxmax()]
            if hi_deve_row[2] == 'N':
                deve_notes = ''
            else:
                deve_notes = 'Overlapped receptor'
            hi_repr_row = risk_summed.loc[risk_summed[hi_repr].idxmax()]
            if hi_repr_row[2] == 'N':
                repr_notes = ''
            else:
                repr_notes = 'Overlapped receptor'
            hi_kidn_row = risk_summed.loc[risk_summed[hi_kidn].idxmax()]
            if hi_kidn_row[2] == 'N':
                kidn_notes = ''
            else:
                kidn_notes = 'Overlapped receptor'
            hi_ocul_row = risk_summed.loc[risk_summed[hi_ocul].idxmax()]
            if hi_ocul_row[2] == 'N':
                ocul_notes = ''
            else:
                ocul_notes = 'Overlapped receptor'
            hi_endo_row = risk_summed.loc[risk_summed[hi_endo].idxmax()]
            if hi_endo_row[2] == 'N':
                endo_notes = ''
            else:
                endo_notes = 'Overlapped receptor'
            hi_hema_row = risk_summed.loc[risk_summed[hi_hema].idxmax()]
            if hi_hema_row[2] == 'N':
                hema_notes = ''
            else:
                hema_notes = 'Overlapped receptor'
            hi_immu_row = risk_summed.loc[risk_summed[hi_immu].idxmax()]
            if hi_immu_row[2] == 'N':
                immu_notes = ''
            else:
                immu_notes = 'Overlapped receptor'
            hi_skel_row = risk_summed.loc[risk_summed[hi_skel].idxmax()]
            if hi_skel_row[2] == 'N':
                skel_notes = ''
            else:
                skel_notes = 'Overlapped receptor'
            hi_sple_row = risk_summed.loc[risk_summed[hi_sple].idxmax()]
            if hi_sple_row[2] == 'N':
                sple_notes = ''
            else:
                sple_notes = 'Overlapped receptor'
            hi_thyr_row = risk_summed.loc[risk_summed[hi_thyr].idxmax()]
            if hi_thyr_row[2] == 'N':
                thyr_notes = ''
            else:
                thyr_notes = 'Overlapped receptor'
            hi_whol_row = risk_summed.loc[risk_summed[hi_whol].idxmax()]
            if hi_whol_row[2] == 'N':
                whol_notes = ''
            else:
                whol_notes = 'Overlapped receptor'
                
            risks = [
                ['mir', mir_row[4], mir_row[8], mir_row[9], mir_notes] if mir_row[9] > 0
                    else ['mir', '', 0, 0, ''],
                ['respiratory', hi_resp_row[4], hi_resp_row[8], hi_resp_row[10], resp_notes] if hi_resp_row[10] > 0
                    else ['respiratory', '', 0, 0, ''],
                ['liver', hi_live_row[4], hi_live_row[8], hi_live_row[11], live_notes] if hi_live_row[11] > 0
                    else ['liver', '', 0, 0, ''],
                ['neurological', hi_neur_row[4], hi_neur_row[8], hi_neur_row[12], neur_notes] if hi_neur_row[12] > 0
                    else ['neurological', '', 0, 0, ''],
                ['developmental', hi_deve_row[4], hi_deve_row[8], hi_deve_row[13], deve_notes] if hi_deve_row[13] > 0
                    else ['developmental', '', 0, 0, ''],
                ['reproductive', hi_repr_row[4], hi_repr_row[8], hi_repr_row[14], repr_notes] if hi_repr_row[14] > 0
                    else ['reproductive', '', 0, 0, ''],
                ['kidney', hi_kidn_row[4], hi_kidn_row[8], hi_kidn_row[15], kidn_notes] if hi_kidn_row[15] > 0
                    else ['kidney', '', 0, 0, ''],
                ['ocular', hi_ocul_row[4], hi_ocul_row[8], hi_ocul_row[16], ocul_notes] if hi_ocul_row[16] > 0
                    else ['ocular', '', 0, 0, ''],
                ['endocrine', hi_endo_row[4], hi_endo_row[8], hi_endo_row[17], endo_notes] if hi_endo_row[17] > 0
                    else ['endocrine', '', 0, 0, ''],
                ['hematological', hi_hema_row[4], hi_hema_row[8], hi_hema_row[18], hema_notes] if hi_hema_row[18] > 0
                    else ['hematological', '', 0, 0, ''],
                ['immunological', hi_immu_row[4], hi_immu_row[8], hi_immu_row[19], immu_notes] if hi_immu_row[19] > 0
                    else ['immunological', '', 0, 0, ''],
                ['skeletal', hi_skel_row[4], hi_skel_row[8], hi_skel_row[20], skel_notes] if hi_skel_row[20] > 0
                    else ['skeletal', '', 0, 0, ''],
                ['spleen', hi_sple_row[4], hi_sple_row[8], hi_sple_row[21], sple_notes] if hi_sple_row[21] > 0
                    else ['spleen', '', 0, 0, ''],
                ['thyroid', hi_thyr_row[4], hi_thyr_row[8], hi_thyr_row[22], thyr_notes] if hi_thyr_row[22] > 0
                    else ['thyroid', '', 0, 0, ''],
                ['whole body', hi_whol_row[4], hi_whol_row[8], hi_whol_row[23], whol_notes] if hi_whol_row[23] > 0
                    else ['whole body', '', 0, 0, ''],
            ]
            maxrisk_df = pd.DataFrame(risks, columns=[risktype, rec_id, population, risk, notes])
           


        # Put final df into array
        self.dataframe = maxrisk_df
        self.data = self.dataframe.values
        yield self.dataframe

    # Override the default write() method in order to add bottom section of report
    def writeWithTimestamp(self):
        super(MaxRisk, self).writeWithTimestamp()

        faclist = {}
        facilityHeaders = []
        if self.altrec == 'N':
            for index, row in self.dataframe.iterrows():
                if row[risk] > 0:
                    header = 'Facilities impacting ' + row[risktype] + ' Block'
                    facilityHeaders.append(header)
                    faclist[header] = self.getImpactingFacilities(row[fips], row[block])
        else:
            for index, row in self.dataframe.iterrows():
                if row[risk] > 0:
                    header = 'Facilities impacting ' + row[risktype] + ' Receptor ID'
                    facilityHeaders.append(header)
                    faclist[header] = self.getImpactingFacilitiesNonCensus(row[rec_id])
                
        faclistpad = self.pad_dict_list(faclist)
        facilities_df = pd.DataFrame(data=faclistpad, columns=facilityHeaders)            
        self.appendHeaderAtLocation(startingcol=1, headers=facilityHeaders)
        self.appendToFileAtLocation(dataframe=facilities_df, startingcol=1)

    def getImpactingFacilities(self, fipsValue, blockValue):
        impacting = []
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            blockSummaryChronic = BlockSummaryChronic(targetDir=targetDir, facilityId=facilityId, createDataframe=True)
            bsc_df = blockSummaryChronic.createDataframe()
            loc = bsc_df.loc[(bsc_df[fips] == fipsValue) & (bsc_df[block] == blockValue)]
            if loc.size > 0:
                impacting.append(facilityId)

        return impacting


    def getImpactingFacilitiesNonCensus(self, receptorId):
        impacting = []
        for facilityId in self.facilityIds:
            targetDir = self.categoryFolder + "/" + facilityId

            blockSummaryChronic = BlockSummaryChronicNonCensus(targetDir=targetDir, facilityId=facilityId, createDataframe=True)
            bsc_df = blockSummaryChronic.createDataframe()
            loc = bsc_df.loc[bsc_df[rec_id] == receptorId]
            if loc.size > 0:
                impacting.append(facilityId)
            
        return impacting

    def pad_dict_list(self, dict_list):
        lmax = 0
        for lname in dict_list.keys():
            lmax = max(lmax, len(dict_list[lname]))
        for lname in dict_list.keys():
            ll = len(dict_list[lname])
            if  ll < lmax:
                dict_list[lname] += ' ' * (lmax - ll)
        return dict_list