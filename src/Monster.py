from src.ActionTrait import ActionTrait
from jinja2 import Environment, FileSystemLoader
from math import floor
import re
import os

class Monster:
    def __init__(self, data : dict[str, str], source : str, outputFolder : str) -> None:
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('monster.md')

        self.data = data
        self.source = source
        self.name = self.data['name'].replace('/','-')
        self.size = self.data['size']
        self.type = self.data['type']
        self.cr = self.data['cr']
        self.alignment = self.data['alignment']
        self.ac = self.data['ac']
        self.hp = self.data['hp']
        self.str = int(self.data.get('str', 0))
        self.dex = int(self.data.get('dex', 0))
        self.con = int(self.data.get('con', 0))
        self.int = int(self.data.get('int', 0))
        self.wis = int(self.data.get('wis', 0))
        self.cha = int(self.data.get('cha', 0))

        self.strMod = self.calculateModifier(self.str)
        self.dexMod = self.calculateModifier(self.dex)
        self.conMod = self.calculateModifier(self.con)
        self.intMod = self.calculateModifier(self.int)
        self.wisMod = self.calculateModifier(self.wis)
        self.chaMod = self.calculateModifier(self.cha)

        self.saves = self.data.get('save', '')

        self.strSave = self.getSave('str')
        self.dexSave = self.getSave('dex')
        self.conSave = self.getSave('con')
        self.intSave = self.getSave('int')
        self.wisSave = self.getSave('wis')
        self.chaSave = self.getSave('cha')

        self.speed = self.data.get('speed', 0)
        self.skill = self.data.get('skill', '')
        self.senses = self.data.get('senses', '')
        self.languages = self.data.get('languages', '')

        self.resist = self.data.get('resist', '')
        self.vulnerable = self.data.get('vulnerable', '')
        self.immune = self.data.get('immune', '')
        self.conditionImmune = self.data.get('conditionImmune', '')
        self.buildResistances()


        self.outputFolder = outputFolder
        self.monsterOutputFolder = os.path.join(self.outputFolder, self.cr.replace('/', '-').replace('l','1').replace('00','0'))
        self.completeOutputPath = os.path.join(self.monsterOutputFolder, self.name) + '.md',
        if not os.path.exists(self.monsterOutputFolder):
            os.makedirs(self.monsterOutputFolder)

        self.traits = self.parseActionTraits('trait')
        self.actions = self.parseActionTraits('action')
        self.legendary = self.parseActionTraits('legendary')

        self.buildActionTraits()

    def parseActionTraits(self, actionTraitType : str) -> str:
        actionTrait = self.data.get(actionTraitType)
        if actionTrait is None:
            return ''
        traitType = type(actionTrait)
        if traitType not in (list, dict):
            raise NotImplementedError('Type not supported') 
        
        if traitType == list:
            return '\n'.join([ActionTrait(trait, self.name, self.environment, actionTraitType, self.outputFolder).completeText for trait in actionTrait]) # type: ignore
        
        return '\n'.join([ActionTrait(actionTrait, self.name, self.environment, actionTraitType, self.outputFolder).completeText])# type: ignore

    def buildResistances(self) -> None:
        self.resistances = ''

        if self.resist != '':
            self.resistances += '**Resistances**: ' + self.resist + '\n\n'
        if self.vulnerable != '':
            self.resistances += '**Vulnerabilities**: ' + self.vulnerable + '\n\n'
        if self.immune != '':
            self.resistances += '**Damage Immunities**: ' + self.immune + '\n\n'
        if self.conditionImmune != '':
            self.resistances += '**Condition Immunities**: ' + self.conditionImmune + '\n\n'

    def buildActionTraits(self) -> None:
        self.actionTraits = ''
        if self.traits != '':
            self.actionTraits += f'## Traits\n\n{self.traits}\n\n'
        if self.actions != '':
            self.actionTraits += f'## Actions\n\n{self.actions}\n\n'
        if self.legendary != '':
            self.actionTraits += f'## Legendary Actions\n\n{self.legendary}\n\n'


    def generateText(self) -> str:
        return self.template.render(self.__dict__)

    @staticmethod
    def calculateModifier(stat: int) -> int:
        return int(floor(stat/2.) - 5)

    def getSave(self, stat : str) -> int:
        regex = re.compile(stat.lower() + r'\s([+\-]\d+)').search(self.saves.lower())
        if regex:
            return int(regex.group(1))

        return self.__getattribute__(stat + 'Mod')