from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.graph import weather_bot_graph


app = FastAPI(
    title="Weather Advisory Support Bot",
    description=(
        "A policy-driven weather advisory system using "
        "LangGraph, live weather data, and external YAML SOPs."
    ),
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        description="The user's weather-related question.",
    )

    session_id: str = Field(
        default="default",
        description="Identifier used to maintain conversation context.",
    )


class ChatAPIResponse(BaseModel):
    reply: str
    protocol_id: str | None = None
    severity: str | None = None


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post(
    "/chat",
    response_model=ChatAPIResponse,
)
def chat(request: ChatRequest):

    result = weather_bot_graph.invoke(
        {
            "message": request.message,
            "session_id": request.session_id,
        }
    )

    selected_sop = result.get("selected_sop")

    return ChatAPIResponse(
        reply=result["reply"],
        protocol_id=(
            selected_sop.id
            if selected_sop
            else None
        ),
        severity=(
            selected_sop.severity
            if selected_sop
            else None
        ),
    )


# -------------------------------------------------
# Serve React frontend
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


if FRONTEND_DIST.exists():

    # Serve Vite-generated JS, CSS and other assets
    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="assets",
    )

    # Serve React application
    @app.get("/")
    async def serve_frontend():
        return FileResponse(
            FRONTEND_DIST / "index.html"
        )