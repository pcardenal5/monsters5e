import os
import json
from src.Monster import Monster

class ToolsMonsterParser:
    def __init__(self, dataPath : str, outputFolder : str) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder

    def generateMonsterList(self) -> None:
        for file in os.listdir(self.dataPath):
            if not file.startswith('bestiary'):
                continue
            print(file)
            # Open xml file and get the monster list
            with open(os.path.join(self.dataPath, file), 'r') as inputFile:
                data : list[dict]= json.load(inputFile)['monster']

            for monster in data:
                # Skip monsters that are copies of other creatures
                # TODO: consider "Edge" case 
                if monster.get('_copy') is not None:
                    continue
                monsterData = self.adaptToMonster(monster)

                mon = Monster(data = monsterData, source = monsterData['source'])

                outputFolder = os.path.join(self.outputFolder, mon.cr.replace('/', '-').replace('l','1').replace('00','0'))
                if not os.path.exists(outputFolder):
                    os.makedirs(outputFolder)

                with open(os.path.join(outputFolder, mon.name) + '.md', 'w') as outputFile:
                    outputFile.write(mon.generateText())


    def adaptToMonster(self, data: dict)-> dict:
        # Here we adapt the data from the json to the 
        # format the Monster class expects
        # Thus, we only change the values that actually
        # need to change

        data['size'] = [self.parseSize(i) for i in data.get('size', [])]
        data['type'], data['additionalType'] = self.parseTypes(data.get('type'))
        data['alignment'] = self.parseAlignment(data.get('alignment'))
        data['hp'] = self.parseHP(data.get('hp'))
        data['save'] = self.parseSave(data.get('save'))
        data['resist'] = self.parseConditions(data.get('resist'), 'resist')
        data['conditionImmune'] = self.parseConditions(data.get('conditionImmune'), 'conditionImmune')
        data['immune'] = self.parseConditions(data.get('immune'), 'immune')
        data['vulnerable'] = self.parseConditions(data.get('vulnerable'), 'vulnerable')
        data['cr'], data['lairCr'] = self.parseCR(data.get('cr'))

        return data


    @staticmethod
    def parseSize(size: list|None) -> str:
        if size is None:
            return 'None'
        if len(size) > 1:
            raise ValueError(f'Size List too long: {size}')
        match size[0]:
            case None:
                return 'None'
            case 'T':
                return 'Tiny'
            case 'S':
                return 'Small'
            case 'M':
                return 'Medium'
            case 'L':
                return 'Large'
            case 'H':
                return 'Huge'
            case 'G':
                return 'Gargantuan'
            case _:
                raise LookupError(f'Size not supported: {size}')


    def parseTypes(self, type: str | dict | None) -> tuple[str,str]:
        if type is None:
            return 'None', 'None'

        subtype = 'None'
        if isinstance(type, str):
            return type, subtype
        if isinstance(type, dict):
            if type.get('tags') is not None:
                tags = type['tags']
                for tag in tags:
                    if isinstance(tag, str):
                        subtype = tag
                    elif isinstance(tag, list):
                        subtype = ', '.join(tag)
                    elif isinstance(tag, dict):            
                        subtype = f'{tag.get('prefix')} {tag.get('tag')}'.strip()
                    else:
                        subtype = ''
                        raise ValueError(f'Type tags has not been considered: {tag}')
            elif type.get('swarmSize') is not None:
                subtype = ','.join([self.parseSize(i) for i in  type['swarmSize']])
            else:
                subtype = 'None'


            return type['type'], subtype


    @staticmethod
    def parseAlignment(alignment: list[str]| None) -> str:
        # TODO: See what 5e.tools is actually doing to set the alignmnet
        if alignment is None:
            return 'None'
        match alignment[0]:
            case 'NX':
                return 'Any non legal alignment'
            case 'A':
                alignment1 = 'Any'
            case 'L':
                alignment1 = 'Legal'
            case 'N':
                alignment1 = 'Neutral'
            case 'C':
                alignment1 = 'Chaotic'
            case _:
                alignment1 = 'Unknown'

        if len(alignment) == 1:
            return alignment1

        match alignment[1]:
            case 'G':
                alignment2 = 'Good'
            case 'N':
                alignment2 = 'Neutral'
            case 'E':
                alignment2 = 'Evil'
            case _:
                alignment2 = 'Unknown'

        return alignment1 + ' ' + alignment2 


    @staticmethod
    def parseAC(ac: list) -> str:
        acStr = ''
        if isinstance(ac[0], int):
            acStr += str(ac[0])
            if len(ac) == 1:
                return acStr 
            ac = ac[1:]

        if isinstance(ac[0], dict):
            acStr += f'{ac[0]['ac']} {','.join(ac[0]['from'])}'


        return acStr


    @staticmethod
    def parseHP(hp: dict | None) -> str:
        if hp is None:
            return 'None'
        if hp.get('special'):
            return hp['special']
        return f'{hp['average']} ({hp['formula']})'


    @staticmethod
    def parseSave(save: dict[str, str] | None) -> str:
        if save is None:
            return 'None'

        return ', '.join([f'{key}, {value}' for key, value in save.items()])


    @staticmethod
    def parseConditions(conditionList: list | None, conditionName: str):
        if conditionList is None:
            return 'None'

        resistStr = ''
        for item in conditionList:
            if isinstance(item, str):
                resistStr += item
                continue

            if isinstance(item, dict):
                if item.get('preNote'):
                    resistStr += f'{item.get('preNote')}'
                resistStr += ', '.join([i.title() for i in item[conditionName]]) # TODO: Add recursivity
                if item.get('note'):
                    resistStr += f'{item.get('note')}'
                
                continue

        return resistStr


    @staticmethod
    def parseCR(cr : str | dict | None) -> tuple[str, str]:
        if cr is None:
            return 'None', 'None'

        if isinstance(cr, str):
            return 'cr', 'None'

        if isinstance(cr, dict):
            return cr['cr'], cr['lair']