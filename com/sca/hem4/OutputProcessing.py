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
from com.sca.hem4.writer.excel.AcuteChemicalUnpopulated import AcuteChemicalUnpopulated
from com.sca.hem4.writer.excel.AcuteBreakdown import AcuteBreakdown
from com.sca.hem4.writer.kml.KMLWriter import KMLWriter
from com.sca.hem4.support.UTM import *
from com.sca.hem4.model.Model import *
from com.sca.hem4.writer.excel.FacilityCancerRiskExp import FacilityCancerRiskExp
from com.sca.hem4.writer.excel.FacilityTOSHIExp import FacilityTOSHIExp

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

        self.abort = abort

        self.acute_yn = self.runstream.facoptn_df.iloc[0][acute]
        
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
        
#        # Determine how Aermod was run (with or without deposition)
#        if self.model.facops['dep'] == 'N':
#            # No deposition
#            self.model.model_optns['runtype'] = 0
#        else:
#            if self.model.facops['pdep'] == 'WD':
#                # Wet and dry deposition
#                self.model.model_optns['runtype'] = 1
#            elif self.model.facops['pdep'] == 'DO':
#                # Dry only deposition
#                self.model.model_optns['runtype'] = 2
#            elif self.model.facops['pdep'] == 'WO':
#                # Wet only deposition
#                self.model.model_optns['runtype'] = 3
#            else:
#                self.model.model_optns['runtype'] = 0
#        
#        # Read chronic plotfile and put into a dataframe
#        pfile = open("aermod/plotfile.plt", "r")
#        
#        if runtype == 0:
#            plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
#                names=[utme,utmn,result,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
#                usecols=[0,1,2,3,4,5,6,7,8,9], 
#                converters={utme:np.float64,utmn:np.float64,result:np.float64,elev:np.float64,hill:np.float64
#                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
#                comment='*')
#        elif runtype == 1:
#            plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
#                names=[utme,utmn,result,ddp,wdp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
#                usecols=[0,1,2,3,4,5,6,7,8,9], 
#                converters={utme:np.float64,utmn:np.float64,result:np.float64,ddp:np.float64,wdp:np.float64,elev:np.float64,hill:np.float64
#                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
#                comment='*')
#        elif runtype == 2:
#            plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
#                names=[utme,utmn,result,ddp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
#                usecols=[0,1,2,3,4,5,6,7,8,9], 
#                converters={utme:np.float64,utmn:np.float64,result:np.float64,ddp:np.float64,elev:np.float64,hill:np.float64
#                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
#                comment='*')
#        elif runtype == 3:
#            plot_df = pd.read_table(pfile, delim_whitespace=True, header=None, 
#                names=[utme,utmn,result,wdp,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
#                usecols=[0,1,2,3,4,5,6,7,8,9], 
#                converters={utme:np.float64,utmn:np.float64,result:np.float64,wdp:np.float64,elev:np.float64,hill:np.float64
#                       ,flag:np.float64,avg_time:np.str,source_id:np.str,num_yrs:np.int64,net_id:np.str},
#                comment='*')
            

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return


        #----------- copy input files used to the output directory for posterity --------
        # Note: the copies must be named in a standard way so that they can be found by the
        # summary report which needs them:
        # faclist.xlsx, emisloc.xlsx, hapemis.xlsx
        # TODO

        #----------- create input selection file -----------------
        input_selection = InputSelectionOptions(self.outdir, self.facid, self.model, None)
        input_selection.write()
        Logger.logMessage("Completed InputSelectionOptions output")


        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        
        #----------- create All_Polar_Receptor output file -----------------
        all_polar_receptors = AllPolarReceptors(self.outdir, self.facid, self.model, self.plot_df)
        all_polar_receptors.write()
        self.model.all_polar_receptors_df = all_polar_receptors.dataframe
        Logger.logMessage("Completed AllPolarReceptors output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        # Was this facility run with user receptors only? If so, we need to use the output modules that do not
        # reference census data fields like FIPs and block number.
        ureponly = self.model.urepOnly_optns.get("ureponly", None)
        ureponly_nopop = self.model.urepOnly_optns.get("ureponly_nopop", None)

        #----------- create All_Inner_Receptor output file -----------------
        all_inner_receptors = AllInnerReceptorsNonCensus(self.outdir, self.facid, self.model, self.plot_df) if ureponly \
                        else AllInnerReceptors(self.outdir, self.facid, self.model, self.plot_df)
        all_inner_receptors.write()
        self.model.all_inner_receptors_df = all_inner_receptors.dataframe
        Logger.logMessage("Completed AllInnerReceptors output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create All_Outer_Receptor output file -----------------
        all_outer_receptors = AllOuterReceptorsNonCensus(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn) if ureponly \
                        else AllOuterReceptors(self.outdir, self.facid, self.model, self.plot_df, self.acute_yn)
        all_outer_receptors.write()
        self.model.all_outer_receptors_df = all_outer_receptors.dataframe
        Logger.logMessage("Completed AllOuterReceptors output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return


        #----------- create Ring_Summary_Chronic data -----------------
        ring_summary_chronic = RingSummaryChronic(self.outdir, self.facid, self.model, self.plot_df)
        generator = ring_summary_chronic.generateOutputs()
        for batch in generator:
            ring_summary_chronic_df = ring_summary_chronic.dataframe
        Logger.logMessage("Completed RingSummaryChronic output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        #----------- create Block_Summary_Chronic data -----------------
        block_summary_chronic = BlockSummaryChronicNonCensus(self.outdir, self.facid, self.model, self.plot_df, all_outer_receptors.outerAgg) if ureponly else \
            BlockSummaryChronic(self.outdir, self.facid, self.model, self.plot_df, all_outer_receptors.outerAgg)
        generator = block_summary_chronic.generateOutputs()
        for batch in generator:
            self.model.block_summary_chronic_df = block_summary_chronic.dataframe
        Logger.logMessage("Completed BlockSummaryChronic output")

        if self.abort.is_set():
            Logger.logMessage("Terminating output processing...")
            return

        # Combine ring summary chronic and block summary chronic dfs into one and assign a receptor type
        ring_columns = [lat, lon, mir, hi_resp, hi_live, hi_neur, hi_deve, hi_repr, hi_kidn, hi_ocul, 
                      hi_endo, hi_hema, hi_immu, hi_skel, hi_sple, hi_thyr, hi_whol, overlap]
        block_columns = ring_columns + [rec_type]
        
        ring_risk = ring_summary_chronic_df[ring_columns].copy()
        ring_risk[rec_type] = 'P'
        
        block_risk = self.model.block_summary_chronic_df[block_columns]
        self.model.risk_by_latlon = ring_risk.append(block_risk).reset_index(drop=True).infer_objects()

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

        Logger.logMessage("Finished creating Cancer Risk Exposure for " + self.facid)          
        
        #----------- create Maximum_Individual_Risk output file ---------------
        max_indiv_risk = MaximumIndividualRisksNonCensus(self.outdir, self.facid, self.model, self.plot_df) if ureponly \
                else MaximumIndividualRisks(self.outdir, self.facid, self.model, self.plot_df)
        max_indiv_risk.write()
        self.model.max_indiv_risk_df = max_indiv_risk.dataframe
        Logger.logMessage("Completed MaximumIndividualRisks output")

        #----------- create Maximum_Offsite_Impacts output file ---------------
        inner_recep_risk_df = self.model.block_summary_chronic_df[self.model.block_summary_chronic_df["rec_type"] == "I"]
        max_offsite_impacts = MaximumOffsiteImpactsNonCensus(self.outdir, self.facid, self.model, self.plot_df,
                                                    ring_summary_chronic_df, inner_recep_risk_df) if ureponly else \
            MaximumOffsiteImpacts(self.outdir, self.facid, self.model, self.plot_df, ring_summary_chronic_df, inner_recep_risk_df)
        max_offsite_impacts.write()
        Logger.logMessage("Completed MaximumOffsiteImpacts output")


        # For any rows in ring_summary_chronic and block_summary_chronic where overlap = Y, 
        # replace mir and HI's with values from max_indiv_risk and write data to csv output.
        replacement = self.model.max_indiv_risk_df[value].values
        ringrows = np.where(ring_summary_chronic_df[overlap] == 'Y')[0]
        if len(ringrows) > 0:
            ring_summary_chronic.data[ringrows, 7:22] = replacement
        blockrows = np.where(self.model.block_summary_chronic_df[overlap] == 'Y')[0]
        if len(blockrows) > 0:
            block_summary_chronic.data[blockrows, 10:25] = replacement

        ring_summary_chronic.write()
        block_summary_chronic.write()
        
        
        #----------- create Risk Breakdown output file ------------------------
        risk_breakdown = RiskBreakdown(self.outdir, self.facid, self.model, self.plot_df)
        risk_breakdown.write()
        Logger.logMessage("Completed RiskBreakdown output")


        #----------- create Incidence output file ------------------------
        if not ureponly_nopop:
            outerInc_list = []
            for key in all_outer_receptors.outerInc.keys():
                insert_list = [key[0], key[1], key[2], all_outer_receptors.outerInc[key]]
                outerInc_list.append(insert_list)
            outerInc_df = pd.DataFrame(outerInc_list, columns=[source_id, pollutant, ems_type, inc])
            incidence= Incidence(self.outdir, self.facid, self.model, self.plot_df, outerInc_df)
            incidence.write()
            Logger.logMessage("Completed Incidence output")


        #----------- append to facility max risk output file ------------------

        fac_max_risk = FacilityMaxRiskandHINonCensus(self.model.rootoutput, self.facid, self.model, self.plot_df, incidence.dataframe) if ureponly else \
            FacilityMaxRiskandHI(self.model.rootoutput, self.facid, self.model, self.plot_df, incidence.dataframe)
        fac_max_risk.writeWithoutHeader()

        #----------- append to facility cancer risk exposure output file ------------------
        fac_risk_exp = FacilityCancerRiskExp(self.model.rootoutput, self.facid, self.model, self.plot_df)
        fac_risk_exp.writeWithoutHeader()

        #----------- append to facility TOSHI exposure output file ------------------
        fac_toshi_exp = FacilityTOSHIExp(self.model.rootoutput, self.facid, self.model, self.plot_df)
        fac_toshi_exp.writeWithoutHeader()


        #=================== Acute processing ==============================================
        
        # If acute was run for this facility, read the acute plotfile and create the acute outputs

        if self.acute_yn == 'Y':

            apfile = open("aermod/maxhour.plt", "r")
            aplot_df = pd.read_table(apfile, delim_whitespace=True, header=None, 
                names=[utme,utmn,result,elev,hill,flag,avg_time,source_id,num_yrs,net_id],
                usecols=[0,1,2,3,4,5,6,7,8,9], 
                converters={utme:np.float64,utmn:np.float64,result:np.float64,elev:np.float64,hill:np.float64
                       ,flag:np.float64,avg_time:np.str,source_id:np.str,rank:np.str,net_id:np.str
                       ,concdate:np.str},
                comment='*')
    
            if self.abort.is_set():
                Logger.logMessage("Terminating output processing...")
                return

            #----------- create Acute Chemical Populated output file ------------------------
            acutechempop = AcuteChemicalPopulated(self.outdir, self.facid, self.model, aplot_df)
            acutechempop.write()

            #----------- create Acute Chemical Unpopulated output file ------------------------
            acutechemunpop = AcuteChemicalUnpopulated(self.outdir, self.facid, self.model, aplot_df)
            acutechemunpop.write()

            #----------- create Acute Breakdown output file ------------------------
            acutebkdn = AcuteBreakdown(self.outdir, self.facid, self.model, aplot_df,
                                       acutechempop.dataframe, acutechemunpop.dataframe)
            acutebkdn.write()
            


        #create facility kml
        Logger.logMessage("Writing KML file for " + self.facid)
        kmlWriter = KMLWriter()
        kmlWriter.write_facility_kml(self.facid, self.model.computedValues['cenlat'], 
                                     self.model.computedValues['cenlon'], self.outdir, self.model)

#        return local_vars
    
    
    