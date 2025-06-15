import ollama
from typing import Dict, Any
from .llm import get_llm_response

# A default prompt to critique code – customize as needed
PROMPT_CODE_SNIPPET_TEMPLATE = """
You are a critical code reviewer. Review the following code and point out only what is wrong, flawed, or could be improved. Be on point but keep it short and concise. Do not include any positive feedback or compliments.

Focus on:
- Poor variable or function names
- Confusing or illogical flow
- Lack of or bad comments
- Unclear structure
- Overengineering or messy code
- Anything that would raise red flags in a real code review
- Anything usefull for a humoristic roast of the repository

Avoid saying anything positive. Be brutally honest.

Code: {code}
Critique:
"""

def critique_code_dict(code_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively critiques code in a nested dict where file contents are strings.
    Replaces each file's content with the LLM's critique.
    """
    result = {}

    for key, value in code_dict.items():
        if isinstance(value, str):
            # This is a file
            prompt = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=value)
            try:
                summary = get_llm_response(prompt)
                result[key] = summary
            except Exception as e:
                print(f"LLM error on file {key}: {e}")
                result[key] = f"Error during LLM evaluation: {e}"
        elif isinstance(value, dict):
            # This is a folder
            result[key] = critique_code_dict(value)
        else:
            result[key] = "Unknown format"

    return result