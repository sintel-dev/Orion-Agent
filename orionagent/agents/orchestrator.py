import json
import pickle

from agent import Agent, LLM

class OrchestratorAgent(Agent):
    def __init__(self, llm: LLM):
        super().__init__(llm, 'orchestrator')
        self.database = dict()

    def run(self, prompt: str) -> str:
        return self.llm.run(prompt)
    
    def save_database(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(self.database, f)

    def load_database(self, filename: str):
        with open(filename, 'rb') as f:
            self.database = pickle.load(f)