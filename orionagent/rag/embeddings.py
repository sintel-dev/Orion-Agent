import os
import json
import pickle

import tiktoken
import numpy as np
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

MAX_TOKENS = 8191

def num_tokens_from_string(string, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def split_text(text, chunk_size=None, overlap=None, model="cl100k_base"):
    chunk_size = chunk_size or MAX_TOKENS // 2
    overlap = overlap or chunk_size // 5

    chunks = []
    start = end = 0

    words = text.split(' ')
    while end < len(words):
        end = start + chunk_size

        text_chunck = ' '.join(text[start:end])
        chunks.append(text_chunck)
        start = end - overlap  # overlap chunks

    return chunks

def get_embedding(text, client, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model, encoding_format="float")

def generate_embeddings(openai_key, path='orion_contents/', model="text-embedding-3-small", test=True):
    documents = list()

    for (root, dirs, files) in os.walk(path):
        for file in tqdm(files, desc=root):
            if os.path.isdir(file) or '.png' in file or '.ico' in file:
                continue

            name = file.split('/')[-1]
            print(file)
            with open(os.path.join(root, file), 'r') as f:
                data = f.read()

            if test:
                count = num_tokens_from_string(data)
                documents.append({'document': name, 'num_tokens': count})

            else:
                try:
                    client = OpenAI(api_key=openai_key)
                    chunks = split_text(data)
                    for i, chunk in enumerate(chunks):
                        embedding = get_embedding(chunk, client, model=model).to_dict()
                        embedding['document'] = f'{name}_{i+1}_{len(chunks)}'
                    
                        documents.append(embedding)

                except Exception as ex:
                    print(f'ran into an error processing {file} with message {ex}.')
                    with open('embeddings.pkl', 'wb') as f:
                        pickle.dump(documents, f)
                
        print(f'finished processing {root}')
        with open('embeddings.pkl', 'wb') as f:
            pickle.dump(documents, f)

    if test:
        return pd.DataFrame.from_records(documents)
    
    return documents

def format_into_table(embeddings):
    formatted = []
    for embed in embeddings:
        eid = embed['document']
        evalue = np.array(embed['data'][0]['embedding'])
        formatted.append({'eid': eid, 'embedding': evalue})

    table = pd.DataFrame.from_records(formatted)
    return table


if __name__ == '__main__':
    openai_key = os.environ['OPENAI_API_KEY']
    docs = generate_embeddings(openai_key, test=False)

    with open('embeddings.pkl', 'rb') as f:
        test = pickle.load(f)

    table = format_into_table(test)
    print(table)