from fastapi import FastAPI

from graph_app import build_graph
from .routes.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="LangGraph Agentic Assistant", version="0.1.0")
    app.state.graph = build_graph(model_name="gpt-4.1-nano")
    app.include_router(chat_router)
    return app


app = create_app()
