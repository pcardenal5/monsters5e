class Action():
    def __init__(self, action : dict) -> None:
        self.name = action['name']
        self.text = action['text']
        self.attack = action.get('attack')

        otherActions = list(action.keys())
        otherActions.remove('name')
        otherActions.remove('text')
        if self.attack:
            otherActions.remove('attack')
        # Check to see if any fields have not been accounted for
        if len(otherActions) != 0:
            raise NotImplementedError(f'There are more features in the action {", ".join(otherActions)}')