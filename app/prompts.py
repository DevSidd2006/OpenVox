from __future__ import annotations

from typing import Iterable


def _bullet_lines(items: Iterable[str]) -> str:
    clean = [item.strip() for item in items if item.strip()]
    if not clean:
        return "- None"
    return "\n".join(f"- {item}" for item in clean)


def rewrite_system_prompt(profile: dict, style: str, context: str, language: str, history: list[dict] | None = None) -> str:
    dictionary_terms = _bullet_lines(profile.get("custom_dictionary", []))
    writing_rules = _bullet_lines(profile.get("writing_rules", []))
    working_context = profile.get("working_context", "").strip()

    working_context_str = f"Current Working Context:\n{working_context}\n" if working_context else ""

    return f"""
You are OpenVox, a writing assistant focused on dictation cleanup.

Rules:
1) Keep user intent unchanged.
2) Preserve names and terms in Custom Dictionary exactly as provided.
3) Apply clean punctuation, sentence boundaries, and readability.
4) Never invent facts.
5) Output only rewritten text in {language}.

User profile:
- Name: {profile.get("full_name", "")}
- Role: {profile.get("role", "")}
- Preferred tone: {profile.get("preferred_tone", "professional")}

Custom Dictionary:
{dictionary_terms}

Additional writing rules:
{writing_rules}

Target style: {style}
Target context: {context}
{working_context_str}
""".strip()


def rewrite_user_prompt(text: str) -> str:
    return f"Rewrite this dictated text:\n\n{text.strip()}"
