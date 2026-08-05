# BANK

Bank management system with a FastAPI backend, a SQLite database, and a responsive frontend dashboard. The backend serves the frontend and API from the same origin.

## Run locally

```powershell
python -m pip install -r requirement.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. SQLite is used exclusively; by default, data is stored in `branch.db` at the project root. Set `DATABASE_PATH` to use another SQLite file.

## Run with Docker

```powershell
docker build -t bank-seva .
docker run --rm -p 8000:8000 -v bank-seva-data:/data bank-seva
```

The image uses `DATABASE_PATH=/data/branch.db`. Mounting `/data` preserves SQLite data across container replacements. `.env` files, local databases, tests, Git metadata, caches, and documentation are excluded from the image; pass any future environment variables at runtime with `--env-file` or `-e`, never by copying them into the image.

## CI

GitHub Actions installs dependencies from `requirement.txt`, runs the test suite, and builds the Docker image on pushes and pull requests to `main`.
