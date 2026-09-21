from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

incident_events_table = Table(
    "incident_events",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
)


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(512), unique=True, nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    extension = Column(String(64), nullable=True)
    size = Column(Integer, default=0)
    sha256 = Column(String(64), nullable=True)
    criticality = Column(String(32), default="NORMAL")  # NORMAL, IMPORTANT, SENSITIVE, CRITICAL
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    baseline_files = relationship("BaselineFileRecord", back_populates="file")
    events = relationship("EventRecord", back_populates="file_record")


class BaselineRecord(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(128), default="system")
    description = Column(Text, nullable=True)
    status = Column(String(32), default="ACTIVE")  # ACTIVE, ARCHIVED, VERIFIED
    sha256 = Column(String(64), nullable=True)  # Tamper protection hash of baseline JSON

    baseline_files = relationship("BaselineFileRecord", back_populates="baseline", cascade="all, delete-orphan")


class BaselineFileRecord(Base):
    __tablename__ = "baseline_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    baseline_id = Column(Integer, ForeignKey("baselines.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    sha256 = Column(String(64), nullable=False)
    size = Column(Integer, default=0)

    baseline = relationship("BaselineRecord", back_populates="baseline_files")
    file = relationship("FileRecord", back_populates="baseline_files")


class EventRecord(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(32), nullable=False)  # MODIFIED, NEW_FILE, DELETED_FILE, RENAMED, HASH_MISMATCH
    file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    path = Column(String(512), nullable=False, index=True)
    old_hash = Column(String(64), nullable=True)
    new_hash = Column(String(64), nullable=True)
    user = Column(String(128), default="UNKNOWN")
    process = Column(String(128), default="UNKNOWN")
    risk_score = Column(Integer, default=0)
    severity = Column(String(32), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    reason = Column(Text, nullable=True)
    status = Column(String(32), default="NEW")  # NEW, REVIEWED, DISMISSED

    file_record = relationship("FileRecord", back_populates="events")
    incidents = relationship("IncidentRecord", secondary=incident_events_table, back_populates="events")


class IncidentRecord(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_number = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(32), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(32), default="NEW")  # NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    analyst_notes = Column(Text, nullable=True)

    events = relationship("EventRecord", secondary=incident_events_table, back_populates="incidents")


class ConfigurationRecord(Base):
    __tablename__ = "configuration"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
