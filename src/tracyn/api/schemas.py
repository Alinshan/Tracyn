from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class EventOut(BaseModel):
    event_id: str
    timestamp: Optional[str]
    event_type: str
    path: str
    old_hash: Optional[str]
    new_hash: Optional[str]
    user: Optional[str]
    process: Optional[str]
    risk_score: int
    severity: str
    reason: Optional[str]
    status: str

    class Config:
        from_attributes = True


class FileOut(BaseModel):
    id: int
    path: str
    filename: str
    extension: Optional[str]
    size: int
    sha256: Optional[str]
    criticality: str
    first_seen: Optional[str]
    last_seen: Optional[str]

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    id: int
    incident_number: str
    title: str
    severity: str
    status: str
    risk_score: int
    created_at: Optional[str]
    updated_at: Optional[str]
    resolved_at: Optional[str]
    analyst_notes: Optional[str]

    class Config:
        from_attributes = True


class BaselineOut(BaseModel):
    id: int
    version: str
    created_at: Optional[str]
    created_by: str
    description: Optional[str]
    status: str

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str
    analyst_notes: Optional[str] = None


class DashboardSummary(BaseModel):
    total_files: int
    modified_files: int
    new_files: int
    deleted_files: int
    total_events: int
    open_incidents: int
    critical_alerts: int
    high_alerts: int
    current_risk_score: int
    current_risk_level: str
    monitor_status: str
