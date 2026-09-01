FROM python:3.11-slim

WORKDIR /app

# System deps needed by some Python packages (pypdf, python-docx parsing,
# sentence-transformers' tokenizer backends).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render (and most free-tier hosts) inject the port to bind via $PORT.
# Default to 8000 for local `docker run` without that variable set.
ENV PORT=8000
EXPOSE 8000

# Run migrations, then start the server. Using sh -c so $PORT expands.
CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"