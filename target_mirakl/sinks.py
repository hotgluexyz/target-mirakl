"""Mirakl target sink class, which handles writing streams."""

from __future__ import annotations

import requests

from target_mirakl.client import MiraklBatchSink


class OrdersSink(MiraklBatchSink):
    """Orders sink implementation."""

    name = "Orders"
    endpoint = "/orders"
    MAX_SIZE_DEFAULT = 100
    SUCCESS_STATUS_CODE = 204

    def process_batch_record(self, record: dict, _index: int) -> dict:
        return record

    def make_batch_request(self, records: list[dict]) -> requests.Response:
        self._current_batch_external_ids = [
            record.get("channel_order_id", "") for record in records
        ]
        payload = {
            "origin": self.origin,
            "orders": records,
        }
        return self.request_api("POST", self.endpoint, request_data=payload)

    def handle_batch_response(self, response: requests.Response) -> dict:
        if response.status_code != self.SUCCESS_STATUS_CODE:
            return {
                "state_updates": [
                    {
                        "externalId": external_id,
                        "success": False,
                        "error": f"Unexpected response status: {response.status_code}",
                    }
                    for external_id in self._current_batch_external_ids
                ]
            }

        return {
            "state_updates": [
                {
                    "externalId": external_id,
                    "success": True,
                    "id": external_id,
                }
                for external_id in self._current_batch_external_ids
            ]
        }
