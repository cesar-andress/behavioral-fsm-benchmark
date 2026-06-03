#!/usr/bin/env python3
"""Patch Zenodo deposition creator metadata to canonical author identity.

Requires a personal access token with deposit:write scope:
  export ZENODO_TOKEN='...'   # from https://zenodo.org/account/settings/applications/

Usage:
  python scripts/update_zenodo_creators.py --dry-run
  python scripts/update_zenodo_creators.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

CANONICAL_CREATOR = {
    "name": "Andrés, César",
    "orcid": "0009-0001-8968-3404",
}

# Published record IDs (latest versions as of 2026-06-03).
RECORDS = {
    "behavioral-fsm-benchmark": "20522834",
    "fsm-bench-20": "20516296",
}

ZENODO_API = "https://zenodo.org/api"


def _request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_record(record_id: str) -> dict:
    with urllib.request.urlopen(f"{ZENODO_API}/records/{record_id}") as resp:
        return json.load(resp)


def find_deposition_id(token: str, record_id: str) -> int | None:
    """Resolve deposition ID by scanning the authenticated user's depositions."""
    url = f"{ZENODO_API}/deposit/depositions?size=100"
    while url:
        depositions = _request("GET", url, token)
        for dep in depositions:
            metadata = dep.get("metadata", {})
            doi = metadata.get("doi", "")
            if doi.endswith(record_id):
                return dep["id"]
            for rel in metadata.get("related_identifiers", []) or []:
                identifier = rel.get("identifier", "")
                if record_id in identifier:
                    return dep["id"]
        url = None
    return None


def patch_creators(metadata: dict) -> tuple[dict, list[str]]:
    changes: list[str] = []
    old_creators = metadata.get("creators", [])
    new_creators = [{**CANONICAL_CREATOR}]
    if old_creators != new_creators:
        changes.append(
            f"creators: {old_creators!r} -> {new_creators!r}"
        )
    metadata["creators"] = new_creators

    # Strip DOI-related related_identifiers that break PUT validation on edit.
    related = metadata.get("related_identifiers") or []
    filtered = [
        rel
        for rel in related
        if rel.get("relation") != "isVersionOf"
        and not (
            rel.get("identifier", "").startswith("10.5281/zenodo.")
            and rel.get("relation") in {"isVersionOf", "isIdenticalTo"}
        )
    ]
    if len(filtered) != len(related):
        changes.append(
            f"related_identifiers: removed {len(related) - len(filtered)} DOI/version entries"
        )
        metadata["related_identifiers"] = filtered

    return metadata, changes


def apply_patch(token: str, deposition_id: int, metadata: dict) -> None:
    base = f"{ZENODO_API}/deposit/depositions/{deposition_id}"
    _request("POST", f"{base}/actions/edit", token)
    _request("PUT", base, token, {"metadata": metadata})
    _request("POST", f"{base}/actions/publish", token)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply metadata patch via Zenodo deposit API (default: dry-run only)",
    )
    args = parser.parse_args()

    print("Canonical creator:", CANONICAL_CREATOR)
    print()

    for label, record_id in RECORDS.items():
        print(f"=== {label} (record {record_id}) ===")
        record = fetch_record(record_id)
        live_creators = record.get("metadata", {}).get("creators", [])
        print("Live Zenodo creators:", live_creators)

        metadata, changes = patch_creators(dict(record["metadata"]))
        if not changes:
            print("Already aligned.\n")
            continue

        for change in changes:
            print("  -", change)

        if not args.apply:
            print("Dry-run only (pass --apply to push).\n")
            continue

        token = os.environ.get("ZENODO_TOKEN")
        if not token:
            print("ERROR: set ZENODO_TOKEN to apply changes.", file=sys.stderr)
            return 1

        deposition_id = find_deposition_id(token, record_id)
        if deposition_id is None:
            print(
                f"ERROR: could not resolve deposition ID for record {record_id}.",
                file=sys.stderr,
            )
            return 1

        try:
            apply_patch(token, deposition_id, metadata)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"ERROR: Zenodo API {exc.code}: {body}", file=sys.stderr)
            return 1

        updated = fetch_record(record_id)
        print("Updated creators:", updated["metadata"]["creators"])
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
