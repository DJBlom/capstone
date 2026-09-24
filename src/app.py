import os

from flask import Flask, jsonify, render_template, request

from src.analyzer import DateRangeError, catalog_summary, fireball_energy_analysis
from src.instrumentation import register_metrics
from src.models import FireballEvent, SentryObject, Users, db


def default_database_uri():
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return "sqlite:///" + os.path.join(root, "users.db")


def submitted_text_from_form(method, form):
    """Return the submitted name, or None if the user has not posted yet."""
    if method != "POST":
        return None
    return form.get("name", "")


def user_name_from_form(form):
    return (form.get("name") or "").strip()


def user_role_from_form(form):
    role = (form.get("role") or "").strip()
    return role or None


def create_app(config=None):
    application = Flask(__name__)
    application.config["SQLALCHEMY_DATABASE_URI"] = default_database_uri()
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if config:
        application.config.update(config)

    db.init_app(application)
    register_metrics(application)

    @application.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @application.route("/metrics")
    def metrics():
        snapshot = application.extensions["http_metrics"].snapshot()
        return jsonify(snapshot), 200

    @application.route("/", methods=["GET", "POST"])
    def index():
        submitted_text = submitted_text_from_form(request.method, request.form)
        name = user_name_from_form(request.form)
        if request.method == "POST" and name:
            db.session.add(Users(name=name, role=user_role_from_form(request.form)))
            db.session.commit()

        users = Users.query.order_by(Users.id.asc()).all()
        fireballs = (
            FireballEvent.query.order_by(FireballEvent.occurred_at.desc()).limit(10).all()
        )
        sentry_objects = (
            SentryObject.query.order_by(SentryObject.impact_probability.desc())
            .limit(10)
            .all()
        )
        return render_template(
            "index.html",
            submitted_text=submitted_text,
            users=users,
            fireballs=fireballs,
            sentry_objects=sentry_objects,
            analysis=catalog_summary(),
        )

    @application.route("/average/<start_date>/<end_date>")
    def average_impact_energy(start_date, end_date):
        """JSON analysis: mean fireball impact energy (kt) between two dates."""
        try:
            return jsonify(fireball_energy_analysis(start_date, end_date))
        except DateRangeError as exc:
            return jsonify({"error": str(exc)}), 400

    @application.route("/api/summary")
    def api_summary():
        return jsonify(catalog_summary())

    with application.app_context():
        db.create_all()

    return application


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    create_app().run(host="0.0.0.0", port=port)
