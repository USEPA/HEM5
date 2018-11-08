from threading import Event

from Processor import Processor
from log import Logger
from model.Model import Model
from upload.FileUploader import FileUploader


class TestHarness:
    """
    A class that simulates the GUI by setting up a model, uploading library
    files, and processing hard-coded inputs in the context of a unit test.
    """
    def __init__(self):
        self.success = False

        self.model = Model()
        uploader = FileUploader(self.model)

        # set up the test fixture files...
        uploader.uploadLibrary("haplib")
        uploader.uploadLibrary("organs")
        uploader.uploadLibrary("gas params")

        uploader.upload("faclist", "fixtures/input/faclist.xlsx")
        self.model.facids = self.model.faclist.dataframe["fac_id"]
        uploader.upload("hapemis", "fixtures/input/hapemis.xlsx")
        uploader.upload("emisloc", "fixtures/input/emisloc.xlsx")
        uploader.uploadDependent("user receptors", "fixtures/input/urec.xlsx",
                                 self.model.faclist.dataframe)

        processor = Processor(self.model, Event())
        self.success = processor.process()
        Logger.close(True)