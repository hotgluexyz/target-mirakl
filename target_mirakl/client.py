"""HTTP client and sink base classes for Mirakl."""


from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from hotglue_singer_sdk.target_sdk.client import HotglueBaseSink, HotglueBatchSink


class MiraklSink(HotglueBaseSink):
    """Mirakl Base target sink class for sinks."""

    base_url = "https://connectpartner-test.mirakl.net/api/channel-platform/v1"
    auth_state = {}

    @property
    def authenticator(self) -> Any:
        authenticator, auth_endpoint = self._target.access_token_support(self._target)
        return authenticator(self._target, self.auth_state, auth_endpoint)

    @property
    def origin(self) -> dict[str, str]:
        """Build the origin object for Mirakl Connect payloads."""
        return {
            "channel_id": self.config["channel_id"],
            "channel_store_id": self.config["channel_store_id"],
        }

    @property
    def unified_schema(self) -> type[BaseModel]:
        raise NotImplementedError


class MiraklBatchSink(MiraklSink, HotglueBatchSink):
    """Mirakl Batch target sink class for batch sinks."""

    name = "MiraklBatchSink"

    def process_batch_record(self, record: dict, _index: int) -> dict:
        return record

    @abstractmethod
    def make_batch_request(self, records: list[dict]) -> Any:
        raise NotImplementedError

    def handle_batch_response(self, _response: Any) -> dict:
        return {"state_updates": []}
