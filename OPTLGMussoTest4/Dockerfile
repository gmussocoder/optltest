FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT con instrumentación automática
CMD ["opentelemetry-instrument", \
     "--traces_exporter=otlp", \
     "--metrics_exporter=otlp", \
     "--logs_exporter=otlp", \
     "--exporter_otlp_endpoint=otel-collector:4317", \
     "--exporter_otlp_insecure=true", \
     "--service_name=fastapi-app", \
     "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#
#    "--metrics_exporter=otlp" activa la exportación de métricas.
#    "--logs_exporter=otlp" activa los logs vía OTLP.