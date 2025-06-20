from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import ollama
import os
from fastapi.staticfiles import StaticFiles

from utils.speech import pipeline, cleanup_prompt, generate_tts_audio
from utils.db import insert_clapback, get_clapback, get_remaining_credits, increment_credits, decrement_credits, reset_credits
from utils.stripe import create_checkout_session, process_webhook

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
    # Fetch remaining pay-it-forward credits
    credits_remaining = get_remaining_credits()
    # Pass Stripe publishable key and price ID for Checkout
    stripe_pk = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "examples": EXAMPLE_SNIPPETS,
        "models": models,
        "roast_styles": roast_styles,
        "voices": VOICES,
        "default_voice": DEFAULT_VOICE,
        "credits_remaining": credits_remaining,
        "stripe_pk": stripe_pk,
    })


@app.get("/example", response_class=HTMLResponse)
async def example(example: str):
    snippet = next((ex for ex in EXAMPLE_SNIPPETS if ex['title'] == example), None)
    code = snippet['code'] if snippet else ""
    html = f"""<div id=\"codeArea\">\n<textarea id=\"code\" name=\"code\" rows=\"10\">{code}</textarea>\n</div>"""
    return HTMLResponse(content=html)
  
@app.post("/create-checkout-session")
async def create_checkout_session_route(request: Request):
    """HTTP endpoint to create a Stripe Checkout Session."""
    data = await request.json()
    success_url = request.url_for("index")
    cancel_url = request.url_for("index")
    session_id = create_checkout_session(
        dollars=data.get("dollars", 0),
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return JSONResponse({"sessionId": session_id})
  
@app.post("/credits/reset", response_class=HTMLResponse)
async def credits_reset(request: Request):
    """Reset the roast counter to zero and return updated HTML snippet."""
    reset_credits()
    remaining = get_remaining_credits()
    html = f"""
    <div id=\"credits\" style=\"margin: 1rem 0;\" hx-get=\"/credits\" hx-trigger=\"every 10s\" hx-swap=\"outerHTML\">
      Roasts Remaining: <span id=\"credit-count\">{remaining}</span>
      <button hx-post=\"/credits/update?delta=1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">+1</button>
      <button hx-post=\"/credits/update?delta=-1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">-1</button>
      <button hx-post=\"/credits/reset\" hx-target=\"#credits\" hx-swap=\"outerHTML\">Reset</button>
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/webhook")
async def stripe_webhook_route(request: Request):
    """HTTP endpoint to receive Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    process_webhook(
        payload=payload,
        sig_header=sig_header,
        webhook_secret=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
    )
    return JSONResponse({"status": "success"})

@app.get("/share/{clapback_id}", response_class=HTMLResponse, name="share_clapback")
async def share_clapback(request: Request, clapback_id: int):
    cb = get_clapback(clapback_id)
    if not cb:
        return HTMLResponse(content="Clapback not found", status_code=404)
    return templates.TemplateResponse("share.html", {"request": request, "clapback": cb})
  
@app.post("/credits/update", response_class=HTMLResponse)
async def update_credits(request: Request, delta: int = 0):
    """Adjust the pay-it-forward credit counter by delta and return updated HTML snippet."""
    # Handle delta from query string (?delta=1 or -1)
    try:
        # If delta not provided or invalid, default 0
        delta = int(request.query_params.get('delta', delta))
    except ValueError:
        delta = 0
    # Apply increment or decrement
    if delta > 0:
        increment_credits(delta)
    elif delta < 0:
        # For negative, attempt to decrement that many times
        for _ in range(abs(delta)):
            if not decrement_credits():
                break
    remaining = get_remaining_credits()
    # Return updated credits HTML
    html = f"""
    <div id=\"credits\" style=\"margin: 1rem 0;\" hx-get=\"/credits\" hx-trigger=\"every 10s\" hx-swap=\"outerHTML\">
      Roasts Remaining: <span id=\"credit-count\">{remaining}</span>
      <button hx-post=\"/credits/update?delta=1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">+1</button>
      <button hx-post=\"/credits/update?delta=-1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">-1</button>
      <button hx-post=\"/credits/reset\" hx-target=\"#credits\" hx-swap=\"outerHTML\">Reset</button>
    </div>
    """
    return HTMLResponse(content=html)
  
@app.get("/credits", response_class=HTMLResponse)
async def get_credits(request: Request):
    """Return the current credits HTML snippet for periodic polling."""
    remaining = get_remaining_credits()
    html = f"""
    <div id=\"credits\" style=\"margin: 1rem 0;\" hx-get=\"/credits\" hx-trigger=\"every 10s\" hx-swap=\"outerHTML\">
      Roasts Remaining: <span id=\"credit-count\">{remaining}</span>
      <button hx-post=\"/credits/update?delta=1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">+1</button>
      <button hx-post=\"/credits/update?delta=-1\" hx-target=\"#credits\" hx-swap=\"outerHTML\">-1</button>
      <button hx-post=\"/credits/reset\" hx-target=\"#credits\" hx-swap=\"outerHTML\">Reset</button>
    </div>
    """
    return HTMLResponse(content=html)

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
    # Enforce pay-it-forward credit counter
    if not decrement_credits():
        return HTMLResponse(content="<div style='color:red;'>Out of credits. Please add more credits to continue.</div>", status_code=402)
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
    # Enforce pay-it-forward credit counter
    if not decrement_credits():
        return HTMLResponse(content="<div style='color:red;'>Out of credits. Please add more credits to continue.</div>", status_code=402)
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