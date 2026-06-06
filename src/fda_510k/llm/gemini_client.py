from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

from fda_510k.config import settings

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or settings.google_api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.model = model or settings.gemini_model
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.1) -> str:
        if not self.is_available():
            raise RuntimeError("Google API key not configured. Set GOOGLE_API_KEY in .env or Streamlit secrets.")

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{GEMINI_API_BASE}/models/{self.model}:generateContent"
        resp = httpx.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {data}")

        parts = candidates[0].get("content", {}).get("parts") or []
        text_parts = [part.get("text", "") for part in parts if part.get("text")]
        if not text_parts:
            raise RuntimeError(f"Gemini returned empty content: {data}")

        return "".join(text_parts)

    @staticmethod
    def _extract_json(text: str) -> Any:
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            return json.loads(match.group(1).strip())
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}")

    def generate_json(
        self,
        prompt: str,
        *,
        system: str | None = None,
        retries: int = 2,
    ) -> Any:
        system_prompt = (system or "") + "\nRespond with valid JSON only. No markdown."
        last_error: Exception | None = None
        for _ in range(retries + 1):
            try:
                raw = self.generate(prompt, system=system_prompt.strip(), temperature=0.0)
                return self._extract_json(raw)
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
        raise ValueError(f"Failed to get valid JSON after {retries + 1} attempts") from last_error
