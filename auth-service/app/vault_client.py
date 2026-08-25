from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import hvac
from hvac.exceptions import VaultError


def _read_approle(path: str) -> tuple[str, str]:
    credentials = json.loads(Path(path).read_text())

    role_id = credentials.get("role_id")
    secret_id = credentials.get("secret_id")

    if not role_id or not secret_id:
        raise RuntimeError(f"Invalid AppRole credentials in {path}")

    return role_id, secret_id


def load_vault_secrets() -> dict[str, Any]:
    vault_addr = os.environ["VAULT_ADDR"]
    credentials_file = os.environ["VAULT_ROLE_ID_FILE"]
    secret_path = os.environ["VAULT_SECRET_PATH"]
    ca_cert = os.environ.get("VAULT_CACERT")

    role_id, secret_id = _read_approle(credentials_file)

    client = hvac.Client(
        url=vault_addr,
        verify=ca_cert if ca_cert else True,
    )

    client.auth.approle.login(
        role_id=role_id,
        secret_id=secret_id,
        mount_point="approle",
    )

    if not client.is_authenticated():
        raise RuntimeError("Vault AppRole authentication failed")

    response = client.secrets.kv.v2.read_secret_version(
        path=secret_path,
        mount_point="secret",
        raise_on_deleted_version=True,
    )

    return response["data"]["data"]