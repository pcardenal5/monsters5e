from jinja2 import Environment
import os
import re

class ActionTrait():
    def __init__(self, actionTrait : dict, monsterName: str, environment : Environment, actionTraitType: str, outputFolder : str) -> None:
        # Jinja setup
        self.environment = environment
        self.template = self.environment.get_template('ActionTrait.md')

        self.mainOutputFolder = outputFolder
        self.outputFolder = os.path.join(self.mainOutputFolder, 'Traits')

        self.actionTraitType = actionTraitType
        self.monsterName = monsterName
        self.name = actionTrait.get('name', '')
        if self.name == '':
            print(f'{self.monsterName} has a trait with no name')
        if actionTrait.get('text'):
            self.text = actionTrait['text']
        elif actionTrait.get('entries') is not None:
            self.text = self.parseActionEntries(actionTrait['entries'])
        else:
            self.text = ''
            print(f'{self.monsterName} has a trait with no text')

        self.attack = actionTrait.get('attack', '')
        self.parseText()
        self.parseAttack()

        self.completeText = self.generateText()

        # Make wikilinks only to traits
        if (self.actionTraitType == 'trait') and (not self.name.__contains__('Spellcasting')):
            self.saveTrait()

    def parseText(self) -> None:
        if type(self.text) == list:
            self.text = '\n'.join([t for t in self.text if t is not None])
        self.text.replace('•', '- ')


    def parseActionEntries(self, actionTraitList: list) -> str:
        actionText = ''
        for item in actionTraitList:
            actionText += self.parseActionEntryElement(item)
        return actionText


    def parseActionEntryElement(self, actionTrait) -> str:
        if isinstance(actionTrait, str):
            return actionTrait

        actionText = ''        
        if isinstance(actionTrait, dict):
            if not actionTrait.get('items'):
                return ActionTrait(
                    actionTrait, 
                    self.monsterName,
                    environment = self.environment, 
                    actionTraitType = self.actionTraitType, 
                    outputFolder = self.mainOutputFolder
                ).completeText


            for element in actionTrait['items']:
                if isinstance(element, dict):
                    try:
                        actionText += f'**{element['name']}** : {element['entry']}'
                    except Exception as e:
                        actionText += f'**{element['name']}** : {element['entries']}'
                if isinstance(element, str):
                    actionText += f'{element}'

            return actionText

        raise TypeError(f'ActionEntryElement not supported({type(actionTrait)}): {actionTrait}')


    def parseAttack(self) -> None:
        if type(self.attack) == list:
            self.attack = '\n'.join([t for t in self.attack if t is not None])
        self.attack.replace('•', '- ')
        if self.attack != '':
            self.attack = f'\n{self.attack}\n'


    def saveTrait(self) -> None:
        cleanName = self.name.replace('/', ' per ').replace('\\', ' per ')
        fileName = f'{cleanName}.md'
        # TODO: move to parseText
        traitTextClean = self.text.replace('ft.', 'ft')
        traitTextClean = re.sub(re.escape(self.monsterName), 'the creature', traitTextClean, flags = re.IGNORECASE)
        traitTextClean = re.sub(re.escape(self.monsterName.split(' ')[-1]), 'the creature', traitTextClean, flags = re.IGNORECASE)
        traitTextClean = re.sub(re.escape(self.monsterName.split(' ')[0]), 'the creature', traitTextClean, flags = re.IGNORECASE)
        traitTextClean = traitTextClean.replace(' the the ', ' the ').replace('The the ', 'The ')
        traitTextClean = '.'.join('\n'.join(k.capitalize() for k in i.split('\n')).capitalize() for i in traitTextClean.split('.'))

        self.completeText = self.generateText()
        if os.path.exists(os.path.join(self.outputFolder,fileName)):
            with open(os.path.join(self.outputFolder,fileName), 'r') as inputFile:
                text = ''.join(inputFile.readlines())

            if traitTextClean == text:
                self.completeText = f'![[{fileName.replace('.md','')}]]'
                return 
            # Save contents to new file
            fileName = f'{cleanName}_{self.monsterName}.md'

        with open(os.path.join(self.outputFolder, fileName), 'w') as outputFile:
            outputFile.write(traitTextClean)
        
        self.completeText = f'![[{fileName.replace('.md','')}]]'


    def generateText(self) -> str:
        return self.template.render(self.__dict__)
