import queue
import sys
import traceback
import unittest
from Hem4Gui_Threaded import Hem4

class SingleFacilityRun(unittest.TestCase):

    def setUp(self):
        messageQueue = queue.Queue()
        self.hem4 = Hem4(messageQueue)

        # set up the test fixture files...
        self.hem4.uploader.uploadLibrary("haplib")
        self.hem4.uploader.uploadLibrary("organs")

        self.hem4.uploader.upload("faclist", "fixtures/faclist.xlsx")
        self.hem4.model.facids = self.hem4.model.faclist.dataframe['fac_id']
        self.hem4.uploader.upload("hapemis", "fixtures/hapemis.xlsx")
        self.hem4.uploader.upload("emisloc", "fixtures/emisloc.xlsx")
        self.hem4.uploader.uploadDependent("user receptors", "fixtures/urec.xlsx",
                                      self.hem4.model.faclist.dataframe)

    def tearDown(self):
        self.hem4.close()

    def test_hem4(self):

        self.hem4.process()

        # assert various stuff
        ex = self.hem4.lastException
        self.assertEqual(ex, None, "The last exception was not None")

if __name__ == '__main__':
    unittest.main()
