"""Database Models
"""

from .alembic_version import AlembicVersion  # noqa F401
from .config import Config  # noqa F401
from .job import Job, JobState  # noqa F401
from .notifications import Notifications  # noqa F401
from .system_drives import SystemDrives  # noqa F401
from .system_info import SystemInfo  # noqa F401
from .track import Track  # noqa F401
from .ui_settings import UISettings  # noqa F401
from .user import User  # noqa F401
from arm.ui import db


class JobImage(db.Model):
    """Per-job uploaded images and OCR/AI metadata."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), nullable=False)
    side = db.Column(db.String(16), nullable=False)  # front|back|disk
    path = db.Column(db.String(512), nullable=False)
    ocr_text = db.Column(db.Text)
    ocr_lang = db.Column(db.String(16))
    ocr_conf = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<JobImage job_id={self.job_id} side={self.side}>'
