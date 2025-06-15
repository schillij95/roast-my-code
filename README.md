# roast-my-code
We provide the best roasts.

## Installation
To set up the GITHUB_TOKEN, create a classic github token. Then export it to the environment:
```bash
export GITHUB_TOKEN=your_token_here
```

Install ollama. See the [ollama installation guide](https://ollama.com/docs/installation).

To install the dependencies, run:
```bash
conda env create -n roaster python=3.12
```
Then activate the environment:
```bash
conda activate roaster
```
Install the requirements:
```bash
pip install -r requirements.txt
```

## Usage
Pull your favourite LLM:
```bash
ollama pull gemma3:4b
```

To run the application, use:
```bash
streamlit run main.py
```
