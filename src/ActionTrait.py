from jinja2 import Environment, FileSystemLoader

class ActionTrait():
    def __init__(self, actionTrait : dict) -> None:
        # Jinja setup
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('ActionTrait.md')

        self.name = actionTrait['name']
        if self.name is None:
            self.name = 'Legendary Action'
        self.text = actionTrait['text']
        self.attack = actionTrait.get('attack', '')
        self.parseText()
        self.parseAttack()

    def parseText(self) -> str:
        if type(self.text) == list:
            self.text = '\n'.join([t for t in self.text if t is not None])
        self.text.replace('•', '- ')

    def parseAttack(self) -> str:
        if type(self.attack) == list:
            self.attack = '\n'.join([t for t in self.attack if t is not None])
        self.attack.replace('•', '- ')
        if self.attack != '':
            self.attack = f'\n{self.attack}\n'

    def generateText(self) -> str:
        return self.template.render(self.__dict__)