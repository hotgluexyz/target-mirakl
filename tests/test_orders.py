"""Unit tests for Mirakl auth and Orders sink."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from target_mirakl.auth import MiraklAuthenticator
from target_mirakl.sinks import OrdersSink
from target_mirakl.target import TargetMirakl


@pytest.fixture
def target() -> TargetMirakl:
    return TargetMirakl(
        config={
            "client_id": "test-id",
            "client_secret": "test-secret",
            "channel_id": "channel-123",
            "channel_store_id": "sandbox",
        },
        validate_config=True,
    )


def test_client_credentials_request_body() -> None:
    target = TargetMirakl(
        config={
            "client_id": "test-id",
            "client_secret": "test-secret",
            "channel_id": "channel-123",
            "channel_store_id": "sandbox",
        },
        validate_config=False,
    )
    auth = MiraklAuthenticator(target, {}, "https://auth-test.mirakl.net/oauth/token")

    assert auth.oauth_request_body == {
        "grant_type": "client_credentials",
        "client_id": "test-id",
        "client_secret": "test-secret",
    }


def test_orders_sink_batch_payload(target: TargetMirakl) -> None:
    sink = OrdersSink(
        target,
        "Orders",
        {"type": "object", "properties": {}},
        ["channel_order_id"],
    )
    assert sink.max_size == OrdersSink.MAX_SIZE_DEFAULT

    order = {"channel_order_id": "WF-PO-1", "status": "AWAITING_ACCEPTANCE"}
    with patch.object(sink, "request_api") as mock_request:
        mock_request.return_value = MagicMock(status_code=204)
        response = sink.make_batch_request([order])

    mock_request.assert_called_once_with(
        "POST",
        "/orders",
        request_data={
            "origin": {
                "channel_id": "channel-123",
                "channel_store_id": "sandbox",
            },
            "orders": [order],
        },
    )
    assert response.status_code == 204


def test_orders_sink_success_response(target: TargetMirakl) -> None:
    sink = OrdersSink(
        target,
        "Orders",
        {"type": "object", "properties": {}},
        ["channel_order_id"],
    )
    order = {"channel_order_id": "WF-PO-1", "status": "AWAITING_ACCEPTANCE"}

    with patch.object(sink, "request_api") as mock_request:
        mock_request.return_value = MagicMock(status_code=204)
        sink.make_batch_request([order])

    response = requests.Response()
    response.status_code = OrdersSink.SUCCESS_STATUS_CODE
    result = sink.handle_batch_response(response)

    assert result == {
        "state_updates": [
            {
                "externalId": "WF-PO-1",
                "success": True,
                "id": "WF-PO-1",
            }
        ]
    }
