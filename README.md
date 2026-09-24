# Impact Sentinel

A monitoring system for current and future asteroid impact zones. The public website is a **Flask** application. Product definition lives in [`documentation/`](documentation/).

This slice is a public Flask site plus a **separate data-collection process**. The form stores workstation users. The collector pulls current fireballs and future Sentry risk from NASA/JPL REST APIs into the same SQL database.

## Local setup (Flask)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=src.app:create_app
flask run
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

- Unit tests: form parsing (`tests/test_unit_form.py`), API payload parsing (`tests/test_unit_collector.py`), date parsing (`tests/test_unit_analyzer.py`)
- Integration tests: form POST, collector upsert with mocked HTTP, `/average/<start>/<end>` analysis, `/health`, `/metrics`, and messaging with a fake broker

## Data collection

The collector is a **separate process** from the web app (same pattern as the course weather example, pointed at NEO catalogs instead of WeatherDB).

```bash
python -m src.collector
```

It calls:

- `https://ssd-api.jpl.nasa.gov/fireball.api?limit=20` — current observed fireballs
- `https://ssd-api.jpl.nasa.gov/sentry.api` — future Sentry impact-risk summary

then upserts `FireballEvent` and `SentryObject` rows. Re-running updates existing designations/times instead of duplicating them. Refresh the website to see the latest stored rows.

### Schedule (cron)

Hourly on Linux:

```bash
crontab -e
```

```
0 * * * * cd /path/to/capstone && ./venv/bin/python -m src.collector >> collector.log 2>&1
```

Daily: `0 6 * * *`. Weekly: `0 6 * * 0`.

### Schedule (Heroku)

This data changes on the order of hours to days, so **hourly** is enough. One-off:

```bash
heroku run python -m src.collector
```

Or add [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler) and run `python -m src.collector` on an hourly job. That is a billed one-off dyno, not a always-on worker.

## Data analysis

NASA/JPL APIs do not return averages. `src/analyzer.py` computes them from stored rows.

JSON endpoint (same shape as the course temperature example, for fireball impact energy in kilotons):

```
GET /average/<start_date>/<end_date>
```

Example: [http://127.0.0.1:5000/average/2024-01-01/2026-12-31](http://127.0.0.1:5000/average/2024-01-01/2026-12-31)

```json
{
  "start_date": "2024-01-01",
  "end_date": "2026-12-31",
  "count": 20,
  "average_impact_energy_kt": 0.15,
  "max_impact_energy_kt": 1.2,
  "total_impact_energy_kt": 3.0
}
```

Invalid or inverted dates return HTTP 400. An empty range returns `count: 0` and `null` averages. Catalog-wide stats are also on the home page and at `GET /api/summary`.

## Event collaboration (RabbitMQ)

Collector and analyzer do not call each other over HTTP. After a successful scrape the collector **produces** a `collection.completed` message. A separate consumer **subscribes** through the RabbitMQ broker, analyzes stored rows, and produces `analysis.completed`. If the broker is down, collection still writes to SQLite.

```bash
# broker (management UI http://localhost:15672 guest/guest)
docker compose up -d rabbitmq

# terminal 1 — consumer
python -m src.consumer

# terminal 2 — producer
python -m src.collector
```

Override the host with `RABBITMQ_HOST` (default `localhost`). Queues: `collection.completed`, `analysis.completed`. Tests inject a fake channel so they do not need a live broker.

## Health and metrics

| Endpoint | Status | Body |
| --- | --- | --- |
| `GET /health` | 200 | `{"status": "ok"}` — liveness; does not call NASA |
| `GET /metrics` | 200 | JSON from `prometheus_client`: `requests_total`, `requests_per_second`, recent rate, status counts, uptime |

## Database

Impact Sentinel uses **SQL** (Flask-SQLAlchemy) rather than NoSQL.

| Factor | Choice |
| --- | --- |
| SQL vs NoSQL | User records (id, name, role) are table-shaped and relational, so a defined schema fits better than a document store. Unstructured scrape payloads can still be added later as another table or a separate store. |
| Ease | SQLite locally needs no server. The same SQLAlchemy models can point at Heroku Postgres via `DATABASE_URL`. |
| Security | Inserts go through the ORM (parameterized SQL), not string-built queries. Jinja auto-escapes names in HTML. |
| Scalability | SQLite is enough for this workstation slice. SQL scales vertically first; Heroku Postgres is the later step if the serving set grows. |
| Cost | SQLite is free on disk. Postgres on Heroku is optional and billed only if you add the add-on. |

Local file: `users.db` in the project root (gitignored). Tests use `sqlite:///:memory:` so they never touch that file.

`src/app.py` is the application file. Templates and CSS live next to it in `src/templates/` and `src/static/`.

## GitHub

This repository is [DJBlom/capstone](https://github.com/DJBlom/capstone).

```bash
git add .
git commit -m "Prepare Flask app for Heroku"
git push -u origin main
```

## Heroku (public URL)

Heroku is not free. The cheapest option is an [Eco dyno](https://devcenter.heroku.com/articles/eco-dyno-hours) at about $5/month (student credits: [Heroku for GitHub Students](https://blog.heroku.com/github-student-developer-program)). You must add a payment method and verify the account.

The app is already Heroku-ready: `Procfile` starts Gunicorn on `$PORT`, `requirements.txt` lists Flask and Gunicorn, `.python-version` pins Python 3.12.

### 1. Publish the code to GitHub

```bash
cd /home/odin/cu-boulder-ms-cs/architecture-of-big-data/project/capstone
git add .
git commit -m "Prepare Flask app for Heroku"
git push origin main
```

### 2. Install the Heroku CLI and log in

```bash
# Linux (see https://devcenter.heroku.com/articles/heroku-cli)
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

`heroku login` opens a browser. Finish the login there.

### 3. Create the app and deploy

```bash
heroku create
git push heroku main
heroku ps:scale web=1
heroku open
```

`heroku create` prints a public URL such as `https://something.herokuapp.com`. That is the live site.

To pick a name: `heroku create impact-sentinel-djblom` (the name must be unique on Heroku).

### 4. If the page is blank or you get H14

```bash
heroku logs --tail
heroku ps
```

Scale the web process if it is at 0: `heroku ps:scale web=1`.

Eco dynos sleep after about 30 minutes with no traffic. The first request after sleep can take several seconds.

### Dashboard alternative (no CLI)

1. Open [https://dashboard.heroku.com/new-app](https://dashboard.heroku.com/new-app) and create an app.
2. **Deploy** → **GitHub** → connect `DJBlom/capstone`.
3. Deploy the `main` branch.
4. **Resources** → make sure the `web` dyno is on.

## Layout

| Path | Role |
| --- | --- |
| `src/app.py` | Flask application and form routes |
| `src/models.py` | `Users`, `FireballEvent`, `SentryObject` |
| `src/collector.py` | Separate REST collection process |
| `src/analyzer.py` | Date-range averages and catalog summary |
| `src/instrumentation.py` | prometheus_client request counters for `/metrics` |
| `src/messaging.py` | Pika publish/subscribe helpers |
| `src/consumer.py` | RabbitMQ consumer (analysis on collection.completed) |
| `docker-compose.yaml` | Local RabbitMQ broker |
| `src/templates/index.html` | Public page |
| `src/static/style.css` | Page styles |
| `users.db` | Local SQLite file (created at runtime, not committed) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Heroku web process |
| `.python-version` | Python 3.12 for Heroku |
| `documentation/` | Requirements, stories, architecture |
