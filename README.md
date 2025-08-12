# Mountain Peak

A simple web service for storing and retrieving mountain peaks.

## Description

Technical exercice using FastAPI framework and asynchronous programming.

## Quick start

1. Install uv\
   See more on [documentation](https://docs.astral.sh/uv/getting-started/installation/) or install with `pip install uv`

2. Create a virtual environment with\
   `uv venv`

3. Install dependencies with\
   `uv pip install -r pyproject.toml`

4. Create a `.env` file in mountain-peak file and add a `DATABASE_NAME` variable

5. Run app with\
   `uv run fastapi dev app/main.py`

6. Load initial datas with\
   `python initial_peaks.py`

## How to test the code

```bash
pytest --cov=app app/tests/
```

## How to build the app

```bash
sudo docker-compose build
sudo docker-compose up
```

## Linting commands

```bash
uv run ruff format
uv run ruff check
```
