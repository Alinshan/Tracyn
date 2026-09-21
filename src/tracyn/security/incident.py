from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import EventRecord, IncidentRecord
from ..database.repositories import Repository


class IncidentManager:
    def __init__(self, repository: Repository):
        self.repo = repository

    def process_event(self, event: EventRecord) -> Optional[IncidentRecord]:
        # If event severity is HIGH or CRITICAL, group into an incident
        if event.severity in ["HIGH", "CRITICAL"] or event.risk_score >= 50:
            incident = self.repo.get_or_create_active_incident(severity=event.severity)
            self.repo.add_event_to_incident(incident, event)
            return incident
        return None

    def update_status(self, incident_id: str, status: str, analyst_notes: str = None) -> Optional[IncidentRecord]:
        inc = self.repo.get_incident_by_id(incident_id)
        if inc:
            inc.status = status
            if analyst_notes:
                if inc.analyst_notes:
                    inc.analyst_notes += f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {analyst_notes}"
                else:
                    inc.analyst_notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {analyst_notes}"
            if status in ["RESOLVED", "FALSE_POSITIVE"]:
                inc.resolved_at = datetime.utcnow()
            self.repo.session.commit()
        return inc
