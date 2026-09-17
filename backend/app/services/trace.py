import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trace import TraceRecord


def persist_trace(
    db: Session,
    agent_id: str,
    run_id: str,
    trace: list[dict[str, Any]],
    status: str = "completed",
) -> TraceRecord:
    start_time = datetime.fromisoformat(trace[0]["start_time"]) if trace else datetime.now(timezone.utc)
    end_time = datetime.fromisoformat(trace[-1]["end_time"]) if trace else start_time
    record = TraceRecord(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        run_id=run_id,
        status=status,
        start_time=start_time,
        end_time=end_time,
        duration=max((end_time - start_time).total_seconds(), 0),
        payload=json.dumps({"spans": trace}),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_traces(db: Session, run_id: str) -> list[TraceRecord]:
    return list(db.scalars(select(TraceRecord).where(TraceRecord.run_id == run_id).order_by(TraceRecord.created_at)))