from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ollama
import os

from config import EXAMPLE_SNIPPETS, ROAST_STYLES
from utils.parser import parse_full_github_user, parse_repo
from utils.summarize_git import critique_code_dict
from utils.llm import generate_code_roast, get_model_names

app = FastAPI()
templates = Jinja2Templates(directory="templates")

if "OLLAMA_HOST" in os.environ:
    ollama.Client(host=os.environ["OLLAMA_HOST"])

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    models = get_model_names()
    roast_styles = [r['name'] for r in ROAST_STYLES]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "examples": EXAMPLE_SNIPPETS,
        "models": models,
        "roast_styles": roast_styles
    })

@app.get("/example", response_class=HTMLResponse)
async def example(example: str):
    snippet = next((ex for ex in EXAMPLE_SNIPPETS if ex['title'] == example), None)
    code = snippet['code'] if snippet else ""
    html = f"""<div id=\"codeArea\">\n<textarea id=\"code\" name=\"code\" rows=\"10\">{code}</textarea>\n</div>"""
    return HTMLResponse(content=html)

@app.post("/roast/code-snippet-html", response_class=HTMLResponse)
async def roast_code_snippet(
    request: Request,
    code: str = Form(...),
    model: str = Form(...),
    roast_style: str = Form(...),
    detailed: str = Form(None)
):
    detailed_bool = bool(detailed)
    roast_text = generate_code_roast(
        code,
        roast_style,
        detailed=detailed_bool,
        type="code snippet",
        model=model,
        stream=False
    )
    html = f"<pre>{roast_text}</pre>"
    return HTMLResponse(content=html)

@app.post("/roast/github-profile-html", response_class=HTMLResponse)
async def roast_github_profile(
    request: Request,
    profile: str = Form(...),
    repository: str = Form(""),
    model: str = Form(...),
    roast_style: str = Form(...),
    detailed: str = Form(None)
):
    detailed_bool = bool(detailed)
    if not repository:
        code_dict = parse_full_github_user(profile, depth=1 if detailed_bool else 0)
    else:
        code_dict = parse_repo(profile, repository, depth=2 if detailed_bool else 1)
    summary_dict = critique_code_dict(code_dict)
    summary_text = "\n".join(f"{k}: {v}" for k, v in summary_dict.items())
    summary_text += f"\nSummary for the user {profile}:"
    roast_text = generate_code_roast(
        summary_text,
        roast_style,
        detailed=detailed_bool,
        type="github profile",
        model=model,
        stream=False
    )
    html = f"<pre>{roast_text}</pre>"
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_main:app", host="0.0.0.0", port=8000, reload=True)