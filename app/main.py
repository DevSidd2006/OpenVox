from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import (
    add_entry,
    fetch_profile,
    get_app_settings,
    init_db,
    list_entries,
    list_session_entries,
    set_app_setting,
    upsert_profile,
)
from .groq_client import GroqService
from .models import AppSettingModel, ProfileModel, RewriteRequest, RewriteResponse

APP_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = APP_ROOT / "web"

app = FastAPI(title="OpenVox", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/profile", response_model=ProfileModel)
def get_profile() -> ProfileModel:
    return ProfileModel(**fetch_profile())


@app.put("/api/profile", response_model=ProfileModel)
def put_profile(payload: ProfileModel) -> ProfileModel:
    upsert_profile(
        full_name=payload.full_name,
        role=payload.role,
        preferred_tone=payload.preferred_tone,
        writing_rules=payload.writing_rules,
        custom_dictionary=payload.custom_dictionary,
        working_context=payload.working_context,
        default_language=payload.default_language,
    )
    return ProfileModel(**fetch_profile())


@app.get("/api/settings")
def settings_get() -> dict[str, str]:
    return get_app_settings()


@app.put("/api/settings")
def settings_put(payload: AppSettingModel) -> dict[str, str]:
    set_app_setting(payload.key, payload.value)
    return get_app_settings()


@app.post("/api/rewrite", response_model=RewriteResponse)
def rewrite_text(payload: RewriteRequest) -> RewriteResponse:
    try:
        groq = GroqService()
        profile = fetch_profile()
        rewritten = groq.rewrite_text(
            text=payload.text,
            profile=profile,
            style=payload.style,
            context=payload.context,
            language=payload.language,
            history=None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {exc}") from exc

    add_entry(
        source_text=payload.text,
        rewritten_text=rewritten,
        style=payload.style,
        language=payload.language,
        context=payload.context,
    )

    return RewriteResponse(
        original_text=payload.text,
        rewritten_text=rewritten,
        style=payload.style,
        context=payload.context,
        language=payload.language,
    )


@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    style: str = Form("professional"),
    context: str = Form("email"),
    language: str = Form("en"),
    prompt: str = Form(""),
    auto_rewrite: bool = Form(True),
) -> dict:
    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        groq = GroqService()
        profile = fetch_profile()
        transcript = groq.transcribe_audio(
            filename=audio.filename or "input.webm",
            content=raw,
            language=language,
            prompt=prompt,
        )
        rewritten = transcript
        if auto_rewrite:
            rewritten = groq.rewrite_text(
                text=transcript,
                profile=profile,
                style=style,
                context=context,
                language=language,
                history=None,
            )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc

    entry_id = add_entry(
        source_text=transcript,
        rewritten_text=rewritten,
        style=style,
        language=language,
        context=context,
    )

    return {
        "entry_id": entry_id,
        "transcript": transcript,
        "rewritten_text": rewritten,
        "style": style,
        "context": context,
        "language": language,
    }


@app.get("/api/history")
def history(limit: int = 25) -> list[dict]:
    return list_entries(limit=limit)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/api/export")
def export_history() -> JSONResponse:
    profile = fetch_profile()
    entries = list_entries(limit=500)
    return JSONResponse({"profile": profile, "entries": entries})


app.mount("/web", StaticFiles(directory=WEB_ROOT), name="web")
