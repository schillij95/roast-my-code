"""
Environment settings loader.
Loads API keys and other secrets from a .env file in the project root.
"""
from dotenv import load_dotenv
import os

# Load variables from .env (must be at project root)
load_dotenv()

# GitHub token for authenticating to GitHub API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# OpenAI API key for OpenAI Python client (if used)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")