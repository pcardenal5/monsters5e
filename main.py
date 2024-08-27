import os
from src.DataService import DataService


dataFolder = './data'
outputFolder = './MonsterClean'
ds = DataService(dataFolder, outputFolder = outputFolder)

for file in os.listdir(dataFolder):
    if not file.endswith('.xml'):
        continue

    ds.generateMonsterList(fileName = file)
