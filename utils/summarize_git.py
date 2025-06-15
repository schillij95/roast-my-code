import ollama
from typing import Dict, Any
from .llm import get_llm_response
from .parser import is_text_file
from tqdm import tqdm

# A default prompt to critique code – customize as needed
PROMPT_CODE_SNIPPET_TEMPLATE = """
You are a critical code reviewer. Review the following code/README and point out only what is wrong, flawed, or could be improved. Be on point but keep it short and concise. Do not include any positive feedback or compliments.

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

    items = code_dict.items()
    # random shuffle the items to ensure different order each time
    items = list(items)  # Convert to list for tqdm compatibility
    from random import shuffle
    shuffle(items)
    # only use first 10 items for performance
    count = 0
    for key, value in tqdm(items, desc="Critiquing code", unit="file"):
        if isinstance(value, str) and is_text_file(key):
            if count >= 10:
                # Limit to first 10 files for performance
                result[key] = "Critique skipped for performance reasons."
                continue
            count += 1
            max_length = min(1000, len(value))  # Limit to first 10,000 characters for performance
            code = value[:max_length]
            # This is a file
            prompt = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code)
            try:
                summary = get_llm_response(prompt, stream=False)
                result[key] = summary
            except Exception as e:
                result[key] = f"Error during LLM evaluation: {e}"
        elif isinstance(value, dict):
            # This is a folder
            result[key] = critique_code_dict(value)
        else:
            result[key] = str(value)  # Handle other types gracefully

    return result