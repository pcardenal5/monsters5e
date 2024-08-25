from src.Trait import Trait
from src.Action import Action
from jinja2 import Environment, FileSystemLoader


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
        self.str = data['str']
        self.dex = data['dex']
        self.con = data['con']
        self.int = data['int']
        self.wis = data['wis']
        self.cha = data['cha']
        self.speed = data['speed']
        self.save = data.get('save')
        self.skill = data.get('skill')
        self.passive = data.get('passive') # Passive perception
        self.senses = data.get('senses')
        self.languages = data.get('languages')
        
        self.resist = data.get('resist')
        self.vulnerable = data.get('vulnerable')
        self.immune = data.get('immune')
        self.conditionImmune = data.get('conditionImmune')
        self.buildResistances()
        
        self.traits = self.parseTraits(data.get('trait'))
        self.action = self.parseActions(data.get('action'))
        
        self.spells = data.get('spells')
        self.slots = data.get('slots')
    
    @staticmethod
    def parseTraits(traits : list[dict[str,str]] | dict[str,str]) -> list[Trait]:
        if traits is None:
            return []
        traitType = type(traits)
        if traitType not in (list, dict):
            raise NotImplementedError('Unknown type for the traits') 
        
        if traitType == list:
            return [Trait(trait).generateText() for trait in traits]
        elif traitType == dict:
            return [Trait(traits).generateText()]

    @staticmethod
    def parseActions(actions : list[dict[str,str]] | dict[str,str] | None) -> list[Action]:
        if actions is None:
            return []
        actionType = type(actions)
        if actionType not in (list, dict):
            raise NotImplementedError('Unknown type for the actions') 
        
        if actionType == list:
            return [Action(action).generateText() for action in actions]
        elif actionType == dict:
            return [Action(actions).generateText()]

    def buildResistances(self):
        self.resistances = ''

        if self.resist is not None:
            self.resistances += '**Resistances**: ' + self.resist + '\n\n'
        if self.vulnerable is not None:
            self.resistances += '**Vulnerabilities**: ' + self.vulnerable + '\n\n'
        if self.immune is not None:
            self.resistances += '**Damage Immunities**: ' + self.immune + '\n\n'
        if self.conditionImmune is not None:
            self.resistances += '**Condition Immunities**' + self.conditionImmune + '\n\n'
    
    def generateText(self) -> str:
        return self.template.render(self.__dict__)