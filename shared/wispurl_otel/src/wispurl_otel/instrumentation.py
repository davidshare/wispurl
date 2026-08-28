import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_otel(service_name: str):
    """
    Initializes the OpenTelemetry TracerProvider and configures the OTLP exporter.
    It automatically reads OTEL_EXPORTER_OTLP_ENDPOINT from the environment.
    """
    # Build the resource with service metadata
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": os.getenv("DEPLOYMENT_ENV", "local"),
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
    })

    # Set the global tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure the exporter (reads OTEL_EXPORTER_OTLP_ENDPOINT automatically)
    # insecure=True is correct for local Docker network (http://alloy:4317)
    exporter = OTLPSpanExporter(insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))


def instrument_fastapi(app):
    """
    Instruments the FastAPI application. 
    Must be called AFTER `app = FastAPI()` is created.
    """
    FastAPIInstrumentor.instrument_app(app)
