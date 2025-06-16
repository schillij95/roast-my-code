import ollama
import streamlit as st
from config import PROMPT_CODE_SNIPPET_TEMPLATE, PROMPT_GITHUB_PROFILE_TEMPLATE

def get_model_names():
    """
    Retrieve a list of installed model names from Ollama.

    Returns:
        list[str]: List of model names.
    """
    return [model.model for model in ollama.list().get('models', [])]

def get_llm_response(prompt: str, stream=True):
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
    result = ollama.generate(model=model, prompt=prompt, stream=stream)

    if stream:
        return result  # generator
    else:
        return result['response']  # full string

def generate_code_roast(code: str, roast_style: str, detailed: bool = False, type: str = "code snippet"):
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
    match type:
        case "code snippet":
            print("Roasting code snippet...")
            prompt_template = PROMPT_CODE_SNIPPET_TEMPLATE
        case "github profile":
            print("Roasting GitHub profile...")
            prompt_template = PROMPT_GITHUB_PROFILE_TEMPLATE
        case _:
            print(f"Unknown type: {type}")
            raise ValueError(f"Unknown type: {type}")
    prompt = prompt_template.format(
        code=code,
        roast_style=roast_style + (" (mention specific files)" if detailed else " (use at most 3 sentences)"),
    )
    return get_llm_response(prompt)