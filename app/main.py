from __future__ import annotations

from fastapi import FastAPI

from app.routes import agent, cases

app = FastAPI(title="Tax Copilot API", version="0.1.0")

app.include_router(cases.router)
app.include_router(agent.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
