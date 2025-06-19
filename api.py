import os
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
    from fastapi.templating import Jinja2Templates
except ImportError as e:
    raise ImportError(
        "fastapi and its dependencies are required. "
        "Install with 'pip install fastapi uvicorn[standard]'"
    ) from e
import html
templates = Jinja2Templates(directory="templates")
from pydantic import BaseModel
from typing import List, Optional
import ollama
import config
from utils.parser import parse_full_github_user, parse_repo
from utils.summarize_git import critique_code_dict

# App instance
app = FastAPI(title="Roast My Code UI and API")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main Roast My Code UI."""
    models = list_models()
    roast_styles = [r["name"] for r in config.ROAST_STYLES]
    examples = config.EXAMPLE_SNIPPETS
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "models": models, "roast_styles": roast_styles, "examples": examples},
    )

@app.get("/example", response_class=HTMLResponse)
async def example_code(title: str):
    """Return a textarea with the selected example code."""
    snippet = next((ex for ex in config.EXAMPLE_SNIPPETS if ex["title"] == title), None)
    if not snippet:
        raise HTTPException(status_code=404, detail="Example not found")
    code = snippet["code"]
    escaped = html.escape(code)
    return HTMLResponse(f'<div id="codeArea"><textarea id="code" name="code" rows="10">{escaped}</textarea></div>')

@app.post("/roast/code-snippet-html", response_class=HTMLResponse)
async def roast_code_snippet_html(request: Request):
    """Handle form submission to roast a code snippet and return HTML."""
    form = await request.form()
    code = form.get("code", "")
    roast_style = form.get("roast_style", "")
    model = form.get("model", list_models()[0])
    detailed = "detailed" in form
    roast_style_mod = roast_style + (" (mention specific files)" if detailed else " (use at most 3 sentences)")
    prompt = config.PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code, roast_style=roast_style_mod)
    try:
        gen = ollama.generate(model=model, prompt=prompt, stream=False)
        content = "".join(chunk.get("response", "") for chunk in gen)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating roast: {e}")
    escaped = html.escape(content)
    return HTMLResponse(f"<div id=\"roastResult\"><pre>{escaped}</pre></div>")

# Initialize Ollama client (default to localhost)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ollama.Client(host=OLLAMA_HOST)

def list_models() -> List[str]:
    resp = ollama.list().get("models", [])
    models = []
    for m in resp:
        if hasattr(m, "model"):
            models.append(m.model)
        elif isinstance(m, dict) and "model" in m:
            models.append(m["model"])
    return models

class CodeRoastRequest(BaseModel):
    code: str
    roast_style: str
    model: Optional[str] = None
    detailed: bool = False
    stream: bool = True

class GitHubRoastRequest(BaseModel):
    profile: str
    repository: Optional[str] = None
    roast_style: str
    model: Optional[str] = None
    detailed: bool = False
    stream: bool = True

@app.get("/models")
def get_models():
    try:
        return {"models": list_models()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/roast_styles")
def get_roast_styles():
    return {"roast_styles": config.ROAST_STYLES}

@app.get("/examples")
def get_examples():
    return {"examples": config.EXAMPLE_SNIPPETS}

@app.post("/roast/code-snippet")
async def roast_code_snippet(request: CodeRoastRequest):
    models = list_models()
    if not models:
        raise HTTPException(status_code=400, detail="No models available")
    model = request.model or models[0]
    roast_style_mod = (
        request.roast_style
        + (" (mention specific files)" if request.detailed else " (use at most 3 sentences)")
    )
    prompt = config.PROMPT_CODE_SNIPPET_TEMPLATE.format(
        code=request.code, roast_style=roast_style_mod
    )
    try:
        gen = ollama.generate(model=model, prompt=prompt, stream=request.stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating roast: {e}")
    if request.stream:
        def iter_response():
            for chunk in gen:
                yield chunk.get("response", "")
        return StreamingResponse(iter_response(), media_type="text/plain")
    content = "".join(chunk.get("response", "") for chunk in gen)
    return JSONResponse({"roast": content})

@app.post("/roast/github-profile")
async def roast_github_profile(request: GitHubRoastRequest):
    try:
        if request.repository:
            code_dict = parse_repo(
                request.profile,
                request.repository,
                depth=(1 if not request.detailed else 2),
            )
        else:
            code_dict = parse_full_github_user(
                request.profile, depth=(0 if not request.detailed else 1)
            )
        summary = critique_code_dict(code_dict)
        snippet = "\n".join(f"{k}: {v}" for k, v in summary.items())
        snippet += f"\nSummary for the user {request.profile}:"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching or summarizing code: {e}")
    models = list_models()
    if not models:
        raise HTTPException(status_code=400, detail="No models available")
    model = request.model or models[0]
    roast_style_mod = (
        request.roast_style
        + (" (mention specific files)" if request.detailed else " (use at most 3 sentences)")
    )
    prompt = config.PROMPT_GITHUB_PROFILE_TEMPLATE.format(
        code=snippet, roast_style=roast_style_mod
    )
    try:
        gen = ollama.generate(model=model, prompt=prompt, stream=request.stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating roast: {e}")
    if request.stream:
        def iter_response():
            for chunk in gen:
                yield chunk.get("response", "")
        return StreamingResponse(iter_response(), media_type="text/plain")
    content = "".join(chunk.get("response", "") for chunk in gen)
    return JSONResponse({"roast": content})