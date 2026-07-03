from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    base_model = Column(String, nullable=False, default="auto")
    lora_config = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    runs = relationship("Run", back_populates="build", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="build", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="build", cascade="all, delete-orphan")
    evals = relationship("Eval", back_populates="build", cascade="all, delete-orphan")
    serves = relationship("Serve", back_populates="build", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=False)
    epochs_completed = Column(Integer, default=0)
    loss = Column(Float, nullable=True)
    gpu_usage = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="running")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    build = relationship("Build", back_populates="runs")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=False)
    source_type = Column(String, nullable=False)  # e.g., local, public, synthetic
    url = Column(String, nullable=False)  # e.g., file path, HF dataset ID, generator name
    record_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    build = relationship("Build", back_populates="sources")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=False)
    train_split = Column(String, nullable=True)
    val_split = Column(String, nullable=True)
    eval_split = Column(String, nullable=True)
    processing_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    build = relationship("Build", back_populates="datasets")


class Eval(Base):
    __tablename__ = "evals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=False)
    rouge_score = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    verdict = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    build = relationship("Build", back_populates="evals")


class Serve(Base):
    __tablename__ = "serves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    build_id = Column(Integer, ForeignKey("builds.id"), nullable=False)
    model_path = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="inactive")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    build = relationship("Build", back_populates="serves")
