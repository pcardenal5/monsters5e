import os
import json
import sys
sys.path.append('.')
from src.Monster import Monster
from src.LegendaryGroup import LegendaryGroup
import re
from tqdm import tqdm

class ToolsMonsterParser:
    def __init__(self, dataPath : str, outputFolder : str) -> None:
        self.dataPath = dataPath
        self.outputFolder = outputFolder
        if not os.path.exists(self.outputFolder):
            os.mkdir(self.outputFolder)
            os.mkdir(os.path.join(self.outputFolder, 'Traits'))

    def generateMonsterList(self) -> None:
        fileList = os.listdir(self.dataPath)
        for file in tqdm(fileList):
            if file.startswith('bestiary'):
                self.readMonsterData(file)
            elif file.startswith('legendarygroups'):
                self.readLegendaryGroupData(file)


    def readMonsterData(self, file : str):
        # Open json file and get the monster list
        with open(os.path.join(self.dataPath, file), 'r') as inputFile:
            data : list[dict]= json.load(inputFile)['monster']

        for monster in data:
            # Skip monsters that are copies of other creatures
            # TODO: consider "Edge" case 
            if monster.get('_copy') is not None:
                continue
            monsterData = self.adaptToMonster(self.sanitizeData(monster)) # type:ignore
            mon = Monster(data = monsterData, source = monsterData['source'], outputFolder = self.outputFolder)

            # Monster name is NOT unique across monster manuals, first check if it exists
            if os.path.exists(mon.completeOutputPath):
                mon.completeOutputPath = mon.completeOutputPath.replace('.md', f'_{mon.source}.md')

            with open(mon.completeOutputPath, 'w') as outputFile:
                outputFile.write(mon.generateText())


    def readLegendaryGroupData(self, file : str): 

        with open(os.path.join(self.dataPath, file), 'r') as inputFile:
            data : list[dict]= json.load(inputFile)['legendaryGroup']

        for legendaryGroup in data:
            if legendaryGroup.get('_copy') is not None:
                continue
            legendaryGroupData = self.adaptToLegendaryGroup(self.sanitizeData(legendaryGroup))# type:ignore
            lg = LegendaryGroup(data = legendaryGroupData, source = legendaryGroupData['source'], outputFolder = self.outputFolder)

            # Monster name is NOT unique across monster manuals, first check if it exists
            if os.path.exists(lg.completeOutputPath):
                lg.completeOutputPath = lg.completeOutputPath.replace('.md', f'_{lg.source}.md')

            with open(lg.completeOutputPath, 'w') as outputFile:
                outputFile.write(lg.generateText())




    def adaptToMonster(self, data: dict)-> dict:
        # Here we adapt the data from the json to the 
        # format the Monster class expects
        # Thus, we only change the values that actually
        # need to change

        if data['name'].lower().__contains__('adult gold') and data['name'].lower().endswith('dragon'):
            pass
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
        data['trait'] = self.parseTraits(data)

        return data


    def adaptToLegendaryGroup(self, data : dict) -> dict:
        data['lairActions'] = self.parseLairActions(data, legendaryType = 'lairActions')
        data['regionalEffects'] = self.parseLairActions(data, legendaryType = 'regionalEffects')
        data['mythicEncounter'] = data.get('mythicEncounter', '')

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
            return f'"[[{type}]]"', subtype
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


            return f'"[[{type['type']}]]"', subtype


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
        conditionStr = ', '.join(cls.parseConditionElement(item, conditionName) for item in conditionList)
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
        
        if isinstance(speed, dict):
            return ', '.join(f'{key} {value} ft' for key, value in speed.items())

        raise TypeError(f'Type of speed not considered {type(speed)}: {speed}')


    @staticmethod
    def parseSkills(skills: dict | str | None) -> str:
        if skills is None:
            return ''
        
        if isinstance(skills, str):
            return skills
        
        if isinstance(skills, dict):
            return ', '.join(f'{key} {value}' for key, value in skills.items())

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


    @classmethod
    def sanitizeString(cls, s0: str) -> str:
        if not isinstance(s0, str):
            return s0

        s = s0.replace('ft.', 'ft')
        s = s.replace('[Area of Effect]', '(Area of Effect)')

        s = re.sub(r'\{@skill (.+?)\}', r'\1', s)
        s = re.sub(r'\{@dice (.+?)\}', r'\1', s)

        s = re.sub(r'\{@atk mw\}', r'melee weapon attack', s)
        s = re.sub(r'\{@atk m\}', r'melee weapon attack', s)
        s = re.sub(r'\{@atk rw\}', r'ranged weapon attack', s)
        s = re.sub(r'\{@atk mw,rw\}', r'melee, ranged weapon attack', s)
        s = re.sub(r'\{@atkr m\}', r'melee attack roll', s)
        s = re.sub(r'\{@atkr r\}', r'ranged attack roll', s)
        s = re.sub(r'\{@atkr m,r\}', r'melee,ranged attack roll', s)

        s = re.sub(r'\{@atk ms\}', r'melee spell attack', s)
        s = re.sub(r'\{@atk rs\}', r'ranged spell attack', s)
        s = re.sub(r'\{@atk ms,rs\}', r'melee, ranged spell attack', s)
        
        s = re.sub(r'\{@actSaveFail\}', r'on a failure', s)
        s = re.sub(r'\{@actsavefail\}', r'on a failure', s)
        s = re.sub(re.escape('{@actsavesuccess}'), r'on a success', s)
        s = re.sub(r'\{@actsave(.+?)\}', r'\1 saving throw', s)
        s = re.sub(r'\{@actSave(.+?)\}', r'\1 saving throw', s)

        s = re.sub(r'\{@disease (.+?)\}', r'\1', s)
        s = re.sub(r'\{@hazard (.+?)\}', r'\1', s)

        s = re.sub(r'\{@note (.+?)\}', r'(\1)', s)
        s = re.sub(r'\{@hitYourSpellAttack(.+?)\}', r'your spell attack modifier', s)

        s = re.sub(r'\{@skillCheck([\w\s]+?)(\d+?)\}', r'\2', s)

        s = '. '.join(i.strip().capitalize() for i in s.split('. '))

        # Items need to be treated differently because they often
        #  come in the form {@item itemName|book|otherName}
        s = cls.getLink(s, r'\{@spell (.+?)\}' )
        s = cls.getLink(s, r'\{@item (.+?)\}')
        s = cls.getLink(s, r'\{@creature (.+?)\}')
        s = cls.getLink(s, r'\{@filter (.+?)\}')
        s = cls.getLink(s, r'\{@status (.+?)\}')
        s = cls.getLink(s, r'\{@variantrule (.+?)\}')   
        s = cls.getLink(s, r'\{@condition (.+?)\}')
        s = cls.getLink(s, r'\{@deity (.+?)\}',)
        s = cls.getLink(s, r'\{@table (.+?)\}')

        s = re.sub(r'\{@b (.+?)}', r'**\1**', s)
        s = re.sub(r'\{@i (.+?)\}', r'_\1_', s)        


        s = cls.getLinkSection(s,r'\{@book (.+?)\}',)
        s = cls.getLinkSection(s,r'\{@quickref (.+?)\}')
        s = cls.getLinkSection(s,r'\{@adventure (.+?)\}')
        s = cls.getLinkSection(s,r'\{@action (.+?)\}')

        

        s = re.sub(r'\{@sense (.+?)\}', r'[[\1]]', s)

        


        s = re.sub(r'\{@hit -(\d+?)\}', r'-\1', s)
        s = re.sub(r'\{@hit \+*(\d+?)\}', r'+\1', s)
        s = re.sub(r'\{@h\}', r'*Hit* ', s)
        s = re.sub(r'\{@acttrigger(.*?)\}', r'*Trigger* ', s)
        s = re.sub(r'\{@actresponse(.*?)\}', r'*Response* ', s)
        s = re.sub(r'\{@h\}', r'*Hit* ', s)
        s = re.sub(r'\{@damage (.+?)\}', r'\1', s)
        s = re.sub(r'\{@hom(.*?)\}', r'*Homing*', s)
        s = re.sub(r'\{@chance (\d+).*?\}', r'\1 %', s)

        s = re.sub(r'\{@dc (\d+?)\}', r'DC\1', s)

        s = re.sub(r'\{@recharge\}', r'(Recharge 6)', s)
        s = re.sub(r'\{@recharge (.+?)\}', r'(Recharge \1 or greater)', s)

        s = s.replace('||', '|')

        if s.__contains__('{@'):
            raise ValueError(f'String has not been cleaned: {s}')

        # Remove exceptions that don't make sense to be linked
        s = s.replace('[[d20 test]]', 'saving throw, ability check or attack roll')

        return s


    @staticmethod
    def getLink(s: str, regexPattern : str) -> str:
        for res in re.compile('(' + regexPattern + ')').findall(s):
            if not res:
                return s
            linkName = res[1].split('|')[0]
            s = s.replace(res[0], f'[[{linkName}]]')

        return s


    @staticmethod
    def getLinkSection(s : str, regexPattern : str) -> str:
        '''
        Replaces references in the form
        {@refName str1|.|.|str2} -> [[str1#str2|str2]]
        '''
        # Input regex pattern is enveloped in parentheses so that 
        # the findall returns a list[tuple[regexPattern,match]]
        # This makes it possible to replace all the references in
        # the string iteratively        
        for res in re.compile('(' + regexPattern + ')').findall(s):
            if not res:
                return s
            names = res[1].split('|')

            # Do not replace chapters if they are numbers
            if re.search(r'\d', names[-1]):
                s = s.replace(res[0], f'[[{names[0]}]]')
            else:
                s = s.replace(res[0], f'[[{names[0]}#{names[-1]}|{names[-1]}]]')

        return s


    @staticmethod
    def parseTraits(data : dict) -> list:
        return data.get('trait',[]) + data.get('bonus', []) + data.get('spellcasting',[]) + data.get('Spellcasting',[])


    @classmethod
    def parseLairActions(cls, data: dict[str, list], legendaryType : str) -> str:
        if data.get(legendaryType) is None:
            return ''
        if legendaryType == 'lairActions':
            lairActionString = '## Lair Actions\n'
        elif legendaryType == 'regionalEffects':
            lairActionString = '## Regional Effects\n'
        else:
            raise ValueError(f'Lair action not supported. Must be lairActions or regionalEffects: {legendaryType}')
        for action in data[legendaryType]:
            if isinstance(action, str):
                lairActionString += f'{action}\n'
            elif isinstance(action, dict):
                if action.get('type', '').lower() == 'list':
                    lairActionString += f'{cls.parseListTypeDict(action, key = 'items')}\n'
                elif action.get('type', '').lower() == 'entries':
                    lairActionString += f'\n### {action['name']}\n{cls.parseListTypeDict(action, key = 'entries')}\n' # type:ignore
            else:
                raise TypeError(f'Action type not considered ({type(action)}) : {action}')


        return lairActionString

            
    @staticmethod
    def parseListTypeDict(d : dict, key : str) -> str:
        # Assume the dictionary already has a 
        #   "type" : "list"
        # key: value pair
        s = ''
        if len(d[key]) == 1:
            split = ''
        else:
            split = '- '
        for value in d[key]:
            if isinstance(value, dict):
                if value.get('name'):
                    if value.get('entries'):
                        s += f'\n### {value['name']}\n{f'\n{split}'.join(value['entries'])}\n'
                    elif value.get('entries'):
                        s += f'\n### {value['name']}\n{split}{value['entry']}\n'
                elif value.get('items'):
                    for item in value['items']:
                        s += f'\n{split}**{item['name']}**: {item['entry']}'
                        
                else:
                    if value.get('entries'):
                        s += f'\n{split}'.join(value['entries'])
                    elif value.get('entries'):
                        s += f'{split}{value['entry']}'
            if isinstance(value, str):
                s += f'{split}{value}\n'
        return s
    
if __name__ == '__main__':
    s0 = "Pike has {@quickref Advantage and Disadvantage|PHB|2|0|advantage} on Intelligence, Wisdom, and Charisma {@quickref saving throws|PHB|2|1} against magic."
    tmp = ToolsMonsterParser.getLinkSection(s0,r'\{@quickref (.+?)\}')
    print(s0, '\n', tmp)