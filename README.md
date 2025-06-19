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

### Environment Variables
To authenticate to services, you can either export env vars in your shell or create a `.env` file at the project root (see `.env.example`).

For GitHub profile roasting:
```bash
export GITHUB_TOKEN=your_token_here
```

If you plan to use the OpenAI Python client in the future (not required for Ollama):
```bash
export OPENAI_API_KEY=your_openai_api_key_here
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