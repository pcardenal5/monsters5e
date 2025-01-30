from src.ModeEnum import ModeEnum
from src.XmlMonsterParser import XmlMonsterParser

class DataService():
    def __init__(self, dataPath : str, outputFolder : str, mode : ModeEnum) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder
        self.mode = mode

    def generateMonsterList(self) -> None:
        match self.mode:
            case ModeEnum.XML: 
                xmlMonsterParser = XmlMonsterParser(self.dataPath, self.outputFolder)
                xmlMonsterParser.generateMonsterList()
            case ModeEnum.TOOLS:
                pass
            case _:
                raise ValueError('Not supported')