import os
import json
import xmltodict
from src.Monster import Monster

class XmlMonsterParser:
    def __init__(self, dataPath : str, outputFolder : str) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder


    def generateMonsterList(self) -> None:

        for file in os.listdir(self.dataPath):
            if not file.endswith('.xml'):
                continue

            # Open xml file and get the monster list
            with open(os.path.join(self.dataPath, file), 'r') as inputFile:
                data = xmltodict.parse(inputFile.read())['compendium']['monster']

            # Save resulting dict to json for easier navigation
            with open(os.path.join(self.dataPath, file.replace('xml', 'json')), 'w') as outputJSON:
                json.dump(data, outputJSON, indent = 4)

            for monster in data:
                monster = {key:val for key, val in monster.items() if val is not None}
                mon = Monster(data = monster, source = file.replace('.xml', '').replace('Bestiary', ''), outputFolder = self.outputFolder)
                outputFolder = os.path.join(self.outputFolder, mon.cr.replace('/', '-').replace('l','1').replace('00','0'))
                if not os.path.exists(outputFolder):
                    os.makedirs(outputFolder)

                with open(os.path.join(outputFolder, mon.name) + '.md', 'w') as outputFile:
                    outputFile.write(mon.generateText())