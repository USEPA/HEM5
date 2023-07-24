# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 12:43:52 2017

@author: dlindsey
"""
from com.sca.hem4.FacilityPrep import sector, ring
from com.sca.hem4.upload.TargetOrganEndpoints import *
from com.sca.hem4.writer.csv.AllInnerReceptorsNonCensus import AllInnerReceptorsNonCensus
from com.sca.hem4.writer.csv.AllOuterReceptorsNonCensus import AllOuterReceptorsNonCensus
from com.sca.hem4.writer.csv.AllPolarReceptors import *
from com.sca.hem4.writer.csv.BlockSummaryChronicNonCensus import BlockSummaryChronicNonCensus
from com.sca.hem4.writer.csv.RingSummaryChronic import RingSummaryChronic
from com.sca.hem4.writer.csv.BlockSummaryChronic import *
from com.sca.hem4.writer.csv.Temporal import Temporal
from com.sca.hem4.writer.excel.AcuteChemicalMax import AcuteChemicalMax
from com.sca.hem4.writer.excel.AcuteChemicalMaxNonCensus import AcuteChemicalMaxNonCensus
from com.sca.hem4.writer.excel.AcuteChemicalPopulatedNonCensus import AcuteChemicalPopulatedNonCensus
from com.sca.hem4.writer.excel.CancerRiskExposure import CancerRiskExposure
from com.sca.hem4.writer.excel.FacilityMaxRiskandHI import FacilityMaxRiskandHI
from com.sca.hem4.writer.excel.FacilityMaxRiskandHINonCensus import FacilityMaxRiskandHINonCensus
from com.sca.hem4.writer.excel.InputSelectionOptions import InputSelectionOptions
from com.sca.hem4.writer.excel.MaximumIndividualRisks import MaximumIndividualRisks, value
from com.sca.hem4.writer.excel.MaximumIndividualRisksNonCensus import MaximumIndividualRisksNonCensus
from com.sca.hem4.writer.excel.MaximumOffsiteImpacts import MaximumOffsiteImpacts
from com.sca.hem4.writer.excel.MaximumOffsiteImpactsNonCensus import MaximumOffsiteImpactsNonCensus
from com.sca.hem4.writer.excel.NoncancerRiskExposure import NoncancerRiskExposure
from com.sca.hem4.writer.excel.RiskBreakdown import RiskBreakdown
from com.sca.hem4.writer.excel.Incidence import Incidence
from com.sca.hem4.writer.excel.AcuteChemicalPopulated import AcuteChemicalPopulated
from com.sca.hem4.writer.excel.AcuteBreakdown import AcuteBreakdown
from com.sca.hem4.writer.kml.KMLWriter import KMLWriter
from com.sca.hem4.support.UTM import *
from com.sca.hem4.model.Model import *
from com.sca.hem4.writer.excel.FacilityCancerRiskExp import FacilityCancerRiskExp
from com.sca.hem4.writer.excel.FacilityTOSHIExp import FacilityTOSHIExp
import traceback


class Process_outputs():
    
    def __init__(self, outdir, facid, model, prep, runstream, plot_df, abort):
        self.facid = facid
        self.haplib_m = model.haplib.dataframe.values
        self.hapemis = runstream.hapemis
        self.outdir = outdir
        self.model = model
        self.runstream = runstream
        self.plot_df = plot_df
        self.model.numsectors = self.model.polargrid[sector].max()
        self.model.numrings = self.model.polargrid[ring].max()
        self.model.innerblks_df = prep.innerblks
        self.model.outerblks_df = prep.outerblks
        self.model.runstream_hapemis = runstream.hapemis
        self.facops = self.model.facops.loc[self.model.facops.fac_id == facid]
        self.generateOnly = False
        self.abort = abort

        self.acute_yn = self.runstream.facoptn_df.iloc[0][acute]
        self.temporal = self.model.temporal

        # Units conversion factor
        self.cf = 2000*0.4536/3600/8760

        
    def nodivby0(self, n, d):
        quotient = np.zeros(len(n))
        for i in np.arange(len(n)):
            if d[i] != 0:
                quotient[i] = n[i]/d[i]
            else:
                quotient[i] = 0
        return quotient
        

    def process(self):
        
        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return


        #----------- create input selection file -----------------
        input_selection = InputSelectionOptions(self.outdir, self.facid, self.model, None)
        input_selection.write()
        Logger.logMessage("Completed InputSelectionOptions output")


        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create All_Polar_Receptor output file -----------------
        all_polar_receptors = AllPolarReceptors(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn)
        all_polar_receptors.write(generateOnly=False)

        self.model.all_polar_receptors_df = all_polar_receptors.dataframe
        Logger.logMessage("Completed AllPolarReceptors output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        # Was this facility run with alternate receptors? If so, we need to use the output modules that do not
        # reference census data fields like FIPs and block number.
        altrec = self.model.altRec_optns.get("altrec", None)
        altrec_nopop = self.model.altRec_optns.get("altrec_nopop", None)
        
        #----------- create All_Inner_Receptor output file -----------------
        all_inner_receptors = AllInnerReceptorsNonCensus(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn) if altrec \
                        else AllInnerReceptors(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn)
        all_inner_receptors.write(generateOnly=False)
        self.model.all_inner_receptors_df = all_inner_receptors.dataframe
        Logger.logMessage("Completed AllInnerReceptors output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        
        # ----------- create All_Outer_Receptor output file -----------------
        if not self.model.outerblks_df.empty:
            all_outer_receptors = AllOuterReceptorsNonCensus(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn) if altrec \
                            else AllOuterReceptors(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn)
            all_outer_receptors.write(generateOnly=self.generateOnly)
            self.model.all_outer_receptors_df = all_outer_receptors.dataframe
            Logger.logMessage("Completed AllOuterReceptors output")
        else:
            Logger.logMessage("No outer receptors. Did not create AllOuterReceptors output.")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        # ----------- create temporal output file if necessary -----------------
        if self.temporal:
            temporal = Temporal(self.outdir, self.facid, self.model, self.plot_df)
            temporal.write()
            Logger.logMessage("Completed Temporal output")


        #----------- create Ring_Summary_Chronic data -----------------
        ring_summary_chronic = RingSummaryChronic(self.outdir, self.facid, self.model, self.plot_df)
        generator = ring_summary_chronic.generateOutputs()

        # Store in a temporary DF because the ring summary chronic may need to change if there are overlaps
        for batch in generator:
            temp_rsc_df = ring_summary_chronic.dataframe

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        
        #----------- create Block_Summary_Chronic data -----------------
        if not self.model.outerblks_df.empty:
            block_summary_chronic = BlockSummaryChronicNonCensus(targetDir=self.outdir, facilityId=self.facid,
                     model=self.model, plot_df=self.plot_df, outerAgg=all_outer_receptors.outerAgg) if altrec else \
                BlockSummaryChronic(self.outdir, self.facid, self.model, self.plot_df, all_outer_receptors.outerAgg)
        else:
            block_summary_chronic = BlockSummaryChronicNonCensus(targetDir=self.outdir, facilityId=self.facid,
                     model=self.model, plot_df=self.plot_df) if altrec else \
                BlockSummaryChronic(self.outdir, self.facid, self.model, self.plot_df)
        
        # Store in a temporary DF because the block summary chronic may need to change if there are overlaps
        generator = block_summary_chronic.generateOutputs()
        for batch in generator:
            temp_bsc_df = block_summary_chronic.dataframe

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        
        
        # Construct a DF of total risk by lat and lon for all receptors. Do this by combining the block summary 
        # chronic and ring summary chronic DFs into one DF.
        
        # First, organize the ring summary chronic DF
        ring_columns = [lat, lon, mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, 
                      hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol, overlap]
        ring_risk = temp_rsc_df[ring_columns].copy()
        ring_risk[rec_type] = 'PG'
        ring_risk['blk_type'] = 'PG'

        # Second, define the columns that are needed. Block and populatoin is needed to determine the mir.
        if not altrec:
            # census data used
            block_columns = ring_columns + [rec_type, 'blk_type', block, population]
            ring_risk[block] = ''
            ring_risk[population] = 0
        else:
            # alternate receptors used
            block_columns = ring_columns + [rec_type, 'blk_type', rec_id]
            ring_risk[rec_id] = ''
            
        # Subset the block summary chronic DF to needed columns
        block_risk = temp_bsc_df[block_columns]
        
        # Now create DF of risk by lat and lon for all receptors
        self.model.risk_by_latlon = (pd.concat([ring_risk, block_risk])
                                     .reset_index(drop=True).infer_objects())

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

       
        #----------- create Maximum_Individual_Risk output file ---------------
        max_indiv_risk = MaximumIndividualRisksNonCensus(self.outdir, self.facid, self.model, self.plot_df) if altrec \
                else MaximumIndividualRisks(self.outdir, self.facid, self.model, self.plot_df)
        max_indiv_risk.write()
        self.model.max_indiv_risk_df = max_indiv_risk.dataframe
        Logger.logMessage("Completed MaximumIndividualRisks output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return
        
        #----------- create Maximum_Offsite_Impacts output file ---------------
        inner_recep_risk_df = temp_bsc_df[temp_bsc_df["blk_type"] == "D"]
        max_offsite_impacts = MaximumOffsiteImpactsNonCensus(self.outdir, self.facid, self.model, self.plot_df,
                                                    temp_rsc_df, inner_recep_risk_df) if altrec else \
                            MaximumOffsiteImpacts(self.outdir, self.facid, self.model, self.plot_df, 
                                                  temp_rsc_df, inner_recep_risk_df)
        max_offsite_impacts.write()
        Logger.logMessage("Completed MaximumOffsiteImpacts output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #---------------------------------------------------------------------------------
        # For any rows in ring_summary_chronic and block_summary_chronic where overlap = Y, 
        # replace mir and HI's with values from max_indiv_risk and write data to csv output.
        replacement = self.model.max_indiv_risk_df[value].values
        
        ringrows = np.where(temp_rsc_df[overlap] == 'Y')[0]
        if len(ringrows) == 0:
            # No overlaps
            ring_summary_chronic_df = temp_rsc_df
            ring_summary_chronic.write()
        else:
            # Some overlaps
            temp_rsc_df.iloc[ringrows, 7:22] = replacement
            ring_summary_chronic_df = temp_rsc_df
            ring_summary_chronic.write(False, ring_summary_chronic_df)
        Logger.logMessage("Completed RingSummaryChronic output")
            
        blockrows = np.where(temp_bsc_df[overlap] == 'Y')[0]
        if len(blockrows) == 0:
            # No overlaps
            self.model.block_summary_chronic_df = temp_bsc_df
            block_summary_chronic.write()
        else:
            temp_bsc_df.iloc[blockrows, 10:25] = replacement
            self.model.block_summary_chronic_df = temp_bsc_df
            block_summary_chronic.write(False, self.model.block_summary_chronic_df)
        Logger.logMessage("Completed BlockSummaryChronic output")


        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create noncancer risk exposure output file -----------------
        noncancer_risk_exposure = NoncancerRiskExposure(self.outdir, self.facid, self.model, self.plot_df, self.model.block_summary_chronic_df)
        noncancer_risk_exposure.write()
        Logger.logMessage("Completed NoncancerRiskExposure output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create cancer risk exposure output file -----------------
        cancer_risk_exposure = CancerRiskExposure(self.outdir, self.facid, self.model, self.plot_df, self.model.block_summary_chronic_df)
        cancer_risk_exposure.write()
        Logger.logMessage("Completed CancerRiskExposure output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return
        
        
        #----------- create Risk Breakdown output file ------------------------
        risk_breakdown = RiskBreakdown(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn)
        risk_breakdown.write()
        Logger.logMessage("Completed RiskBreakdown output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create Incidence output file ------------------------
        if not altrec_nopop:
            if not self.model.outerblks_df.empty:
                outerInc_list = []
                for key in all_outer_receptors.outerInc.keys():
                    insert_list = [key[0], key[1], key[2], all_outer_receptors.outerInc[key]]
                    outerInc_list.append(insert_list)
                outerInc_df = pd.DataFrame(outerInc_list, columns=[source_id, pollutant, emis_type, inc])
                incidence= Incidence(self.outdir, self.facid, self.model, self.plot_df, outerInc_df)
            else:
                incidence= Incidence(self.outdir, self.facid, self.model, self.plot_df)
                
            incidence.write()
            Logger.logMessage("Completed Incidence output")


        #----------- append to facility max risk output file ------------------
        fac_max_risk = FacilityMaxRiskandHINonCensus(self.model.rootoutput, self.facid, self.model, self.plot_df, incidence.dataframe) if altrec else \
            FacilityMaxRiskandHI(targetDir=self.model.rootoutput, facilityId=self.facid, model=self.model,
                                 plot_df=self.plot_df, incidence=incidence.dataframe)

        fac_max_risk.writeWithoutHeader()

        #----------- append to facility cancer risk exposure output file ------------------
        fac_risk_exp = FacilityCancerRiskExp(self.model.rootoutput, self.facid, self.model, self.plot_df)
        fac_risk_exp.writeWithoutHeader()

        #----------- append to facility TOSHI exposure output file ------------------
        fac_toshi_exp = FacilityTOSHIExp(self.model.rootoutput, self.facid, self.model, self.plot_df)
        fac_toshi_exp.writeWithoutHeader()

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #=================== Acute processing ==============================================
        
        # If acute was run for this facility, read the acute plotfile and create the acute outputs
        
        if self.acute_yn == 'Y':
                
            if self.abort.is_set():
                Logger.logMessage("Terminating output processing...")
                return

            #----------- create Acute Chemical Populated output file ------------------------
            acutechempop = AcuteChemicalPopulatedNonCensus(self.outdir, self.facid, self.model, self.model.acuteplot_df) if altrec \
                 else AcuteChemicalPopulated(self.outdir, self.facid, self.model, self.model.acuteplot_df)
            acutechempop.write()
            Logger.logMessage("Completed Acute Chemical Populated output")

            #----------- create Acute Chemical Max output file ------------------------
            acutechemmax = AcuteChemicalMaxNonCensus(self.outdir, self.facid, self.model, self.model.acuteplot_df) if altrec \
                 else AcuteChemicalMax(self.outdir, self.facid, self.model, self.model.acuteplot_df)
            acutechemmax.write()
            Logger.logMessage("Completed Acute Chemical Max output")


            #----------- create Acute Breakdown output file ------------------------
            acutebkdn = AcuteBreakdown(self.outdir, self.facid, self.model, self.model.acuteplot_df, None, False,
                                       acutechempop.dataframe, acutechemmax.dataframe)
            acutebkdn.write()
            Logger.logMessage("Completed Acute Breakdown output")
            


        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return


        #create facility kml
        kmlWriter = KMLWriter()

        try:
                
            if not altrec:
                kmlWriter.write_facility_kml(self.facid, self.model.computedValues['cenlat'], 
                                             self.model.computedValues['cenlon'], self.outdir, self.model)
            else:
                kmlWriter.write_facility_kml_NonCensus(self.facid, self.model.computedValues['cenlat'], 
                                         self.model.computedValues['cenlon'], self.outdir, self.model)

        except BaseException as e:
        
#            exc_type, exc_obj, exc_tb = sys.exc_info()
            var = traceback.format_exc()
            Logger.logMessage(var)

        Logger.logMessage("Completed creating KMZ file for " + self.facid)

#        return local_vars

    