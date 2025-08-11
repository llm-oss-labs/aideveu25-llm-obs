FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
 && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main --no-root --no-ansi

COPY apps/cli/main.py ./main.py

ENV API_BASE_URL="http://llm-workshop-api:8000/v1"

CMD ["python", "main.py"]
