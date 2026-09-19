from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("agentguard", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="agentguard.run_test_run")
def run_test_run(run_id: str, categories: list[str], inputs: list[str] | None = None) -> str:
    from app.db.session import SessionLocal
    from app.models.test_run import TestRun
    from app.evaluation.runner import run_evaluation

    db = SessionLocal()
    try:
        run = db.get(TestRun, run_id)
        if run is None:
            raise ValueError("Test run not found")
        run.status = "running"
        db.commit()
        run_evaluation(db, run, categories, inputs)
        return run_id
    except Exception:
        run = db.get(TestRun, run_id)
        if run is not None:
            run.status = "failed"
            db.commit()
        raise
    finally:
        db.close()