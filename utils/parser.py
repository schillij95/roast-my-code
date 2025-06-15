import os
import requests
import base64
from tqdm import tqdm
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
GITHUB_API_URL = "https://api.github.com/repos"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found. Set the GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# -----------------------------
# FILE TYPE FILTER
# -----------------------------
def is_text_file(file_name):
    text_extensions = (
        '.txt', '.md', '.py', '.js', '.ts', '.json', '.html', '.css',
        '.java', '.c', '.cpp', '.sh', '.go', '.rs'
    )
    return file_name.lower().endswith(text_extensions)

# -----------------------------
# FETCH REPO CONTENTS
# -----------------------------
def fetch_repo_contents(owner, repo, path=""):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# -----------------------------
# PARSE REPO RECURSIVELY
# -----------------------------
def parse_repo(owner, repo, path="", depth=2):
    repo_dict = {}
    if depth < 0:
        return repo_dict

    try:
        items = fetch_repo_contents(owner, repo, path)
    except Exception as e:
        print(f"Failed to fetch {path}: {e}")
        return repo_dict

    for item in tqdm(items, desc=f"Parsing {owner}/{repo}/{path or '.'}", unit="item"):
        item_path = item['path']
        item_type = item['type']
        item_size = item.get('size', 0)

        if item_type == 'file' and is_text_file(item['name']) and item_size < 1_000_000:
            try:
                file_data = requests.get(item['url'], headers=HEADERS).json()
                if file_data.get('encoding') == 'base64':
                    content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                    repo_dict[item['name']] = content
            except Exception as e:
                print(f"Error reading {item_path}: {e}")

        elif item_type == 'dir' and depth > 0:
            repo_dict[item['name']] = parse_repo(owner, repo, item_path, depth - 1)

    return repo_dict

# -----------------------------
# EXAMPLE USAGE
# -----------------------------
if __name__ == "__main__":
    # Example: parse schillij95/ThaumatoAnakalyptor
    owner = "schillij95"
    repo = "ThaumatoAnakalyptor"
    
    print(f"Parsing {owner}/{repo} with max depth of 2...")
    data = parse_repo(owner, repo, depth=2)
    
    # Optionally save result to file
    with open(f"{repo}_parsed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved output to {repo}_parsed.json")
