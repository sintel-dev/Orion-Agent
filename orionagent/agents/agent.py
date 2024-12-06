import json
import os

import openai
import tiktoken
from openai import OpenAI

TEMPLATE = """
You are a helpful assistant.
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