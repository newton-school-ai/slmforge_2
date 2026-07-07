from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect

from slmforge.api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_builds_unimplemented() -> None:
    r = client.get("/builds")
    assert r.status_code == 501
    assert r.json() == {"detail": "Not implemented"}


def test_get_build_unimplemented() -> None:
    r = client.get("/builds/build_2026_06_10_142231")
    assert r.status_code == 501
    assert r.json() == {"detail": "Not implemented"}


def test_post_builds_happy_path() -> None:
    valid_payload = {
        "sources": [
            {"type": "local", "path": "/data/train.jsonl"},
            {"type": "public", "id": "cnn_dailymail"},
            {"type": "synthetic", "generator": "feedback_summariser", "size": 20000, "seed": 42},
            {"type": "internal"},
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=valid_payload)
    # The endpoint validates the payload first, then returns 501 Not Implemented.
    assert r.status_code == 501
    assert r.json() == {"detail": "Not implemented"}


@pytest.mark.parametrize(
    "invalid_payload",
    [
        # Missing fields (lora, training, eval, etc.)
        {
            "sources": [{"type": "local", "path": "/data/train.jsonl"}],
            "task_type": "summarisation",
            "base_model": "auto",
        },
        # Invalid task_type
        {
            "sources": [{"type": "local", "path": "/data/train.jsonl"}],
            "task_type": "invalid_task",
            "base_model": "auto",
            "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
            "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
            "eval": {"llm_judge": False},
        },
        # Invalid source type
        {
            "sources": [{"type": "invalid_source"}],
            "task_type": "summarisation",
            "base_model": "auto",
            "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
            "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
            "eval": {"llm_judge": False},
        },
        # Local source missing path
        {
            "sources": [{"type": "local"}],
            "task_type": "summarisation",
            "base_model": "auto",
            "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
            "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
            "eval": {"llm_judge": False},
        },
        # Public source missing id
        {
            "sources": [{"type": "public"}],
            "task_type": "summarisation",
            "base_model": "auto",
            "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
            "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
            "eval": {"llm_judge": False},
        },
        # Synthetic source missing generator or size
        {
            "sources": [{"type": "synthetic", "generator": "feedback_summariser"}],
            "task_type": "summarisation",
            "base_model": "auto",
            "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
            "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
            "eval": {"llm_judge": False},
        },
    ],
)
def test_post_builds_invalid_payload(invalid_payload: dict) -> None:
    r = client.post("/builds", json=invalid_payload)
    assert r.status_code == 422


def test_websocket_stream_unimplemented() -> None:
    # Testing websocket when it is unimplemented (handshake fails with 501 status)
    with pytest.raises((WebSocketDisconnect, Exception)):
        with client.websocket_connect("/builds/build_2026_06_10_142231/stream") as websocket:
            # If it somehow gets past handshake, try to receive/send to trigger close/error
            websocket.send_text("ping")
            websocket.receive_text()
