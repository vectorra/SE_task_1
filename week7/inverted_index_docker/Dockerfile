# Lightweight Python base
FROM python:3.11-slim

# System deps for NLTK (if needed later) and pip hygiene
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Workdir and app copy
WORKDIR /opt/app
COPY inverted_index_app /opt/app/inverted_index_app

# Install runtime deps
RUN pip install --no-cache-dir nltk redis

# Download NLTK data at build time (punkt tokenizer)
ENV NLTK_DATA=/usr/local/nltk_data
RUN python - <<'PY'
import nltk; nltk.download('punkt')
PY

# Make package importable
ENV PYTHONPATH=/opt/app

# Default entrypoint to the CLI
ENTRYPOINT ["python", "-m", "inverted_index_app.cli"]
