import os
from src.DataService import DataService


dataFolder = './data'
ds = DataService(dataFolder)

for file in os.listdir(dataFolder):
    if not file.endswith('.xml'):
        continue

    ds.cleanXML(fileName = file)
    