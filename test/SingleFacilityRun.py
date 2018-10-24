import hashlib
import queue
import unittest

from Hem4Gui_Threaded import Hem4
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
        messageQueue = queue.Queue()
        callbackQueue = queue.Queue()
        cls.hem4 = Hem4(messageQueue, callbackQueue)

        # set up the test fixture files...
        cls.hem4.uploader.uploadLibrary("haplib")
        cls.hem4.uploader.uploadLibrary("organs")

        cls.hem4.uploader.upload("faclist", "fixtures/input/faclist.xlsx")
        cls.hem4.model.facids = cls.hem4.model.faclist.dataframe["fac_id"]
        cls.hem4.uploader.upload("hapemis", "fixtures/input/hapemis.xlsx")
        cls.hem4.uploader.upload("emisloc", "fixtures/input/emisloc.xlsx")
        cls.hem4.uploader.uploadDependent("user receptors", "fixtures/input/urec.xlsx",
                                      cls.hem4.model.faclist.dataframe)

        cls.hem4.process()

    @classmethod
    def tearDownClass(cls):
        cls.hem4.close()

    def test_all_polar_receptors(self):
        """
        Verify that the all polar receptors output file is identical to the test fixture.
        """
        for facid in self.hem4.model.facids:
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
        for facid in self.hem4.model.facids:
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
        for facid in self.hem4.model.facids:
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
        for facid in self.hem4.model.facids:
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

        for facid in self.hem4.model.facids:
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
