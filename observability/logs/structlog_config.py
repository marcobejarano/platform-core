import logging

import structlog
from opentelemetry import trace


def add_otel_trace_context(_, __, event_dict):
    span = trace.get_current_span()
    ctx = span.get_span_context()

    attributes = {}

    if ctx.is_valid:
        attributes["trace_id"] = f"{ctx.trace_id:032x}"
        attributes["span_id"] = f"{ctx.span_id:016x}"

    # Extract structured fields (everything except internal structlog keys)
    structured = {
        k: v
        for k, v in event_dict.items()
        if k not in ("event", "level", "timestamp") and not k.startswith("_")
    }

    # The "body" is the log message itself
    event_dict["body"] = event_dict.get("event", "")

    # Attributes = structured fields + trace/span IDs
    event_dict["attributes"] = {**structured, **attributes}

    return event_dict


def setup_structlog():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_otel_trace_context,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
