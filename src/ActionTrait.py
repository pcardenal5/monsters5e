from jinja2 import Environment
import os

class ActionTrait():
    def __init__(self, actionTrait : dict, monsterName: str, environment : Environment, actionTraitType: str) -> None:
        # Jinja setup
        self.environment = environment
        self.template = self.environment.get_template('ActionTrait.md')
        self.actionTraitType = actionTraitType
        self.monsterName = monsterName

        self.name = actionTrait['name']
        if self.name is None:
            self.name = 'Legendary Action'
        if actionTrait.get('text') is not None:
            self.text = actionTrait['text']
        if actionTrait.get('entries') is not None:
            self.text = self.parseActionEntries(actionTrait['entries'])


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

    @staticmethod
    def parseActionEntries(actionTrait: list) -> str:
        actionText = ''
        for item in actionTrait:
            if isinstance(item, str):
                actionText += item
                continue
            
            if isinstance(item, dict):
                for element in item['items']:
                    try:
                        actionText += f'**{element['name']}** : {element['entry']}'
                    except Exception as e:
                        actionText += f'**{element['name']}** : {element['entries']}'

        return actionText

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