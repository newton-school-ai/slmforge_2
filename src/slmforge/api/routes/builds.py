from __future__ import annotations

from fastapi import APIRouter, HTTPException, WebSocket
from slmforge.api.schemas import BuildRequest

router = APIRouter()


@router.post("/builds")
def create_build(payload: BuildRequest) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/builds")
def list_builds() -> None:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/builds/{id}")
def get_build(id: str) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.websocket("/builds/{id}/stream")
async def stream_build(websocket: WebSocket, id: str) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")
