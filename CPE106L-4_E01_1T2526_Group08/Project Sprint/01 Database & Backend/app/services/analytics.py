from datetime import datetime, timedelta
from collections import Counter
from sqlmodel import Session, select
from ..models.models import RideRequest

def rides_per_day(session: Session, days: int = 7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = session.exec(select(RideRequest).where(RideRequest.requested_at >= cutoff)).all()
    counts = Counter(r.requested_at.date().isoformat() for r in rows)
    return [{"date": d, "count": counts[d]} for d in sorted(counts.keys())]

def avg_wait_minutes(session: Session, days: int = 30):
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = session.exec(select(RideRequest).where(RideRequest.requested_at >= cutoff)).all()
    waits = [
        (r.assigned_at - r.requested_at).total_seconds() / 60.0
        for r in rows if r.assigned_at
    ]
    return {"avg_wait_min": round(sum(waits)/len(waits), 2) if waits else 0.0}
