import logging
import sys

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def setup_logging(otlp_endpoint: str, resource: Resource):
    exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    set_logger_provider(provider)

    # Create console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))  # Just the message

    # Create OTLP handler
    otlp_handler = LoggingHandler(level=logging.INFO, logger_provider=provider)

    # Configure root logger with BOTH handlers
    logging.basicConfig(
        level=logging.INFO,
        handlers=[otlp_handler, console_handler],
        force=True,  # Override any existing config
    )

    return provider
