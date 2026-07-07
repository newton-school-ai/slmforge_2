from __future__ import annotations

from typing import Annotated, List, Literal, Optional, Union
from pydantic import BaseModel, Field

# --- Source Schemas ---


class LocalSource(BaseModel):
    type: Literal["local"] = "local"
    path: str


class PublicSource(BaseModel):
    type: Literal["public"] = "public"
    id: str


class SyntheticSource(BaseModel):
    type: Literal["synthetic"] = "synthetic"
    generator: str
    size: int
    seed: Optional[int] = None


class InternalSource(BaseModel):
    type: Literal["internal"] = "internal"


SourceSchema = Annotated[
    Union[LocalSource, PublicSource, SyntheticSource, InternalSource], Field(discriminator="type")
]


# --- Configuration Schemas ---


class LoraConfig(BaseModel):
    r: int
    alpha: int
    dropout: float


class TrainingConfig(BaseModel):
    epochs: int
    batch_size: int
    lr: float


class EvalConfig(BaseModel):
    llm_judge: bool


# --- Build Request Schema ---


class BuildRequest(BaseModel):
    sources: List[SourceSchema]
    task_type: Literal["classification", "summarisation", "qa", "instruction", "chat", "auto"]
    base_model: str
    lora: LoraConfig
    training: TrainingConfig
    eval: EvalConfig


# --- Build Response Event Schemas (for WebSocket stream) ---


class DiscoverSourcesEvent(BaseModel):
    event: Literal["discover_sources"] = "discover_sources"
    files: List[str]


class DetectTaskEvent(BaseModel):
    event: Literal["detect_task"] = "detect_task"
    task_type: Literal["classification", "summarisation", "qa", "instruction", "chat", "auto"]


class PlanEvent(BaseModel):
    event: Literal["plan"] = "plan"
    vram_gb: float
    est_minutes: float


class EpochEvent(BaseModel):
    event: Literal["epoch"] = "epoch"
    epoch: int
    train_loss: float
    val_loss: float


class CheckpointEvent(BaseModel):
    event: Literal["checkpoint"] = "checkpoint"
    path: str


class EvalEvent(BaseModel):
    event: Literal["eval"] = "eval"
    metrics: dict


class CompleteEvent(BaseModel):
    event: Literal["complete"] = "complete"
    build_id: str
    usage_url: str


BuildEvent = Annotated[
    Union[
        DiscoverSourcesEvent,
        DetectTaskEvent,
        PlanEvent,
        EpochEvent,
        CheckpointEvent,
        EvalEvent,
        CompleteEvent,
    ],
    Field(discriminator="event"),
]
