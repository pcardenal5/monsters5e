from src.DataService import DataService
from src.ModeEnum import ModeEnum


dataPath = './5etools-v2.5.12/data/bestiary'
outputFolder = './5etools'
ds = DataService(dataPath, outputFolder = outputFolder, mode = ModeEnum.TOOLS)
ds.generateMonsterList()