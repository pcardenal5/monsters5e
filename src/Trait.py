class Trait():
    def __init__(self, trait : dict[str,str]) -> None:
        self.name = trait['name']
        self.text = trait['text']
        self.attack = trait.get('attack')

        otherTrait = list(trait.keys())
        otherTrait.remove('name')
        otherTrait.remove('text')
        if self.attack:
            otherTrait.remove('attack')
        # Check to see if any fields have not been accounted for
        if len(otherTrait) != 0:
            raise NotImplementedError(f'There are more features in the trait {", ".join(otherTrait)}')