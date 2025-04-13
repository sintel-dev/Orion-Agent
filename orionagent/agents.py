import ast
import textwrap
import json
import os
import re

# import openai
from openai import OpenAI

from rag.embeddings import find_similar, load_embeddings

TEMPLATE = """
Orion is a python library for time series anomaly detection.
Familiarize yourself with the Orion library: https://github.com/sintel-dev/Orion/

You are going to help the user find anomalies in their data and solve their task
provided under USER TASK DESCRIPTION by generating code that explicitly uses Orion.

Only return code, return nothing else.

USER TASK DESCRIPTION:
"""

RAG_TEMPLATE = """
QUESTION:
{}

CONTEXT:
{}

INSTRUCTIONS:
Answer the users QUESTION using the CONTEXT above.
Keep your answer grounded in the facts of the CONTEXT.

Make sure to use the right pipeline name and right configuration
of hyperparameters. Only return code, return nothing else.
"""

class LLM:
    def run(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAILLM(LLM):
    def __init__(self, model: str = 'gpt-4o-mini', client: OpenAI = None, system_prompt: str = TEMPLATE):
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

        self.rag_table = load_embeddings(path='../embeddings.pkl')

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
    
    def run_rag(self, user_task: str) -> str:

        similar_documents = find_similar(user_task, table=self.rag_table, openai_client = self.client, k=3)
        documents = [
            f'DOCUMENT #{i+1}: {doc}' for i, doc in enumerate(similar_documents)
        ]
        
        prompt = RAG_TEMPLATE.format(user_task, documents)
        system_message = """
            Orion is a python library for time series anomaly detection.
            Familiarize yourself with the Orion library: https://github.com/sintel-dev/Orion/
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content


class Agent:
    def __init__(self, llm: LLM, name: str):
        self.llm = llm
        self.name = name

    def ask_user(self, question: str) -> str:
        # print('Asking user...')
        response = input(question)
        return response


def normalize_generated_code(code: str) -> str:
    # Remove ```python or ``` at the start, and closing ``
    code = re.sub(r'^```(?:python)?\s*|\s*```$', '', code.strip(), flags=re.MULTILINE)

    # Replace common invisible unicode with plain space
    code = code.replace('\u00A0', ' ')  # non-breaking space
    code = code.replace('\u200B', '')   # zero-width space
    code = code.replace('\ufeff', '')   # BOM

    # Normalize line endings and remove leading/trailing space
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    code = textwrap.dedent(code)
    code = code.strip()

    # Remove leading blank lines
    code = re.sub(r'^\s*\n', '', code, flags=re.MULTILINE)

    # Make sure it ends with a newline (optional)
    if not code.endswith('\n'):
        code += '\n'


    return code

def is_code_valid(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return False

def execute_code(code: str, variable_name: str) -> bool:
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
        code = normalize_generated_code(code)
        is_code_valid(code)
        # Execute the code and capture the output
        print('trying')
        exec_globals = {}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)

        print('executed successfully')
        
        result = exec_locals.get(variable_name, None)
        return True, result
    
    except Exception as ex:
        print(f'error {ex}')
        return False, None


if __name__ == '__main__':
    with open('code_snippet.txt', 'r') as f:
        test = f.read()

    status, anomalies = execute_code(test, 'anomalies')

    print(anomalies)
