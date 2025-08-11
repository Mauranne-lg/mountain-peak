# Mountain Peak

A simple web service for storing and retrieving mountain peaks.

## Description

Technical exercice using FastAPI framework and asynchronous programming.

## Quick start

```bash
pip install uv
uv init
uv pip install -r pyproject.toml
uv run fastapi dev app/main.py
```

## Load initial data

```bash
python initial_peaks.py
```

## Test main.py

```bash
pytest --cov=app app/tests/
```

## Linting

```bash
ruff format
ruff check
```

## Build the app

```bash
sudo docker-compose build
sudo docker-compose up
```
