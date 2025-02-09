from jinja2 import Environment, FileSystemLoader
import re
import os

class LegendaryGroup:
    def __init__(self, data : dict[str, str], source : str, outputFolder : str) -> None:
        self.environment = Environment(loader = FileSystemLoader('templates/'))
        self.template = self.environment.get_template('LegendaryGroup.md')

        self.data = data
        self.name = self.data['name']
        self.source = self.data['source']


        self.outputFolder = outputFolder
        self.groupsOutputFolder = os.path.join(self.outputFolder, 'LegendaryGroups')
        self.completeOutputPath = os.path.join(self.groupsOutputFolder, f'{self.name}_{self.source}') + '.md'
        if not os.path.exists(self.groupsOutputFolder):
            os.makedirs(self.groupsOutputFolder)

    def generateText(self) -> str:
        return self.template.render(self.__dict__)
