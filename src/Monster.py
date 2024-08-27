from src.ActionTrait import ActionTrait
from jinja2 import Environment, FileSystemLoader
from math import floor
import re

class Monster:
    def __init__(self, data : dict[str, str], source : str) -> None:
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('monster.md')

        self.source = source
        self.name = data['name']
        self.size = data['size']
        self.type = data['type']
        self.cr = data['cr']
        self.alignment = data['alignment']
        self.ac = data['ac']
        self.hp = data['hp']
        self.str = int(data['str'])
        self.dex = int(data['dex'])
        self.con = int(data['con'])
        self.int = int(data['int'])
        self.wis = int(data['wis'])
        self.cha = int(data['cha'])

        self.strMod = self.calculateModifier(self.str)
        self.dexMod = self.calculateModifier(self.dex)
        self.conMod = self.calculateModifier(self.con)
        self.intMod = self.calculateModifier(self.int)
        self.wisMod = self.calculateModifier(self.wis)
        self.chaMod = self.calculateModifier(self.cha)

        self.saves = data.get('save', '')

        self.strSave = self.getSave('str')
        self.dexSave = self.getSave('dex')
        self.conSave = self.getSave('con')
        self.intSave = self.getSave('int')
        self.wisSave = self.getSave('wis')
        self.chaSave = self.getSave('cha')

        self.speed = data['speed']
        self.skill = data.get('skill', '')
        self.passive = data.get('passive', '') # Passive perception
        self.senses = data.get('senses', '')
        self.languages = data.get('languages', '')
        
        self.resist = data.get('resist', '')
        self.vulnerable = data.get('vulnerable', '')
        self.immune = data.get('immune', '')
        self.conditionImmune = data.get('conditionImmune', '')
        self.buildResistances()
        
        self.traits = self.parseActionTraits(data.get('trait'))
        self.actions = self.parseActionTraits(data.get('action'))
        
        self.spells = data.get('spells')
        self.slots = data.get('slots')
    
    @staticmethod
    def parseActionTraits(actionTrait : list[dict[str,str]] | dict[str,str]) -> list[ActionTrait]:
        if actionTrait is None:
            return ''
        traitType = type(actionTrait)
        if traitType not in (list, dict):
            raise NotImplementedError('Type not supported') 
        
        if traitType == list:
            return '\n'.join([ActionTrait(trait).generateText() for trait in actionTrait])
        elif traitType == dict:
            return '\n'.join([ActionTrait(actionTrait).generateText()])

    def buildResistances(self):
        self.resistances = ''

        if self.resist != '':
            self.resistances += '**Resistances**: ' + self.resist + '\n\n'
        if self.vulnerable != '':
            self.resistances += '**Vulnerabilities**: ' + self.vulnerable + '\n\n'
        if self.immune != '':
            self.resistances += '**Damage Immunities**: ' + self.immune + '\n\n'
        if self.conditionImmune != '':
            self.resistances += '**Condition Immunities**: ' + self.conditionImmune + '\n\n'

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