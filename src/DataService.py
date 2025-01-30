from src.ModeEnum import ModeEnum
from src.XmlMonsterParser import XmlMonsterParser
from src.ToolsMonsterParser import ToolsMonsterParser

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
                    
                toolsMonsterParser = ToolsMonsterParser(self.dataPath, self.outputFolder)
                toolsMonsterParser.generateMonsterList()
            case _:
                raise ValueError('Not supported')