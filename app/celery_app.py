
import os

from celery import Celery


# Redis connection settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")


if not CELERY_BROKER_URL:
    raise RuntimeError("CELERY_BROKER_URL environment variable is not set")


if not CELERY_RESULT_BACKEND:
    raise RuntimeError("CELERY_RESULT_BACKEND environment variable is not set")


# Create the Celery application
celery_app = Celery(
    "workflow_orchestrator",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)


# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)
