import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from slmforge.engine.state import Base, Build, Run, Source, Dataset, Eval, Serve


@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_all_models_create_and_read(db_session):
    # 1. Build
    build = Build(
        name="my-first-build",
        base_model="microsoft/Phi-3-mini-4k-instruct",
        lora_config={"r": 16},
        status="pending",
    )
    db_session.add(build)
    db_session.commit()
    db_session.refresh(build)
    assert build.id is not None
    assert build.name == "my-first-build"

    # 2. Run
    run = Run(build_id=build.id, epochs_completed=2, loss=0.84, gpu_usage=92.5, status="completed")
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    assert run.id is not None
    assert run.build_id == build.id

    # 3. Source
    source = Source(build_id=build.id, source_type="public", url="cnn_dailymail", record_count=1000)
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    assert source.id is not None
    assert source.source_type == "public"

    # 4. Dataset
    dataset = Dataset(
        build_id=build.id, train_split="train_split.jsonl", processing_config={"epochs": 2}
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    assert dataset.id is not None
    assert dataset.train_split == "train_split.jsonl"

    # 5. Eval
    eval_metric = Eval(build_id=build.id, rouge_score=0.62, accuracy=0.91, verdict="passed")
    db_session.add(eval_metric)
    db_session.commit()
    db_session.refresh(eval_metric)
    assert eval_metric.id is not None
    assert eval_metric.verdict == "passed"

    # 6. Serve
    serve = Serve(
        build_id=build.id, model_path="builds/build_1/adapter", port=8000, status="active"
    )
    db_session.add(serve)
    db_session.commit()
    db_session.refresh(serve)
    assert serve.id is not None
    assert serve.port == 8000
