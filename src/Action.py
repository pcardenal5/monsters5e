from jinja2 import Environment, FileSystemLoader

class Action():
    def __init__(self, action : dict) -> None:
        # Jinja setup
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('actions.md')

        self.name = action['name']
        self.text = action['text']
        self.attack = action.get('attack', '')
        self.parseText()
        self.parseAttack()

        otherActions = list(action.keys())
        otherActions.remove('name')
        otherActions.remove('text')
        if self.attack:
            otherActions.remove('attack')
        # Check to see if any fields have not been accounted for
        if len(otherActions) != 0:
            raise NotImplementedError(f'There are more features in the action {", ".join(otherActions)}')

    def parseText(self) -> str:
        if type(self.text) == list:
            self.text = '\n'.join([t for t in self.text if t is not None])

    def parseAttack(self) -> str:
        if type(self.attack) == list:
            self.attack = '\n'.join([t for t in self.attack if t is not None])

    def generateText(self) -> str:
        return self.template.render(self.__dict__)