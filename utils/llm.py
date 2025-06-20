import os
import ollama
import streamlit as st
from config import PROMPT_CODE_SNIPPET_TEMPLATE, PROMPT_GITHUB_PROFILE_TEMPLATE


if "OLLAMA_HOST" in os.environ:
    ollama.Client(host=os.environ["OLLAMA_HOST"])


def get_model_names():
    """
    Retrieve a list of installed model names from Ollama.

    Returns:
        list[str]: List of model names.
    """
    return [model.model for model in ollama.list().get('models', [])]

def get_llm_response(prompt: str, stream=True, model=None):
    """
    Generate a response from the selected LLM model using a given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        generator: A generator yielding response chunks from the LLM.
    """
    # If OpenAI API key is set, use GPT-4.1 nano via OpenAI Python >=1.0.0
    # If OpenAI API key is set, use GPT-4.1 nano via OpenAI Python >=1.0.0
    if os.getenv("OPENAI_API_KEY"):
        try:
            import openai
        except ImportError:
            raise RuntimeError("OPENAI_API_KEY set but openai package not installed")
        openai.api_key = os.environ["OPENAI_API_KEY"]
        # Debug: show the outgoing prompt
        print(f"[LLM][OpenAI] Prompt: {prompt}")
        if stream:
            resp = openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            # Debug: streaming response object
            print(f"[LLM][OpenAI] Streaming response object: {resp}")
            def event_stream():
                for chunk in resp:
                    choice = chunk.choices[0]
                    delta = getattr(choice, "delta", None)
                    content = getattr(delta, "content", None) if delta is not None else None
                    if content:
                        # Debug: chunk content
                        print(f"[LLM][OpenAI] Chunk content: {content}")
                        yield content
            return event_stream()
        else:
            resp = openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
            )
            # Debug: raw full response
            print(f"[LLM][OpenAI] Raw response: {resp}")
            try:
                choice = resp.choices[0]
                message = getattr(choice, "message", None)
                content = getattr(message, "content", "") if message is not None else ""
                # Debug: parsed content
                print(f"[LLM][OpenAI] Parsed content: {content}")
                return content
            except Exception as e:
                print(f"[LLM][OpenAI] Error parsing response: {e}")
                return ""
    # Fallback to Ollama if no OpenAI key
    if model is None:
        model_name = st.session_state.get('model')
        if not model_name:
            raise ValueError("No model selected in session state.")
    else:
        model_name = model
    result = ollama.generate(model=model_name, prompt=prompt, stream=stream)
    if stream:
        return result
    else:
        return result['response']

def generate_code_roast(code: str, roast_style: str, detailed: bool = False, type: str = "code snippet", model=None, stream=True):
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
    return get_llm_response(prompt, stream=stream, model=model)