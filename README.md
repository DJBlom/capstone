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
| `src/templates/index.html` | Public page |
| `src/static/style.css` | Page styles |
| `requirements.txt` | Python dependencies |
| `Procfile` | Heroku web process |
| `.python-version` | Python 3.12 for Heroku |
| `documentation/` | Requirements, stories, architecture |
