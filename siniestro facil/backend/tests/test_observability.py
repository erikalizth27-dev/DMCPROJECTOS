import json
import logging

from siniestro_facil.observability import (
    JsonLineFormatter,
    build_http_log,
)


def test_http_log_contains_operational_fields() -> None:
    record = build_http_log(
        correlation_id="c7-observability",
        method="GET",
        path="/health/live",
        status_code=200,
        latency_seconds=0.125,
    )
    assert record["severity"] == "INFO"
    assert record["correlationId"] == "c7-observability"
    assert record["httpRequest"]["requestMethod"] == "GET"
    assert record["httpRequest"]["status"] == 200
    assert record["httpRequest"]["latency"] == "0.125000s"


def test_http_log_uses_path_without_query_or_headers() -> None:
    rendered = str(
        build_http_log(
            correlation_id="safe-id",
            method="POST",
            path="/api/v1/siniestros",
            status_code=422,
            latency_seconds=0,
        )
    )
    assert "token" not in rendered.lower()
    assert "authorization" not in rendered.lower()
    assert "password" not in rendered.lower()
    assert "query" not in rendered.lower()


def test_negative_latency_is_normalized() -> None:
    record = build_http_log(
        correlation_id="safe-id",
        method="GET",
        path="/health/live",
        status_code=200,
        latency_seconds=-1,
    )
    assert record["httpRequest"]["latency"] == "0.000000s"


def test_formatter_emits_single_line_json() -> None:
    payload = build_http_log(
        correlation_id="safe-id",
        method="GET",
        path="/health/live",
        status_code=200,
        latency_seconds=0.1,
    )
    log_record = logging.LogRecord(
        "test",
        logging.INFO,
        __file__,
        1,
        payload,
        (),
        None,
    )
    rendered = JsonLineFormatter().format(log_record)
    assert "\n" not in rendered
    assert json.loads(rendered) == payload


def test_valid_correlation_id_is_preserved() -> None:
    from siniestro_facil.api.middleware import normalized_correlation_id

    assert normalized_correlation_id("c7-valid_01:trace") == "c7-valid_01:trace"


def test_invalid_correlation_id_is_replaced() -> None:
    from siniestro_facil.api.middleware import normalized_correlation_id

    supplied = "invalid correlation\nforged-log"
    generated = normalized_correlation_id(supplied)
    assert generated != supplied
    assert "\n" not in generated


def test_oversized_correlation_id_is_replaced() -> None:
    from siniestro_facil.api.middleware import normalized_correlation_id

    supplied = "x" * 129
    assert normalized_correlation_id(supplied) != supplied
