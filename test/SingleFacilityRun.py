import hashlib
import os
import shutil
import unittest
import pandas as pd
from test.TestHarness import TestHarness
from writer.csv.AllInnerReceptors import AllInnerReceptors
from writer.csv.AllPolarReceptors import AllPolarReceptors
from writer.csv.BlockSummaryChronic import BlockSummaryChronic
from writer.csv.RingSummaryChronic import RingSummaryChronic

fixturePresent = {}

class SingleFacilityRun(unittest.TestCase):
    """
    Process the facility and test the consistency of the various output files etc.
    """

    @classmethod
    def setUpClass(cls):

        # Remove all facility folders from the output directory before beginning
        folder = "output"
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        # Create the test harness, process the files, etc.
        cls.testHarness = TestHarness(False)
        if not cls.testHarness.success:
            raise RuntimeError("something went wrong creating the test harness")

        cls.outputFixturePrefix = "fixtures/output/"

    def test_all_polar_receptors(self):
        """
        Verify that the all polar receptors output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = AllPolarReceptors("fixtures/output/", facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = AllPolarReceptors("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                 "The contents of the AllPolarReceptors output file are inconsistent with the test fixture:" +
                 checksum_expected + " != " + checksum_generated)

    def test_all_inner_receptors(self):
        """
        Verify that the all inner receptors output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = AllInnerReceptors(self.outputFixturePrefix, facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = AllInnerReceptors("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                             "The contents of the output file are inconsistent with the test fixture:" +
                             checksum_expected + " != " + checksum_generated)

    def test_all_outer_receptors(self):
        """
        Verify that the all outer receptors output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:

            fixture = pd.read_csv(self.outputFixturePrefix + facid + "_all_outer_receptors.csv")
            produced = pd.read_csv("output/" + facid + "/" + facid + "_all_outer_receptors.csv")

            # difference = fixture[fixture!=produced]
            # print(difference)
            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def test_ring_summary_chronic(self):
        """
        Verify that the ring summary chronic output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = RingSummaryChronic("fixtures/output/", facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = RingSummaryChronic("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                             "The contents of the output file are inconsistent with the test fixture:" +
                             checksum_expected + " != " + checksum_generated)

    def test_block_summary_chronic(self):
        """
        Verify that the block summary chronic output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = BlockSummaryChronic(self.outputFixturePrefix, facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = BlockSummaryChronic("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                             "The contents of the output file are inconsistent with the test fixture:" +
                             checksum_expected + " != " + checksum_generated)

    def test_cancer_risk_exposure(self):
        """
        Verify that the cancer risk exposure output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = pd.read_excel("fixtures/output/" + facid + "_cancer_risk_exposure.xlsx")
            produced = pd.read_excel("output/" + facid + "/" + facid + "_cancer_risk_exposure.xlsx")

            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def test_noncancer_risk_exposure(self):
        """
        Verify that the noncancer risk exposure output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = pd.read_excel("fixtures/output/" + facid + "_noncancer_risk_exposure.xlsx")
            produced = pd.read_excel("output/" + facid + "/" + facid + "_noncancer_risk_exposure.xlsx")

            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def test_max_indiv_risks(self):
        """
        Verify that the maximum individual risks output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = pd.read_excel(self.outputFixturePrefix + facid + "_maximum_indiv_risks.xlsx")
            produced = pd.read_excel("output/" + facid + "/" + facid + "_maximum_indiv_risks.xlsx")

            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def test_incidence(self):
        """
        Verify that the incidence output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = pd.read_excel("fixtures/output/" + facid + "_incidence.xlsx")
            produced = pd.read_excel("output/" + facid + "/" + facid + "_incidence.xlsx")

            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def test_risk_breakdown(self):
        """
        Verify that the risk breakdown output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = pd.read_excel("fixtures/output/" + facid + "_risk_breakdown.xlsx")
            produced = pd.read_excel("output/" + facid + "/" + facid + "_risk_breakdown.xlsx")

            self.assertTrue(fixture.equals(produced), "The contents of the output file are inconsistent with the test fixture.")

    def hashFile(self, filename):
        """
        Calculate the md5 checksum for a given file and return the result.
        """

        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(filename, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

if __name__ == '__main__':
    unittest.main()
