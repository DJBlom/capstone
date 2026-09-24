"""Analyze stored NEO records. NASA/JPL APIs do not return these aggregates."""

from datetime import datetime, timedelta

from sqlalchemy import func

from src.models import FireballEvent, SentryObject, db


class DateRangeError(ValueError):
    pass


def parse_iso_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise DateRangeError(f"dates must be YYYY-MM-DD, got {value!r}") from exc


def fireball_energy_analysis(start_date, end_date):
    """Average / max / total fireball impact energy (kt) in an inclusive date range."""
    start = parse_iso_date(start_date)
    end = parse_iso_date(end_date)
    if end < start:
        raise DateRangeError("end_date must be on or after start_date")

    start_bound = start
    end_bound = end + timedelta(days=1)
    filters = (
        FireballEvent.occurred_at >= start_bound,
        FireballEvent.occurred_at < end_bound,
    )
    count = FireballEvent.query.filter(*filters).count()
    if count == 0:
        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": 0,
            "average_impact_energy_kt": None,
            "max_impact_energy_kt": None,
            "total_impact_energy_kt": None,
        }

    average, maximum, total = (
        db.session.query(
            func.avg(FireballEvent.impact_energy_kt),
            func.max(FireballEvent.impact_energy_kt),
            func.sum(FireballEvent.impact_energy_kt),
        )
        .filter(*filters)
        .one()
    )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "count": count,
        "average_impact_energy_kt": float(average),
        "max_impact_energy_kt": float(maximum),
        "total_impact_energy_kt": float(total),
    }


def sentry_risk_analysis():
    """Summarize stored future-risk objects (Sentry has no single event date)."""
    count = SentryObject.query.count()
    if count == 0:
        return {
            "count": 0,
            "average_impact_probability": None,
            "max_impact_probability": None,
            "highest_risk_designation": None,
        }

    average, maximum = db.session.query(
        func.avg(SentryObject.impact_probability),
        func.max(SentryObject.impact_probability),
    ).one()
    highest = (
        SentryObject.query.order_by(SentryObject.impact_probability.desc()).first()
    )
    return {
        "count": count,
        "average_impact_probability": float(average) if average is not None else None,
        "max_impact_probability": float(maximum) if maximum is not None else None,
        "highest_risk_designation": highest.designation if highest else None,
    }


def catalog_summary():
    fireballs = fireball_energy_analysis("1900-01-01", "2100-12-31")
    fireballs.pop("start_date", None)
    fireballs.pop("end_date", None)
    return {
        "fireballs": fireballs,
        "sentry": sentry_risk_analysis(),
    }
