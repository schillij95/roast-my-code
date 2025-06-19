# roast-my-code
We provide the best roasts.

## Installation
Install ollama. See the [ollama installation guide](https://ollama.com/docs/installation).

To install the dependencies, run:
```bash
conda create -n roaster python=3.12
```
Then activate the environment:
```bash
conda activate roaster
```
Install the requirements:
```bash
pip install -r requirements.txt
```
We are using Ollama to serve local LLMs:
```bash
sudo snap install ollama
```

If you want to use the speech output feature, you need to install `espeak-ng`. You can do this by running:
```bash
sudo apt-get -y install espeak-ng
```

To roast a GItHub profile, set up the GITHUB_TOKEN by creating a classic github token. Then export it to the environment:
```bash
export GITHUB_TOKEN=your_token_here
```

### Docker Compose Setup

```bash
sudo docker compose up --build
```

## Usage
Pull your favourite LLM:
```bash
ollama pull mistral:latest
```

To run the application, use:
```bash
streamlit run main.py
```