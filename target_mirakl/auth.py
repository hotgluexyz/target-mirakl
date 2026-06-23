"""Authentication helpers for Mirakl."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import requests
from hotglue_singer_sdk.target_sdk.auth import OAuthAuthenticator


class MiraklAuthenticator(OAuthAuthenticator):
    """OAuth 2.0 client-credentials authenticator for Mirakl."""

    def __init__(
        self,
        target,
        state,
        auth_endpoint: Optional[str] = None,
    ) -> None:
        """Initialize the authenticator.

        Args:
            target: The Singer target instance.
            state: Authentication state.
            auth_endpoint: Token endpoint URL (from ``target.access_token_support``).
        """
        super().__init__(target, state, auth_endpoint=auth_endpoint)

    @property
    def oauth_request_body(self) -> dict:
        """OAuth request body for the client-credentials grant."""
        return {
            "grant_type": "client_credentials",
            "client_id": self._config["client_id"],
            "client_secret": self._config["client_secret"],
        }

    def _update_access_token_locally(self) -> None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.logger.info(
            "Oauth request - endpoint: %s, body: %s",
            self._auth_endpoint,
            self.oauth_request_body,
        )
        token_response = requests.post(
            self._auth_endpoint,
            data=self.oauth_request_body,
            headers=headers,
        )

        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            self.state.update({"auth_error_response": token_response.json()})
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            ) from ex

        token_json = token_response.json()
        self.access_token = token_json["access_token"]

        self._config["access_token"] = token_json["access_token"]
        now = round(datetime.utcnow().timestamp())
        self._config["expires_in"] = int(token_json["expires_in"]) + now

        with open(self._config_file_path, "w") as outfile:
            json.dump(self._config, outfile, indent=4)
