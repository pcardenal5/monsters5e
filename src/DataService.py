import json.decoder
import json.encoder
import os
import json
import xmltodict
from src.Monster import Monster

class DataService():
    def __init__(self, dataPath : str, outputFolder : str) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder

    def generateMonsterList(self, fileName: str) -> None:
        
        # Open xml file and get the monster list
        with open(os.path.join(self.dataPath, fileName), 'r') as inputFile:
            data = xmltodict.parse(inputFile.read())['compendium']['monster']
        
        # Save resulting dict to json for easier navigation
        with open(os.path.join(self.dataPath, fileName.replace('xml', 'json')), 'w') as outputJSON:
            json.dump(data, outputJSON, indent = 4)

        for monster in data:
            mon = Monster(data = monster, source = fileName.replace('.xml', '').replace('Bestiary', ''))
            outputFolder = os.path.join(self.outputFolder, mon.cr)
            if not os.path.exists(outputFolder):
                os.makedirs(outputFolder)

            with open(os.path.join(outputFolder, mon.name.replace('/','-')) + '.md', 'w') as outputFile:
                outputFile.write(mon.generateText())