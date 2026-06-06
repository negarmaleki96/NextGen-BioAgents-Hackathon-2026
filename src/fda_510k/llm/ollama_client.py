from __future__ import annotations

import json
import re
from typing import Any

import httpx

from fda_510k.config import settings


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.1) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

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
