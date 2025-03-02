# Orion Agent

An app for Orion interaction using LLMs.

# Install

## Requirements
**Orion-Agent** is developed on Python 3.8, 3.9, 3.10, and 3.11.

Also, although it is not strictly required, the usage of a [virtualenv](https://virtualenv.pypa.io/en/latest/) is highly recommended in order to avoid interfering with other software installed in the system where **Orion-Agent** is run.

## Install from source
We use **poetry** for package management. Please [install poetry](https://python-poetry.org/docs/#installation) according to the documentation.

To check if poetry is installed:
```
poetry --version
```
The first step would be to clone the **Orion-Agent** repository. 
```
git clone https://github.com/sintel-dev/Orion-Agent
cd Orion-Agent
```

Then install the package using poetry:
```
poetry install
```

# Quickstart

## Set up keys

Create a new file called `orionagent/.streamlit/secrets.toml` with the following content:

```toml
OPENAI_API_KEY = "your OpenAI key"
```

## Run the app

```bash
streamlit run app.py
```