# Como estoy usando instrumentación automática, no necesito inicializar ni el TracerProvider 
# ni el SpanProcessor en el código. Todo eso lo gestiona opentelemetry-instrument, siempre 
# que le pase los parámetros adecuados.

# Resumen de lo que estás logrando
# Instrumentación automática con opentelemetry-instrument
# Exportación vía OTLP al collector
# Visualización posterior en Grafana Tempo
# Este main.py se corre instrumentandolo de forma autompatica con agente OPTL:
# ver archivo Dockerfile
# CMD ["opentelemetry-instrument", \
#     "--traces_exporter=otlp", \
#     "--exporter_otlp_endpoint=otel-collector:4317", \
#     "--exporter_otlp_insecure=true", \
#     "--service_name=fastapi-app", \
#     "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#from fastapi import FastAPI
#from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI
from opentelemetry import trace
from app.db import SessionLocal1, SessionLocal2
from sqlalchemy import text

app = FastAPI()
tracer = trace.get_tracer(__name__)

@app.get("/")
async def read_root():
    with tracer.start_as_current_span("root-handler"):
        async with SessionLocal1() as session1:
            async with session1.begin():
                result1 = await session1.execute(text("SELECT * FROM items"))
                items = result1.fetchall()

        async with SessionLocal2() as session2:
            async with session2.begin():
                result2 = await session2.execute(text("SELECT * FROM ordenes"))
                ordenes = result2.fetchall()

        return {
            "items": [dict(row._mapping) for row in items],
            "ordenes": [dict(row._mapping) for row in ordenes]
        }