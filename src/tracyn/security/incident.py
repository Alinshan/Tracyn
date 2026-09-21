from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import EventRecord, IncidentRecord
from ..database.repositories import Repository
from .alerts import AlertDispatcher


class IncidentManager:
    def __init__(self, repository: Repository, config: dict = None):
        self.repo = repository
        self.config = config or {}
        self.alert_dispatcher = AlertDispatcher(self.config)

    def process_event(self, event: EventRecord) -> Optional[IncidentRecord]:
        if event.severity in ["HIGH", "CRITICAL"] or event.risk_score >= 50:
            is_new = self.repo.get_incident_by_id(f"INC-{datetime.utcnow().strftime('%Y%m%d')}-0001") is None # A bit hacky to check if new, actually get_or_create_active_incident handles it. Let's just track if severity changed or it's new.
            
            # Since get_or_create_active_incident creates it if it doesn't exist, we don't know if it was just created.
            # We can just dispatch if the event severity is CRITICAL or HIGH.
            # Wait, better to just dispatch if the incident's severity escalates or we add it.
            
            incident = self.repo.get_or_create_active_incident(severity=event.severity)
            old_severity = incident.severity
            
            self.repo.add_event_to_incident(incident, event)
            
            # Dispatch alert if it's a critical or high event and it's either new or escalated
            if event.severity in ["HIGH", "CRITICAL"]:
                # To prevent spam, only alert if the event itself is CRITICAL, or if it escalated the incident to CRITICAL
                if event.severity == "CRITICAL" or old_severity != "CRITICAL":
                    self.alert_dispatcher.dispatch_incident_alert(
                        incident.incident_number, 
                        incident.severity, 
                        incident.risk_score
                    )

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
