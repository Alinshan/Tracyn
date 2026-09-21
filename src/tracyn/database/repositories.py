import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from .models import (
    BaselineFileRecord,
    BaselineRecord,
    ConfigurationRecord,
    EventRecord,
    FileRecord,
    IncidentRecord,
)


class Repository:
    def __init__(self, session: Session):
        self.session = session

    # --- Files ---
    def get_or_create_file(self, path: str, size: int = 0, sha256: str = None, criticality: str = "NORMAL") -> FileRecord:
        file_rec = self.session.query(FileRecord).filter_by(path=path).first()
        filename = path.replace("\\", "/").split("/")[-1]
        ext = filename.split(".")[-1] if "." in filename else ""
        now = datetime.utcnow()

        if not file_rec:
            file_rec = FileRecord(
                path=path,
                filename=filename,
                extension=ext,
                size=size,
                sha256=sha256,
                criticality=criticality,
                first_seen=now,
                last_seen=now
            )
            self.session.add(file_rec)
        else:
            file_rec.size = size
            if sha256:
                file_rec.sha256 = sha256
            file_rec.last_seen = now
        self.session.commit()
        return file_rec

    def get_all_files(self) -> List[FileRecord]:
        return self.session.query(FileRecord).order_by(FileRecord.last_seen.desc()).all()

    # --- Baseline ---
    def create_baseline(self, file_map: Dict[str, str], version: str = "v1.0", description: str = "Initial baseline", tamper_hash: str = None) -> BaselineRecord:
        # Mark existing baselines as ARCHIVED
        self.session.query(BaselineRecord).filter_by(status="ACTIVE").update({"status": "ARCHIVED"})
        
        baseline = BaselineRecord(
            version=version,
            created_at=datetime.utcnow(),
            created_by="system",
            description=description,
            status="ACTIVE",
            sha256=tamper_hash
        )
        self.session.add(baseline)
        self.session.flush()

        for path, hash_val in file_map.items():
            f_rec = self.get_or_create_file(path=path, sha256=hash_val)
            b_file = BaselineFileRecord(
                baseline_id=baseline.id,
                file_id=f_rec.id,
                sha256=hash_val,
                size=f_rec.size
            )
            self.session.add(b_file)

        self.session.commit()
        return baseline

    def get_active_baseline(self) -> Optional[BaselineRecord]:
        return self.session.query(BaselineRecord).filter_by(status="ACTIVE").order_by(BaselineRecord.created_at.desc()).first()

    def get_all_baselines(self) -> List[BaselineRecord]:
        return self.session.query(BaselineRecord).order_by(BaselineRecord.created_at.desc()).all()

    # --- Events ---
    def create_event(
        self,
        event_type: str,
        path: str,
        old_hash: Optional[str] = None,
        new_hash: Optional[str] = None,
        user: str = "UNKNOWN",
        process: str = "UNKNOWN",
        risk_score: int = 0,
        severity: str = "LOW",
        reason: str = "",
        file_id: Optional[int] = None
    ) -> EventRecord:
        evt_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        evt = EventRecord(
            event_id=evt_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            file_id=file_id,
            path=path,
            old_hash=old_hash,
            new_hash=new_hash,
            user=user,
            process=process,
            risk_score=risk_score,
            severity=severity,
            reason=reason,
            status="NEW"
        )
        self.session.add(evt)
        self.session.commit()
        return evt

    def get_all_events(self, limit: int = 100) -> List[EventRecord]:
        return self.session.query(EventRecord).order_by(EventRecord.timestamp.desc()).limit(limit).all()

    def get_event_by_id(self, event_id: str) -> Optional[EventRecord]:
        return self.session.query(EventRecord).filter_by(event_id=event_id).first()

    # --- Incidents ---
    def get_or_create_active_incident(self, severity: str = "HIGH") -> IncidentRecord:
        # Check if there is an active incident created in the last 5 minutes
        five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
        active_inc = (
            self.session.query(IncidentRecord)
            .filter(IncidentRecord.status.in_(["NEW", "INVESTIGATING"]))
            .filter(IncidentRecord.created_at >= five_mins_ago)
            .order_by(IncidentRecord.created_at.desc())
            .first()
        )
        if not active_inc:
            count = self.session.query(IncidentRecord).count() + 1
            inc_num = f"INC-{count:05d}"
            active_inc = IncidentRecord(
                incident_number=inc_num,
                title="Suspicious System Activity Detected",
                description="Multiple file integrity events detected within short time window.",
                severity=severity,
                status="NEW",
                risk_score=0,
                created_at=datetime.utcnow()
            )
            self.session.add(active_inc)
            self.session.commit()
        return active_inc

    def add_event_to_incident(self, incident: IncidentRecord, event: EventRecord):
        if event not in incident.events:
            incident.events.append(event)
            if event.risk_score > incident.risk_score:
                incident.risk_score = event.risk_score
            if event.severity == "CRITICAL" or (event.severity == "HIGH" and incident.severity != "CRITICAL"):
                incident.severity = event.severity
            incident.updated_at = datetime.utcnow()
            self.session.commit()

    def get_all_incidents(self) -> List[IncidentRecord]:
        return self.session.query(IncidentRecord).order_by(IncidentRecord.created_at.desc()).all()

    def get_incident_by_id(self, incident_number: str) -> Optional[IncidentRecord]:
        return self.session.query(IncidentRecord).filter_by(incident_number=incident_number).first()

    # --- Summary Statistics ---
    def get_summary_stats(self) -> Dict:
        total_files = self.session.query(FileRecord).count()
        total_events = self.session.query(EventRecord).count()
        modified_files = self.session.query(EventRecord).filter_by(event_type="MODIFIED").count()
        new_files = self.session.query(EventRecord).filter_by(event_type="NEW_FILE").count()
        deleted_files = self.session.query(EventRecord).filter_by(event_type="DELETED_FILE").count()
        open_incidents = self.session.query(IncidentRecord).filter(IncidentRecord.status.in_(["NEW", "INVESTIGATING", "ACKNOWLEDGED"])).count()
        critical_alerts = self.session.query(EventRecord).filter_by(severity="CRITICAL").count()
        high_alerts = self.session.query(EventRecord).filter_by(severity="HIGH").count()

        # Highest risk score in last events
        recent_events = self.session.query(EventRecord).order_by(EventRecord.timestamp.desc()).limit(20).all()
        max_risk = max([e.risk_score for e in recent_events], default=0)
        
        if max_risk >= 75:
            current_risk_level = "CRITICAL"
        elif max_risk >= 50:
            current_risk_level = "HIGH"
        elif max_risk >= 25:
            current_risk_level = "MEDIUM"
        else:
            current_risk_level = "LOW"

        return {
            "total_files": total_files,
            "modified_files": modified_files,
            "new_files": new_files,
            "deleted_files": deleted_files,
            "total_events": total_events,
            "open_incidents": open_incidents,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "current_risk_score": max_risk,
            "current_risk_level": current_risk_level
        }
