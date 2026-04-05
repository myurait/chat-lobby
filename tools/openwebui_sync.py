#!/usr/bin/env python3
"""Shared helpers for syncing Open WebUI functions."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


NOT_FOUND_DETAIL = "We could not find what you're looking for :/"


def request_json(url: str, method: str, payload: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        return error.code, data


def sign_in(base_url: str, email: str, password: str) -> str:
    status, data = request_json(
        f"{base_url}/api/v1/auths/signin",
        "POST",
        {"email": email, "password": password},
    )
    if status != 200 or "token" not in data:
        raise RuntimeError(f"Failed to sign in to Open WebUI: {data}")
    return data["token"]


def ensure_function(
    base_url: str,
    token: str,
    function_id: str,
    name: str,
    description: str,
    content: str,
) -> dict:
    form = {
        "id": function_id,
        "name": name,
        "meta": {"description": description},
        "content": content,
    }

    status, data = request_json(f"{base_url}/api/v1/functions/id/{function_id}", "GET", token=token)
    if status == 200:
        status, data = request_json(
            f"{base_url}/api/v1/functions/id/{function_id}/update",
            "POST",
            form,
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Failed to update function: {data}")
        return data

    not_found = isinstance(data, dict) and data.get("detail") == NOT_FOUND_DETAIL
    if status not in {401, 404} or not not_found:
        raise RuntimeError(f"Failed to inspect existing function: {data}")

    status, data = request_json(f"{base_url}/api/v1/functions/create", "POST", form, token=token)
    if status != 200:
        raise RuntimeError(f"Failed to create function: {data}")
    return data


def ensure_active(base_url: str, token: str, function_id: str) -> None:
    status, data = request_json(f"{base_url}/api/v1/functions/id/{function_id}", "GET", token=token)
    if status != 200:
        raise RuntimeError(f"Failed to read function after sync: {data}")

    if not data.get("is_active", False):
        status, data = request_json(
            f"{base_url}/api/v1/functions/id/{function_id}/toggle",
            "POST",
            {},
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Failed to activate function: {data}")
