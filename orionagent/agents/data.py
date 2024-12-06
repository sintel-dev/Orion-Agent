import re
import pandas as pd

from agent import Agent, LLM

TEMPLATE = """
You are a data loader agent.

You are responsible for getting the data from the user and loading it into a dataframe.
If you are unable to load the data, please ask the user to share the dataset with you.

You have access to the following tools:
- pd.read_csv(filename: str) -> pd.DataFrame: This tool allows you to read a csv file and load it into a dataframe.
- input(prompt: str) -> str: This tool allows you to query the user for more information.
"""

class DataLoaderAgent(Agent):
    def __init__(self, llm, ):
        super().__init__(llm, 'data_loader')
        self.readingtool = pd.read_csv
        self.querytool = input

    def extract_filename(self, response: str) -> str:
        extension = re.findall(r'\b[\w\-.]+\.csv\b', response)
        while len(extension) == 0:
            response = self.ask_user('I couldn\'t find a csv file in your response. Please share the filename with me.\n')
            extension = re.findall(r'\b[\w\-.]+\.csv\b', response)
        
        return extension[0]

    def run(self, prompt: str) -> str:
        response = self.llm.run(prompt)
        filename = self.extract_data(response)

        while not self.evaluate(filename):
            try:
                file = pd.read_csv(filename)
            except:
                response = self.ask_user(f'I couldn\'t load the file {filename}. Please share the filename with me.\n')
                filename = self.extract_filename(response)
        
        return response
    
    def evaluate(self, database: dict) -> bool:
        if database.get('dataframe') is None:
            return False
        
        return True

