from jinja2 import Environment, FileSystemLoader

class Trait():
    def __init__(self, trait : dict[str,str]) -> None:
        # Jinja setup
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('traits.md')

        self.name = trait['name']
        self.text = trait['text']
        self.attack = trait.get('attack', '')
        self.parseText()
        self.parseAttack()
        otherTrait = list(trait.keys())
        otherTrait.remove('name')
        otherTrait.remove('text')
        if self.attack:
            otherTrait.remove('attack')
        # Check to see if any fields have not been accounted for
        if len(otherTrait) != 0:
            raise NotImplementedError(f'There are more features in the trait {", ".join(otherTrait)}')


    def parseText(self) -> str:
        if type(self.text) == list:
            self.text = ''.join([t for t in self.text if t is not None])

    def parseAttack(self) -> str:
        if type(self.attack) == list:
            self.attack = ''.join([t for t in self.attack if t is not None])

    def generateText(self) -> str:
        return self.template.render(self.__dict__)