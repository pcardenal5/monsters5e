from jinja2 import Environment
import os
import re

class ActionTrait():
    def __init__(self, actionTrait : dict, monsterName: str, environment : Environment, actionTraitType: str, outputFolder : str) -> None:
        # Jinja setup
        self.environment = environment
        self.template = self.environment.get_template('ActionTrait.md')


        self.actionTraitType = actionTraitType
        self.monsterName = monsterName
        self.name = actionTrait.get('name', 'None')
        if self.name == 'None':
            print(f'{self.monsterName} has a trait with no name')
        self.name = self.name.replace('[[resting]]', 'rest')

        self.mainOutputFolder = outputFolder

        # Group Traits by the first letter
        self.outputFolder = os.path.join(self.mainOutputFolder, 'Traits', self.name[0].upper())
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)
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
        self.text = self.text.replace('ft.', 'ft')
        self.text = re.sub(re.escape(self.monsterName), 'the creature', self.text, flags = re.IGNORECASE)
        self.text = re.sub(re.escape(self.monsterName.split(' ')[-1]), 'the creature', self.text, flags = re.IGNORECASE)
        self.text = re.sub(re.escape(self.monsterName.split(' ')[0]), 'the creature', self.text, flags = re.IGNORECASE)
        self.text = self.text.replace(' the the ', ' the ').replace('The the ', 'The ')
        self.text = '. '.join(i.strip().capitalize() for i in self.text.split('. '))




    def parseActionEntries(self, actionTraitList: list) -> str:
        actionText = ''
        for item in actionTraitList:
            actionText += self.parseActionEntryElement(item) + '\n'
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

        self.completeText = self.generateText()
        self.completeFilePath = os.path.join(self.outputFolder, fileName)
        # Check to see if a file with the same name exists.
        if os.path.exists(self.completeFilePath):
            # If it does, read it to compare with the text of the current trait.
            with open(self.completeFilePath, 'r') as inputFile:
                text = ''.join(inputFile.readlines())

            # TODO: this comparison is too strict and some traits differ from a single, often meaningless, word.
            # Maybe a dictionary could be done to save the different versions of the trait and save 
            # only new ones. This could be achieved looping over every different 
            # version of the trait. Very inefficient but could work. 
            if self.completeText == text or self.checkIfSave():
                # It it is the same, change the full text by a hyperlink
                self.completeText = f'![[{self.completeFilePath.replace('.md','').replace(f'{self.mainOutputFolder}/', '')}|{fileName.replace('.md','')}]]'
                return 

            # If its not, save contents to new file
            fileName = f'{cleanName}_{self.monsterName}.md'
            self.completeFilePath = os.path.join(self.outputFolder, fileName)

        # If the file does not exist, save the contents to a new file
        with open(self.completeFilePath, 'w') as outputFile:
            outputFile.write(self.completeText)
        
        self.completeText = f'![[{self.completeFilePath.replace('.md','').replace(f'{self.mainOutputFolder}/', '')}|{fileName.replace('.md','')}]]'


    def generateText(self) -> str:
        return self.template.render(self.__dict__)


    def checkIfSave(self) -> bool:
        '''
        Checks whether or not to try to save the trait. The main criteria is 
        cheching to see if the actionTraitType is `'trait'`, but some are
        hard coded.

        This list is done manually by checking after one iteration has been done 
        '''
        exceptionList = [
            'Aggressive',
            'Legendary resistance',
            'Magic resistance',
            'Pack tactics',
            'Swarm',
            'Incorporeal movement',
            'Evasion',
            'Keen' # Captures all keen eye, smell, etc.
        ]

        check = lambda s: (self.name.lower().startswith(s))

        b = False
        for exception in exceptionList:
            b = b or check(exception.lower())

        return b