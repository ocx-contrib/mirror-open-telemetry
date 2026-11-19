# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk~=0.6.0"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors
"""Generate url_index JSON for the OpenTelemetry Collector core distribution.

Why a generator and not the native `github_release` source: this upstream's
releases carry ~816 assets each, three releases per version (`vX`,
`cmd/builder/vX`, `cmd/opampsupervisor/vX`). The native source lists at
`per_page=100`, which GitHub 504s on every time; the SDK's `list_releases`
survives that but drops the per-asset `digest` GitHub declares. So this pages
the REST endpoint directly at `per_page=10` (measured OK; 30 also OK, 100 not)
and emits `{url, sha256}` when GitHub declares a digest, checked by
`verify.url_index_digest: require` in mirror-base.yml.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time

from ocx_mirror_sdk.errors import HttpStatusError
from ocx_mirror_sdk.http import fetch_json

API = "https://api.github.com/repos/open-telemetry/opentelemetry-collector-releases/releases"
PER_PAGE = 10

# `v0.165.0` only — the leading `^v` rejects `cmd/builder/v…` and
# `cmd/opampsupervisor/v…`, the `$` rejects suffixed tags.
TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
# The underscore straight after `otelcol` keeps `otelcol-contrib_…` & co. out;
# the trailing anchor keeps `.sha256` / `.sbom.json` / `.sigstore.json` out.
ASSET_RE = re.compile(r"^otelcol_[^_]+_[a-z0-9]+_[a-z0-9]+\.tar\.gz$")


def page(n: int) -> list[dict]:
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(4):  # the SDK client retries connections, not 5xx
        try:
            return fetch_json(API, headers=headers, params={"per_page": PER_PAGE, "page": n})
        except HttpStatusError as e:
            if e.status_code < 500 or attempt == 3:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def main() -> int:
    versions: dict[str, dict] = {}
    n = 1
    while batch := page(n):  # until an EMPTY page, never "short page"
        sys.stderr.write(f"generate: page {n}: {len(batch)} releases\n")
        for rel in batch:
            m = TAG_RE.match(rel["tag_name"])
            if m is None or rel.get("draft") or rel.get("prerelease"):
                continue
            assets = {}
            for a in rel["assets"]:
                if ASSET_RE.match(a["name"]):
                    digest = a.get("digest")
                    url = a["browser_download_url"]
                    assets[a["name"]] = {"url": url, "sha256": digest} if digest else url
            if assets:
                versions[m["version"]] = {"prerelease": False, "assets": assets}
        n += 1
    sys.stderr.write(f"generate: {n - 1} non-empty pages, {len(versions)} versions\n")
    json.dump({"versions": versions}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
