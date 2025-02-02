import os
import json
from src.Monster import Monster
import re

class ToolsMonsterParser:
    def __init__(self, dataPath : str, outputFolder : str) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder
        if not os.path.exists(self.outputFolder):
            os.mkdir(self.outputFolder)
            os.mkdir(os.path.join(self.outputFolder, 'Traits'))

    def generateMonsterList(self) -> None:
        fileList = os.listdir(self.dataPath)
        fileList.sort()
        for file in fileList:
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
                monster = self.sanitizeData(monster)
                try:
                    monsterData = self.adaptToMonster(monster) # type:ignore
                    mon = Monster(data = monsterData, source = monsterData['source'], outputFolder = self.outputFolder)
                except Exception as e:
                    
                    raise e
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

        data['size'] = ','.join([self.parseSize(i) for i in data.get('size', [])])
        data['alias'] = ','.join([i for i in data.get('alias', [])])
        data['type'], data['additionalType'] = self.parseTypes(data.get('type'))
        data['alignment'] = self.parseAlignment(data.get('alignment'))
        data['hp'] = self.parseHP(data.get('hp'))
        data['save'] = self.parseSave(data.get('save'))
        data['resist'] = self.parseConditions(data.get('resist'), 'resist')
        data['conditionImmune'] = self.parseConditions(data.get('conditionImmune'), 'conditionImmune')
        data['immune'] = self.parseConditions(data.get('immune'), 'immune')
        data['vulnerable'] = self.parseConditions(data.get('vulnerable'), 'vulnerable')
        data['cr'], data['lairCr'] = self.parseCR(data.get('cr'))
        data['ac'] = self.parseAC(data.get('ac'))
        data['senses'] = self.parseSenses(data.get('senses'))
        data['speed'] = self.parseSpeed(data.get('speed'))
        data['skill'] = self.parseSkills(data.get('skill'))
        data['languages'] = self.parseLanguages(data.get('languages'))

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


    @classmethod
    def parseTypes(cls, type: str | dict | None) -> tuple[str,str]:
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
                subtype = ','.join([cls.parseSize(i) for i in  type['swarmSize']])
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
    def parseAC(ac: list | None) -> str:
        if ac is None:
            return 'None'
        acStr = ''
        for element in ac:
            if isinstance(element, int):
                acStr += str(element)
                if len(ac) == 1:
                    return acStr 

            if isinstance(element, dict):
                for key, value in element.items():
                    if key == 'ac':
                        acStr += f'{value}'
                    elif isinstance(value, list):
                        acStr += f' {key} {','.join(value)}'
                        acStr.strip()
                    elif isinstance(value, str):
                        acStr += f' {key} {value}'
                        acStr.strip()
                    else:
                        pass

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


    @classmethod
    def parseConditions(cls, conditionList: list | None, conditionName: str) -> str:
        if conditionList is None:
            return 'None'

        conditionStr = ''
        for item in conditionList:
            conditionStr += cls.parseConditionElement(item, conditionName) + ' '

        conditionStr = conditionStr.strip()

        return conditionStr

    @classmethod
    def parseConditionElement(cls, conditionitem, conditionName: str) -> str:

        conditionStr = ''
        if isinstance(conditionitem, str):
            return str(conditionitem)

        if isinstance(conditionitem, dict):
            if conditionitem.get('special'):
                return f'{conditionitem.get('special')}'
            if conditionitem.get('preNote'):
                conditionStr += f'{conditionitem.get('preNote')}'
            conditionStr += ', '.join([cls.parseConditionElement(i, conditionName) for i in conditionitem[conditionName]]) 
            if conditionitem.get('note'):
                conditionStr += f'{conditionitem.get('note')}'
            return conditionStr

        raise TypeError(f'Contition data type not considered ({type(conditionitem)}): {conditionitem}')

    @staticmethod
    def parseCR(cr : str | dict | None) -> tuple[str, str]:
        if cr is None:
            return 'None', 'None'

        if isinstance(cr, str):
            return cr, 'None'

        if isinstance(cr, dict):
            if cr.get('lair'):
                return cr['cr'], cr['lair']
            else:
                return cr['cr'], 'None'


    @staticmethod
    def parseSenses(senses : str | list | None) -> str:
        if senses is None:
            return ''

        if isinstance(senses, str):
            return senses

        if isinstance(senses, list):
            return ', '.join(senses)

        raise TypeError(f'Senses type not considered {type(senses)}: {senses}')


    @staticmethod
    def parseSpeed(speed: dict | str | None) -> str:
        if speed is None:
            return ''
        
        if isinstance(speed, str):
            return speed
        
        speedStr = ''
        if isinstance(speed, dict):
            for key, value in speed.items():
                speedStr += f'{key} {value} ft'
            return speedStr

        raise TypeError(f'Type of speed not considered {type(speed)}: {speed}')


    @staticmethod
    def parseSkills(skills: dict | str | None) -> str:
        if skills is None:
            return ''
        
        if isinstance(skills, str):
            return skills
        
        skillsStr = ''
        if isinstance(skills, dict):
            for key, value in skills.items():
                skillsStr += f'{key} {value} '
            return skillsStr.strip()

        raise TypeError(f'Type of skills not considered {type(skills)}: {skills}')


    @staticmethod
    def parseLanguages(language: list | str | None) -> str:
        if language is None:
            return ''
        
        if isinstance(language, str):
            return language
        
        if isinstance(language, list):
            return ', '.join(language)

        raise TypeError(f'Type of language not considered {type(language)}: {language}')



    @classmethod
    def sanitizeData(cls, data : dict | str)-> dict | str:
        '''
        Removes "{...}" from all the keys of the input dict,
        replacing them with hyperlinks wherever they actually matter.
        This repalcement is done on the `sanitizeString` function
        '''
        if not isinstance(data, dict):
            return cls.sanitizeString(data)

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = cls.sanitizeString(value)
                continue

            if isinstance(value, list):
                data[key] = [cls.sanitizeData(i) for i in value]
                continue

            if isinstance(value, dict):
                data[key] = cls.sanitizeData(value)
                continue

        return data


    @staticmethod
    def sanitizeString(s0: str) -> str:
        if not isinstance(s0, str):
            return s0

        s = s0.replace('ft.', 'ft')

        s = re.sub(r'\{@skill (.+?)\}', r'\1', s)
        s = re.sub(r'\{@dice (.+?)\}', r'\1', s)

        s = re.sub(r'\{@atk mw\}', r'melee weapon attack', s)
        s = re.sub(r'\{@atk rw\}', r'ranged weapon attack', s)
        s = re.sub(r'\{@atk mw,rw\}', r'melee, ranged weapon attack', s)
        s = re.sub(r'\{@atkr m\}', r'melee attack roll', s)
        s = re.sub(r'\{@atkr r\}', r'ranged attack roll', s)
        s = re.sub(r'\{@atkr m,r\}', r'melee,ranged attack roll', s)

        s = re.sub(r'\{@atk ms\}', r'melee spell attack', s)
        s = re.sub(r'\{@atk rs\}', r'ranged spell attack', s)
        s = re.sub(r'\{@atk ms,rs\}', r'melee, ranged spell attack', s)
        


        s = '. '.join(i.strip().capitalize() for i in s.split('. '))

        s = re.sub(r'\{@spell (.+?)\}', r'[[\1]]', s)
        # Items need to be treated differently because they often
        #  come in the form {@item itemName|book|otherName}
        res = re.compile(r'\{@item (.+?)\}').search(s)
        if res:
            itemName = res.group(1).split('|')[0]
            s = re.sub(r'\{@item (.+?)\}', f'[[{itemName}]]', s)

        s = re.sub(r'\{@condition (.+?)\}', r'[[\1]]', s)
        s = re.sub(r'\{@status (.+?)\}', r'[[\1]]', s)

        s = re.sub(r'\{@hit -(\d+?)\}', r'-\1', s)
        s = re.sub(r'\{@hit (\d+?)\}', r'+\1', s)
        s = re.sub(r'\{@h\}', r'*Hit* ', s)
        s = re.sub(r'\{@damage (.+?)\}', r'\1', s)

        s = re.sub(r'\{@dc (\d+?)\}', r'DC\1', s)

        s = re.sub(r'\{@recharge\}', r'(Recharge 6)', s)
        s = re.sub(r'\{@recharge (.+?)\}', r'(Recharge \1)', s)

        s = s.replace('||', '|')

        return s