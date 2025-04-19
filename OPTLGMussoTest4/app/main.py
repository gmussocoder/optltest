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

# ¿Qué puedes hacer con el agente y el SDK?
#   Agente de OpenTelemetry:
#       Recolecta trazas: El agente captura las trazas generadas por tu aplicación, pero no métricas ni logs.
#       Exporta trazas: Envía las trazas a un backend de observabilidad, como un colector de OpenTelemetry, Grafana Tempo, o Jaeger, entre otros.
#   SDK de OpenTelemetry:
#       Recolecta métricas: El SDK de OpenTelemetry debe configurarse explícitamente para recolectar métricas de la aplicación (por ejemplo, contadores, histogramas, etc.).
#       Exporta métricas: Las métricas recolectadas por el SDK pueden ser enviadas a un backend como Prometheus o un colector de OpenTelemetry (a través de OTLP o cualquier otro método soportado).

from fastapi import FastAPI, Request
from opentelemetry import trace
# Las siguientes 4 líneas se agregan para poder exportar métricas
from opentelemetry import metrics

# from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter # si uso http es from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
# from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# La correlación entre logs, traces y métricas requiere más que solo el collector:
# El agente o SDK de OpenTelemetry (en la app) debe incluir contexto de traza en los logs.
# Luego, el OTel Collector puede agrupar trazas y logs que comparten el mismo trace_id.
# Las siguientes 8 líneas es para enviar logs a OPTL Colector:
import logging
#from opentelemetry.sdk._logs import LoggingHandler, LoggerProvider
#from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
#from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # para gRPC
import sys
#from opentelemetry._logs import set_logger_provider, get_logger
from opentelemetry._logs import get_logger
from opentelemetry.trace import get_current_span
from opentelemetry.trace.span import INVALID_SPAN_CONTEXT

from app.db import SessionLocal1, SessionLocal2
from sqlalchemy import text

# # Configuración del SDK de métricas con OTLP gRPC Exporter
# resource = Resource(attributes={
#     SERVICE_NAME: "fastapi-app"
# })

# otlp_metric_exporter = OTLPMetricExporter(
#     endpoint="otel-collector:4317",  # URL del OTLP Exporter para métricas si uso http debo poner http://
#     insecure=True  # Usar seguro si es necesario
# )

# reader = PeriodicExportingMetricReader(otlp_metric_exporter)
# provider = MeterProvider(resource=resource, metric_readers=[reader])
# metrics.set_meter_provider(provider)

meter = metrics.get_meter("fastapi-app")

# Ejemplo de una métrica de contador
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Conteo de solicitudes HTTP",
    unit="1"
)

# Configurar el provider de logs
# logger_provider = LoggerProvider(resource=resource)
# log_exporter = OTLPLogExporter(
#     endpoint="otel-collector:4317",
#     insecure=True
# )
# log_processor = BatchLogRecordProcessor(log_exporter)
# logger_provider.add_log_record_processor(log_processor)

# # Se establece el proveedor global de logs
# set_logger_provider(logger_provider)

# Agrego handler a la librería logging
#handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
#logging.getLogger().addHandler(handler)
#logging.getLogger().setLevel(logging.INFO)

# Formatter con trace_id y span_id
class TraceIdFormatter(logging.Formatter):
    def format(self, record):
        # Obtener el contexto actual
        span = get_current_span()
        ctx = span.get_span_context()

        if ctx is not None and not ctx == INVALID_SPAN_CONTEXT:
            record.trace_id = format(ctx.trace_id, '032x')
            record.span_id = format(ctx.span_id, '016x')
        else:
            record.trace_id = "N/A"
            record.span_id = "N/A"

        return super().format(record)


# Uso el formatter en el handler
formatter = TraceIdFormatter("[%(asctime)s] [%(levelname)s] trace_id=%(trace_id)s span_id=%(span_id)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# No necesito cliente de Prometheus dado que expongo métricas desde el OPTL collector y uso OPTL SDK.
#from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST 
#from starlette.responses import Response

app = FastAPI()
tracer = trace.get_tracer(__name__)

# Métricas básicas de Prometheus:
# El siguiente Counter es de prometheus_client, que no se requiere dado que lo comenté arriba:
# REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])

@app.get("/")
async def read_root(request: Request):
    request_counter.add(1, attributes={"method": request.method, "endpoint": "/"})
    # Agrego un log para verificar integración con loki:
#    logger = get_logger(__name__)
    logging.info("Inicio del handler /")

##############################################################
##  Criterios para agregar logging.info(...)                ##
##                                                          ##
##  Lo ideal es agregar logs estratégicamente, es decir:    ##
##                                                          ##
##                                                          ##
# Ubicación	                        ¿Qué loguear?                           ¿Para qué sirve?
# Justo al inicio de                "Inicio handler /items"	                Confirmar entrada de request, útil para debug en Loki
# cada handler o endpoint
# 	
# Antes o después de una            "Conectando con base de datos X"	    Identificar fallos o cuellos de botella
# operación importante
# 	
# En excepciones (con try/except)	"Error al procesar orden" + str(e)	    Diagnóstico más claro de fallos
#
# Al finalizar procesos exitosos	"Orden procesada correctamente"	        Seguimiento de flujo completo
#
# Así, cada log te da visibilidad de una parte importante del flujo, y con Loki podés buscar y seguir esos eventos.

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

#El siguiente endpoint (/metrics) y la función generate_latest() vienen del paquete prometheus_client, 
# y sirven solo cuando la app expone métricas directamente a Prometheus:
# @app.get("/metrics")
# def metrics():
#     return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)