from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# 🔧 SDK y Exporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 🔧 Configurar TracerProvider con nombre de servicio
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "fastapi-app"})
    )
)

# 🔌 Exportador OTLP a OTEL Collector (por gRPC)
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)

# ⚙️ Procesador de spans
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 🚀 Aplicación FastAPI
app = FastAPI()
FastAPIInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)

@app.get("/")
def read_root():
    with tracer.start_as_current_span("root-handler"):
        return {"message": "Hola desde FastAPI + OTEL!"}


#from fastapi import FastAPI
#from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
#from opentelemetry import trace
#from opentelemetry.trace import get_tracer

#app = FastAPI()
#FastAPIInstrumentor().instrument_app(app)
#tracer = get_tracer(__name__)

#@app.get("/")
#def read_root():
#    with tracer.start_as_current_span("root-handler"):
#        return {"message": "Hola desde FastAPI + OTEL!"}