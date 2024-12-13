import ast
import json
import os

# import openai
from openai import OpenAI

TEMPLATE = """
Orion is a python library for time series anomaly detection.
Familiarize yourself with the Orion library: https://github.com/sintel-dev/Orion/

You are going to help the user find anomalies in their data and solve their task
provided under USER TASK DESCRIPTION by generating code that explicitly uses Orion.

Only return code, return nothing else.

USER TASK DESCRIPTION:
"""

class LLM:
    def run(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAILLM(LLM):
    def __init__(self, model: str = 'gpt-4o-mini', client: OpenAI = None, system_prompt: str = TEMPLATE):
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

        print('What can I help you with today?')

    def run(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content

class Agent:
    def __init__(self, llm: LLM, name: str):
        self.llm = llm
        self.name = name

    def ask_user(self, question: str) -> str:
        print('Asking user...')
        response = input(question)
        return response
    

def execute_code(code: str) -> bool:
    """Execute code block.
    
    This function takes in a string ``code`` and
    tests if the syntax is correct, executes 
    the code, then returns whether the execution
    was successful or not.

    Args:
        code (str): String containing code block.

    Returns:
        bool:
            Whether the execution was successful.

    Raises:
        ValueError:
            If the code is not executable.
    """
    try:
        ast.parse(code) # check syntax, throws a SyntaxError

        # Execute the code and capture the output
        print('trying')
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        
        result = exec_locals.get('anomalies', None)
        return True, result
    
    except Exception as ex:
        print(f'error {ex}')
        return False


if __name__ == '__main__':
    with open('code_snippet.txt', 'r') as f:
        test = f.read()

    status, anomalies = execute_code(test)

    print(anomalies)
