# Impact Sentinel

A monitoring system for current and future asteroid impact zones. The public website is a **Flask** application. Product definition lives in [`documentation/`](documentation/).

This first slice is a public-facing page with a form: enter text, click **Submit!**, and the same text is shown on the page.

## Local setup (Flask)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=src/app.py
flask run
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

`src/app.py` is the application file. Templates and CSS live next to it in `src/templates/` and `src/static/`.

## GitHub

This repository is [DJBlom/capstone](https://github.com/DJBlom/capstone). After reviewing the files:

```bash
git add .
git commit -m "Add Flask public site, requirements, and architecture docs"
git push -u origin main
```

## Heroku

The `Procfile` and `requirements.txt` are set up so Heroku can run Gunicorn against `src.app:app`. After the app is on GitHub:

```bash
heroku create
git push heroku main
heroku open
```

Heroku sets `PORT`; Gunicorn binds to `0.0.0.0:$PORT`.

## Layout

| Path | Role |
| --- | --- |
| `src/app.py` | Flask application and form routes |
| `src/templates/index.html` | Public page |
| `src/static/style.css` | Page styles |
| `requirements.txt` | Python dependencies |
| `Procfile` | Heroku web process |
| `documentation/` | Requirements, stories, architecture |
