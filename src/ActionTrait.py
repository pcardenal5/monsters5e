from jinja2 import Environment
import os

class ActionTrait():
    def __init__(self, actionTrait : dict, monsterName: str, environment : Environment, actionTraitType: str) -> None:
        # Jinja setup
        self.environment = environment
        self.template = self.environment.get_template('ActionTrait.md')
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
                return ActionTrait(actionTrait, self.monsterName,environment = self.environment, actionTraitType = self.actionTraitType).completeText


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
        traitTextClean = (
            self.completeText
            .replace(f'{self.monsterName}', 'The creature')
            .replace(f'{self.monsterName.lower()}', 'The creature')
            .replace(f'{self.monsterName.split(' ')[-1].lower()}', 'the creature')
            .replace(' the the ', ' the ')
            .replace('The the ', 'The ')
        )

        if os.path.exists('./5etools/Traits/' + fileName):
            with open('./5etools/Traits/' + fileName, 'r') as inputFile:
                text = ''.join(inputFile.readlines())

            if traitTextClean == text:
                self.completeText = f'![[{fileName.replace('.md','')}]]'
                return 
            # Save contents to new file
            fileName = f'{cleanName}_{self.monsterName}.md'

        with open('./5etools/Traits/' + fileName, 'w') as outputFile:
            outputFile.write(traitTextClean)
        
        self.completeText = f'![[{fileName.replace('.md','')}]]'

    def generateText(self) -> str:
        return self.template.render(self.__dict__)