"""Mirakl target class."""


from __future__ import annotations

from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.target_sdk.target import TargetHotglue
from target_mirakl.auth import MiraklAuthenticator
from target_mirakl.sinks import OrdersSink


class TargetMirakl(TargetHotglue):
    """Target for Mirakl."""

    name = "target-mirakl"
    SINK_TYPES = [OrdersSink]

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType(),
            required=True,
            description="Client identifier for the Mirakl OAuth token endpoint",
        ),
        th.Property(
            "client_secret",
            th.StringType(),
            required=True,
            description="Client secret for the Mirakl OAuth token endpoint",
        ),
        th.Property(
            "channel_id",
            th.StringType(),
            required=True,
            description="Sales channel identifier used in order payload origin",
        ),
        th.Property(
            "channel_store_id",
            th.StringType(),
            required=True,
            description="Store identifier on the sales channel, used in order payload origin",
        ),
        th.Property(
            "access_token",
            th.StringType(),
            required=False,
            description="Current access token (usually populated after token refresh)",
        ),
        th.Property(
            "expires_in",
            th.IntegerType(),
            required=False,
            description="Epoch seconds when the access token expires (updated on refresh)",
        ),
    ).to_dict()

    @classmethod
    def access_token_support(cls, connector=None):
        return (
            MiraklAuthenticator,
            "https://auth-test.mirakl.net/oauth/token",
        )


if __name__ == "__main__":
    TargetMirakl.cli()
