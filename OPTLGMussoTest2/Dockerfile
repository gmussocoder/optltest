FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT con instrumentación automática
CMD ["opentelemetry-instrument", \
     "--traces_exporter=otlp", \
     "--exporter_otlp_endpoint=http://otel-collector:4317", \
     "--service_name=fastapi-app", \
     "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
