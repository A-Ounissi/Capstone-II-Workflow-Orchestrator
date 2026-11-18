
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    String,
    Integer,
    BigInteger,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    Enum,
    DECIMAL,
    Index,
    func,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# 1. JOBS
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index("idx_jobs_file_hash", "file_hash"),
    )

    job_id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)

    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", "review"),
        default="pending",
        server_default="pending",
        nullable=False
    )

    file_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    documents: Mapped[list["Document"]] = relationship(back_populates="job")
    ocr_results: Mapped[list["OcrResult"]] = relationship(back_populates="job")
    extractions: Mapped[list["Extraction"]
                        ] = relationship(back_populates="job")
    validation_results: Mapped[list["ValidationResult"]
                               ] = relationship(back_populates="job")
    events: Mapped[list["Event"]] = relationship(back_populates="job")
    workflow_runs: Mapped[list["WorkflowRun"]
                          ] = relationship(back_populates="job")


# ============================================================
# 2. DOCUMENTS
# ============================================================

class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    job: Mapped["Job"] = relationship(back_populates="documents")


# ============================================================
# 3. OCR RESULTS
# ============================================================

class OcrResult(Base):
    __tablename__ = "ocr_results"

    ocr_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    raw_text: Mapped[str | None] = mapped_column(LONGTEXT)
    confidence: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 2))

    processed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    job: Mapped["Job"] = relationship(back_populates="ocr_results")


# ============================================================
# 4. EXTRACTIONS
# ============================================================

class Extraction(Base):
    __tablename__ = "extractions"

    extraction_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    extracted_data: Mapped[dict | None] = mapped_column(JSON)
    model_used: Mapped[str | None] = mapped_column(String(100))

    extracted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    job: Mapped["Job"] = relationship(back_populates="extractions")


# ============================================================
# 5. VALIDATION RESULTS
# ============================================================

class ValidationResult(Base):
    __tablename__ = "validation_results"

    validation_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    errors: Mapped[list | None] = mapped_column(JSON)

    validated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    job: Mapped["Job"] = relationship(back_populates="validation_results")


# ============================================================
# 6. EVENTS
# ============================================================

class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    job: Mapped["Job"] = relationship(back_populates="events")


# ============================================================
# 7. WORKFLOWS
# ============================================================

class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    definition: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow")
    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="workflow")


# ============================================================
# 8. WORKFLOW STEPS
# ============================================================

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    step_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.workflow_id"),
        nullable=False
    )

    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_type: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    config: Mapped[dict | None] = mapped_column(JSON)
    depends_on: Mapped[list | None] = mapped_column(JSON)

    workflow: Mapped["Workflow"] = relationship(back_populates="steps")
    step_runs: Mapped[list["StepRun"]] = relationship(back_populates="step")


# ============================================================
# 9. WORKFLOW RUNS
# ============================================================

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    run_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False
    )

    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.workflow_id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "completed", "failed"),
        default="pending",
        server_default="pending",
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    job: Mapped["Job"] = relationship(back_populates="workflow_runs")
    workflow: Mapped["Workflow"] = relationship(back_populates="runs")
    step_runs: Mapped[list["StepRun"]] = relationship(
        back_populates="workflow_run")


# ============================================================
# 10. STEP RUNS
# ============================================================

class StepRun(Base):
    __tablename__ = "step_runs"

    step_run_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow_runs.run_id", ondelete="CASCADE"),
        nullable=False
    )

    step_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow_steps.step_id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "completed", "failed"),
        default="pending",
        server_default="pending",
        nullable=False
    )

    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False
    )

    workflow_run: Mapped["WorkflowRun"] = relationship(
        back_populates="step_runs")
    step: Mapped["WorkflowStep"] = relationship(back_populates="step_runs")
