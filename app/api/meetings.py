# app/api/meetings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.meeting import Meeting
from app.core.database import get_db
from app.core.security import get_current_user  # ← нужно реализовать (см. ниже)
import json

router = APIRouter(prefix="/api", tags=["meetings"])

@router.get("/meetings")
def get_user_meetings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meetings = db.query(Meeting).filter(Meeting.owner_id == current_user["id"]).all()
    result = []
    for m in meetings:
        res = {
            "id": m.id,
            "filename": m.filename,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        if m.result_json:
            try:
                res["result"] = json.loads(m.result_json)
            except:
                res["result"] = None
        result.append(res)
    return result