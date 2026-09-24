from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    """Relational record for a workstation user (name plus optional role)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class FireballEvent(db.Model):
    """Observed fireball / bolide — current impact events from CNEOS."""

    __tablename__ = "fireball_events"

    id = db.Column(db.Integer, primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude_km = db.Column(db.Float, nullable=True)
    radiated_energy = db.Column(db.Float, nullable=True)
    impact_energy_kt = db.Column(db.Float, nullable=False)
    collected_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class SentryObject(db.Model):
    """Published future impact risk — Sentry summary rows from CNEOS."""

    __tablename__ = "sentry_objects"

    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(64), nullable=False, unique=True)
    fullname = db.Column(db.String(128), nullable=True)
    impact_probability = db.Column(db.Float, nullable=True)
    palermo_scale = db.Column(db.Float, nullable=True)
    torino_scale = db.Column(db.Integer, nullable=True)
    year_range = db.Column(db.String(32), nullable=True)
    diameter_km = db.Column(db.Float, nullable=True)
    collected_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
