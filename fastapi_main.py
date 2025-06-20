from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ollama
import os
import uuid
import numpy as np
import soundfile as sf
from fastapi.staticfiles import StaticFiles

from utils.speech import pipeline, cleanup_prompt
from utils.db import insert_clapback, get_clapback

from config import EXAMPLE_SNIPPETS, ROAST_STYLES, VOICES, DEFAULT_VOICE
from utils.parser import parse_full_github_user, parse_repo
from utils.summarize_git import critique_code_dict
from utils.llm import generate_code_roast, get_model_names

app = FastAPI()
os.makedirs("tts", exist_ok=True)
app.mount("/tts", StaticFiles(directory="tts"), name="tts")
templates = Jinja2Templates(directory="templates")

if "OLLAMA_HOST" in os.environ:
    ollama.Client(host=os.environ["OLLAMA_HOST"])

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    models = get_model_names()
    # Pass only style names to the template; descriptions are applied server-side
    roast_styles = [r['name'] for r in ROAST_STYLES]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "examples": EXAMPLE_SNIPPETS,
        "models": models,
        "roast_styles": roast_styles,
        "voices": VOICES,
        "default_voice": DEFAULT_VOICE
    })

def generate_tts_audio(text: str, voice: str) -> str:
    """
    Generate TTS audio from text and save to tts directory, returning URL path.
    """
    # remove emojis and prepare text for TTS
    cleaned_text = cleanup_prompt(text)
    segments = []
    for _, _, audio in pipeline(cleaned_text, voice=voice):
        segments.append(audio)
    if segments:
        data = np.concatenate(segments)
    else:
        data = np.array([], dtype='float32')
    audio_id = str(uuid.uuid4())
    filename = f"{audio_id}.wav"
    filepath = os.path.join("tts", filename)
    sf.write(filepath, data, 24000)
    return f"/tts/{filename}"

@app.get("/example", response_class=HTMLResponse)
async def example(example: str):
    snippet = next((ex for ex in EXAMPLE_SNIPPETS if ex['title'] == example), None)
    code = snippet['code'] if snippet else ""
    html = f"""<div id=\"codeArea\">\n<textarea id=\"code\" name=\"code\" rows=\"10\">{code}</textarea>\n</div>"""
    return HTMLResponse(content=html)

@app.get("/share/{clapback_id}", response_class=HTMLResponse, name="share_clapback")
async def share_clapback(request: Request, clapback_id: int):
    cb = get_clapback(clapback_id)
    if not cb:
        return HTMLResponse(content="Clapback not found", status_code=404)
    return templates.TemplateResponse("share.html", {"request": request, "clapback": cb})

@app.post("/roast/code-snippet-html", response_class=HTMLResponse)
async def roast_code_snippet(
    request: Request,
    code: str = Form(...),
    model: str = Form(...),
    roast_style: str = Form(...),
    detailed: str = Form(None),
    tts: str = Form(None),
    voice: str = Form(DEFAULT_VOICE)
):
    detailed_bool = bool(detailed)
    # include the human-readable description in the roast style
    style_def = next((r for r in ROAST_STYLES if r['name'] == roast_style), None)
    roast_style_full = f"{style_def['name']} ({style_def['description']})" if style_def else roast_style
    # generate roast via utils.llm (uses OpenAI or Ollama under the hood)
    roast_text = generate_code_roast(
        code,
        roast_style_full,
        detailed=detailed_bool,
        type="code snippet",
        model=model,
        stream=False
    )
    html = f"<pre>{roast_text}</pre>"
    audio_url = None
    if tts:
        audio_url = generate_tts_audio(roast_text, voice)
        html += f"<audio controls autoplay src=\"{audio_url}\"></audio>"
    clapback_id = insert_clapback(roast_text, audio_url)
    share_url = request.url_for("share_clapback", clapback_id=clapback_id)
    html += f"<div><a href=\"{share_url}\" target=\"_blank\">Share this clapback</a></div>"
    return HTMLResponse(content=html)

@app.post("/roast/github-profile-html", response_class=HTMLResponse)
async def roast_github_profile(
    request: Request,
    profile: str = Form(...),
    repository: str = Form(""),
    model: str = Form(...),
    roast_style: str = Form(...),
    detailed: str = Form(None),
    tts: str = Form(None),
    voice: str = Form(DEFAULT_VOICE)
):
    detailed_bool = bool(detailed)
    if not repository:
        code_dict = parse_full_github_user(profile, depth=1 if detailed_bool else 0)
    else:
        code_dict = parse_repo(profile, repository, depth=2 if detailed_bool else 1)
    summary_dict = critique_code_dict(code_dict)
    summary_text = "\n".join(f"{k}: {v}" for k, v in summary_dict.items())
    summary_text += f"\nSummary for the user {profile}:"
    # include the human-readable description in the roast style
    style_def = next((r for r in ROAST_STYLES if r['name'] == roast_style), None)
    roast_style_full = f"{style_def['name']} ({style_def['description']})" if style_def else roast_style
    # generate roast via utils.llm (uses OpenAI or Ollama under the hood)
    roast_text = generate_code_roast(
        summary_text,
        roast_style_full,
        detailed=detailed_bool,
        type="github profile",
        model=model,
        stream=False
    )
    html = f"<pre>{roast_text}</pre>"
    audio_url = None
    if tts:
        audio_url = generate_tts_audio(roast_text, voice)
        html += f"<audio controls autoplay src=\"{audio_url}\"></audio>"
    clapback_id = insert_clapback(roast_text, audio_url)
    share_url = request.url_for("share_clapback", clapback_id=clapback_id)
    html += f"<div><a href=\"{share_url}\" target=\"_blank\">Share this clapback</a></div>"
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_main:app", host="0.0.0.0", port=8000, reload=True)