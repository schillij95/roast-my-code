import os
import requests
import base64
import json
from tqdm import tqdm

# -----------------------------
# CONFIGURATION
# -----------------------------
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("GitHub token not found. Set the GITHUB_TOKEN environment variable.")

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
        '.java', '.c', '.cpp', '.sh', '.go', '.rs', '.yml', '.yaml'
    )
    return file_name.lower().endswith(text_extensions)

# -----------------------------
# FETCH REPO CONTENTS
# -----------------------------
def fetch_repo_contents(owner, repo, path=""):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# -----------------------------
# PARSE A REPOSITORY
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
# FETCH PINNED REPOS (GraphQL)
# -----------------------------
def fetch_pinned_repos(username):
    url = f"{GITHUB_API_URL}/graphql"
    query = """
    query($login: String!) {
      user(login: $login) {
        pinnedItems(first: 6, types: REPOSITORY) {
          nodes {
            ... on Repository {
              name
              owner {
                login
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"query": query, "variables": {"login": username}}
    )

    response.raise_for_status()
    data = response.json()

    try:
        pinned_repos = data["data"]["user"]["pinnedItems"]["nodes"]
        return [(repo["owner"]["login"], repo["name"]) for repo in pinned_repos]
    except Exception as e:
        print(f"Error parsing pinned repos: {e}")
        return []

# -----------------------------
# PARSE PINNED REPOS
# -----------------------------
def parse_user_pinned_repos(username, depth=2):
    parsed_results = {}
    pinned = fetch_pinned_repos(username)

    if not pinned:
        print(f"No pinned repos found for {username}")
        return parsed_results, pinned

    for owner, repo in pinned:
        print(f"\nParsing pinned repo: {owner}/{repo}")
        parsed_results["pinned repository " + repo] = parse_repo(owner, repo, depth=depth)

    return parsed_results, pinned

# -----------------------------
# PARSE Most ACTIVE REPOS
# -----------------------------
def parse_most_active_repos(username, previously_parsed, depth=2):
    print(f"Fetching most active repos for {username}...")
    # Gather all public repos
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        page_data = response.json()
        if not page_data:
            break
        repos.extend(page_data)
        page += 1

    # Sort by stars and recent update
    sorted_stars = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)
    sorted_recent = sorted(repos, key=lambda r: r.get('updated_at', ''), reverse=True)

    # Combine top 2 of each, excluding already parsed
    combined = []
    seen = set()
    for repo in sorted_stars[:2] + sorted_recent[:2]:
        key = (repo['owner']['login'], repo['name'])
        if key in previously_parsed or key in seen:
            continue
        seen.add(key)
        combined.append(repo)

    # Parse each selected repo
    parsed_results = {}
    for repo in combined:
        owner = repo['owner']['login']
        name = repo['name']
        print(f"\nParsing most active repo: {owner}/{name}")
        parsed_results[f"other relevant user's repository {name}"] = parse_repo(owner, name, depth=depth)

    return parsed_results

# -----------------------------
# FETCH GITHUB PROFILE INFO
# -----------------------------
def fetch_github_profile(username):
    profile_data = {}

    # Basic profile info
    user_url = f"{GITHUB_API_URL}/users/{username}"
    user_res = requests.get(user_url, headers=HEADERS)
    user_res.raise_for_status()
    user_info = user_res.json()

    profile_data["profile"] = {
        "login": user_info.get("login"),
        "name": user_info.get("name"),
        "bio": user_info.get("bio"),
        "location": user_info.get("location"),
        "blog": user_info.get("blog"),
        "email": user_info.get("email"),
        "twitter": user_info.get("twitter_username"),
        "followers": user_info.get("followers"),
        "following": user_info.get("following"),
        "public_repos": user_info.get("public_repos"),
        "created_at": user_info.get("created_at"),
        "updated_at": user_info.get("updated_at"),
    }

    # List of all public repos
    repos = []
    page = 1
    while True:
        repos_url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=100&page={page}"
        repos_res = requests.get(repos_url, headers=HEADERS)
        repos_res.raise_for_status()
        page_data = repos_res.json()
        if not page_data:
            break
        repos.extend(page_data)
        page += 1

    profile_data["repos"] = [
        {
            "name of listed Repository": r["name"],
            "description": r["description"],
            "language": r["language"],
            "stargazers_count": r["stargazers_count"],
            "updated_at": r["updated_at"],
        }
        for r in repos
    ]

    # Public activity (last 10)
    events_url = f"{GITHUB_API_URL}/users/{username}/events/public"
    events_res = requests.get(events_url, headers=HEADERS)
    profile_data["recent_activity"] = []
    if events_res.status_code == 200:
        events = events_res.json()
        profile_data["recent_activity"] = [
            {
                "type": e["type"],
                "repo": e.get("repo", {}).get("name"),
                "created_at": e["created_at"]
            }
            for e in events[:10]
        ]

    return profile_data

# -----------------------------
# PARSE FULL USER PROFILE + CODE
# -----------------------------
def parse_full_github_user(username, depth=1):
    print(f"Fetching profile for: {username}")
    profile_info = fetch_github_profile(username)

    print(f"\nFetching and parsing pinned repos...")
    pinned_repos_data, pinned_repositories = parse_user_pinned_repos(username, depth=depth)
    relevant_repos_data = parse_most_active_repos(username, pinned_repositories, depth=depth)

    return {
        "profile_info": profile_info,
        "pinned_repos_code": pinned_repos_data,
        "relevant_repos_code": relevant_repos_data,
    }

# -----------------------------
# MAIN SCRIPT
# -----------------------------
if __name__ == "__main__":
    github_user = "schillij95"  # Replace with any GitHub username

    full_data = parse_full_github_user(github_user, depth=2)

    with open(f"{github_user}_full_profile.json", "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2)

    print(f"\n✅ Saved complete profile to {github_user}_full_profile.json")
