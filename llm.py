import ollama 
import streamlit as st
from config import PROMPT_CODE_SNIPPET_TEMPLATE

def get_installed_models():
    return [model['name'] for model in ollama.list()['models']]

def get_llm_response(prompt: str):
    model = st.session_state['model']
    response_generator = ollama.generate(model=model, prompt=prompt, stream=True)
    return response_generator

def generate_code_roast(code: str, roast_style: str, detailed: bool = False):
    # TODO implement detailed roast logic
    prompt = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code, roast_style=roast_style)
    response_generator = get_llm_response(prompt)
    return response_generator