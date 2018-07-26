from abc import abstractmethod, ABC


class Writer(ABC):

    def __init__(self):
        self.outputs = None
        self.filename = None
        self.headers = None
        self.data = None

    def write(self):

        self.calculateOutputs()

        if self.headers is not None and self.data is not None:
            self.writeToFile()
        else:
            raise RuntimeError("Headers and data must be present to write file.")

    @abstractmethod
    def calculateOutputs(self):
        pass

    @abstractmethod
    def writeToFile(self):
        pass