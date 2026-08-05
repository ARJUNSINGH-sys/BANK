FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/branch.db

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt \
    && mkdir -p /data

COPY app ./app
COPY auth ./auth
COPY customerservice ./customerservice
COPY database ./database
COPY MAIN ./MAIN
COPY Transcation ./Transcation
COPY frontend ./frontend

VOLUME ["/data"]
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
