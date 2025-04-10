# Como estoy usando instrumentación automática, no necesito inicializar ni el TracerProvider 
# ni el SpanProcessor en el código. Todo eso lo gestiona opentelemetry-instrument, siempre 
# que le pase los parámetros adecuados.

# Resumen de lo que estás logrando
# Instrumentación automática con opentelemetry-instrument
# Exportación vía OTLP al collector
# Visualización posterior en Grafana Tempo


from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace

app = FastAPI()
#FastAPIInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)

@app.get("/")
def read_root():
    with tracer.start_as_current_span("root-handler"):
        return {"message": "Hola desde FastAPI + OTEL!"}
