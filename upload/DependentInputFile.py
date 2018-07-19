import abc
from upload.InputFile import InputFile


class DependentInputFile(InputFile):
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, dependency):
        self.dependency = dependency
        InputFile.__init__(self, path)


    
        
        
