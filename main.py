import os
from src.DataService import DataService
from src.ModeEnum import ModeEnum


dataPath = './data'
outputFolder = './MonsterClean'
ds = DataService(dataPath, outputFolder = outputFolder, mode = ModeEnum.XML)
ds.generateMonsterList()