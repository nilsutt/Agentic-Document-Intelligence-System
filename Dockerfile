FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir build

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install -e .

CMD ["uvicorn", "src.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
