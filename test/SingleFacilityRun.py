import glob
import hashlib
import os
import shutil
import unittest

from test.TestHarness import TestHarness
from writer.csv.AllInnerReceptors import AllInnerReceptors
from writer.csv.AllOuterReceptors import AllOuterReceptors
from writer.csv.AllPolarReceptors import AllPolarReceptors
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
        cls.testHarness = TestHarness()
        if not cls.testHarness.success:
            raise RuntimeError("something went wrong creating the test harness")

    def test_all_polar_receptors(self):
        """
        Verify that the all polar receptors output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = AllPolarReceptors("fixtures/output", facid, None, None)
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
            fixture = AllInnerReceptors("fixtures/output", facid, None, None)
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
            fixture = AllOuterReceptors("fixtures/output", facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = AllOuterReceptors("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                             "The contents of the output file are inconsistent with the test fixture:" +
                             checksum_expected + " != " + checksum_generated)

    def test_ring_summary_chronic(self):
        """
        Verify that the ring summary chronic output file is identical to the test fixture.
        """
        for facid in self.testHarness.model.facids:
            fixture = RingSummaryChronic("fixtures/output", facid, None, None)
            checksum_expected = self.hashFile(fixture.filename)

            generated = RingSummaryChronic("output/"+facid, facid, None, None)
            checksum_generated = self.hashFile(generated.filename)
            self.assertEqual(checksum_expected, checksum_generated,
                             "The contents of the output file are inconsistent with the test fixture:" +
                             checksum_expected + " != " + checksum_generated)

    def test_aermod(self):
        """
        The aermod output files should be identical, except for the timestamp!
        """

        for facid in self.testHarness.model.facids:
            checksum_expected = self.hashFile("fixtures/output/aermod.out")
            checksum_generated = self.hashFile("output/" + facid + "/aermod.out")
            self.assertNotEqual(checksum_expected, checksum_generated,
                 "The contents of the aermod output file should have a different date than the test fixture:" +
                 checksum_expected + " != " + checksum_generated)

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
