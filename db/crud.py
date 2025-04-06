// /backend/db/crud.py
from . import models
from sqlalchemy.orm import Session
from uuid import uuid4
import datetime

def store_tags(db: Session, tags: list, account_id: str):
    for tag in tags:
        log = models.RFIDScanLog(
            id=str(uuid4()),
            rfid_tag=tag,
            scanned_at=datetime.datetime.utcnow(),
            scanned_by="system"  # Replace with actual user ID if needed
        )
        db.add(log)
    db.commit()

def get_recent_tags(db: Session):
    recent = db.query(models.RFIDScanLog).order_by(models.RFIDScanLog.scanned_at.desc()).limit(10).all()
    return [r.rfid_tag for r in recent]