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

If you want to use the speech output feature, you need to install `kokoro`, `soundfile` and `espeak-ng`. You can do this by running:
```bash
!pip install -q kokoro>=0.9.2 soundfile
!apt-get -qq -y install espeak-ng > /dev/null 2>&1
```
(See the [kokoro huggingface page](https://huggingface.co/hexgrad/Kokoro-82M) for more information.)
