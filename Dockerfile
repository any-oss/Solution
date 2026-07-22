FROM python:3.11-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY ui/ ./ui/
COPY cli/ ./cli/
COPY sdk/ ./sdk/
COPY tests/ ./tests/

# Create data directory for database
RUN mkdir -p /app/data && chown -R appuser:appuser /app

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 8000 8001 8002

CMD ["python", "-m", "core.proxy"]
