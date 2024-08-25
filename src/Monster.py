from src.Trait import Trait
from src.Action import Action

class Monster:
    def __init__(self, data : dict[str, str]) -> None:
        self.name = data['name']
        self.size = data['size']
        self.type = data['type']
        self.alignment = data['alignment']
        self.ac = data['ac']
        self.hp = data['hp']
        self.speed = data['speed']
        self.str = data['str']
        self.dex = data['dex']
        self.con = data['con']
        self.int = data['int']
        self.wis = data['wis']
        self.cha = data['cha']
        self.save = data.get('save')
        self.skill = data.get('skill')
        self.resist = data.get('resist')
        self.vulnerable = data.get('vulnerable')
        self.immune = data.get('immune')
        self.conditionImmune = data.get('conditionImmune')
        self.senses = data.get('senses')
        self.passive = data.get('passive')
        self.languages = data.get('languages')
        self.cr = data['cr']
        self.traits = self.parseTraits(data.get('trait'))
        self.action = self.parseActions(data.get('action'))
        
        self.spells = data.get('spells')
        self.slots = data.get('slots')
        print(self.name)
    
    @staticmethod
    def parseTraits(traits : list[dict[str,str]] | dict[str,str]) -> list[Trait]:
        if traits is None:
            return []
        traitType = type(traits)
        if traitType not in (list, dict):
            raise NotImplementedError('Unknown type for the traits') 
        
        if traitType == list:
            return [Trait(trait) for trait in traits]
        elif traitType == dict:
            return [Trait(traits)]
    
    @staticmethod
    def parseActions(actions : list[dict[str,str]] | dict[str,str] | None) -> list[Action]:
        if actions is None:
            return []
        traitType = type(actions)
        if traitType not in (list, dict):
            raise NotImplementedError('Unknown type for the actions') 
        
        if traitType == list:
            return [Action(trait) for trait in actions]
        elif traitType == dict:
            return [Action(actions)]