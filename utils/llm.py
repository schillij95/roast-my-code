import ollama
import streamlit as st
from config import PROMPT_CODE_SNIPPET_TEMPLATE

def get_model_names():
    """
    Retrieve a list of installed model names from Ollama.

    Returns:
        list[str]: List of model names.
    """
    return [model.model for model in ollama.list().get('models', [])]

def get_llm_response(prompt: str):
    """
    Generate a response from the selected LLM model using a given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        generator: A generator yielding response chunks from the LLM.
    """
    model = st.session_state.get('model')
    if not model:
        raise ValueError("No model selected in session state.")
    # Stream responses for efficient UI updates
    return ollama.generate(model=model, prompt=prompt, stream=True)

def generate_code_roast(code: str, roast_style: str, detailed: bool = False):
    """
    Generate a code roast using the LLM based on the provided code and roast style.

    Args:
        code (str): The code snippet to roast.
        roast_style (str): The style of roasting (e.g., humorous, harsh).
        detailed (bool, optional): Whether to request a detailed roast. Defaults to False.

    Returns:
        generator: A generator yielding the roast response from the LLM.
    """
    # Optionally add detail to the prompt if requested
    prompt = PROMPT_CODE_SNIPPET_TEMPLATE.format(
        code=code,
        roast_style=roast_style + (" (detailed)" if detailed else "")
    )
    return get_llm_response(prompt)