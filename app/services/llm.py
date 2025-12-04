from __future__ import annotations

import os
from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from app import schemas


SYSTEM_PROMPT = """
You are a United States tax preparation copilot for CPAs. Read and update the case file JSON. Identify missing information and inconsistencies. Suggest clear questions and checklists for the CPA to send to the client. Do not claim to be a CPA and do not file returns.
Return a strict JSON object with keys 'reply' and 'updated_case_file'.
"""


class LLMService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if OpenAI and api_key else None

    def generate_agent_reply(self, message: str, case_file: schemas.CaseFile) -> schemas.AgentResponse:
        if not self.client:
            # Offline fallback: echo message and return existing case file
            return schemas.AgentResponse(
                reply="LLM not configured. Echo: " + message,
                updated_case_file=case_file,
            )

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Case file: {case_file.json()}"},
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"},
        )

        content = response.output[0].content[0].text  # type: ignore[index]
        payload: Dict[str, Any] = schemas.AgentResponse.parse_raw(content).dict()
        return schemas.AgentResponse(**payload)
