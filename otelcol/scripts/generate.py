# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk~=0.6.0"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors
"""Generate url_index JSON for the OpenTelemetry Collector core distribution.

Why a generator and not the native `github_release` source: this upstream's
releases carry ~816 assets each, and the same repo tags three releases per
version (`vX`, `cmd/builder/vX`, `cmd/opampsupervisor/vX`). The native source
asks GitHub for `per_page=100`, which GitHub cannot serialise in time (504).
The SDK's REST backend falls back to a small page size on a 504 instead.

Only the core distribution tarballs are emitted; `otelcol-contrib_…`, the
other distributions, installers and sidecars never reach the index.
"""

from __future__ import annotations

import re
import sys

from ocx_mirror_sdk import IndexBuilder, github

REPO = "open-telemetry/opentelemetry-collector-releases"

# `v0.165.0` only — the leading `^v` rejects `cmd/builder/v…` and
# `cmd/opampsupervisor/v…`, the `$` rejects suffixed tags.
TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")

# `otelcol_<version>_<os>_<arch>.tar.gz`. The underscore straight after
# `otelcol` keeps `otelcol-contrib_…` & co. out; the trailing anchor keeps
# `.sha256` / `.sbom.json` / `.sigstore.json` sidecars out.
ASSET_RE = re.compile(r"^otelcol_[^_]+_[a-z0-9]+_[a-z0-9]+\.tar\.gz$")


def main() -> int:
    releases = github.list_releases(
        REPO,
        backend=github.Backend.REST,
        include_prereleases=False,
        include_drafts=False,
    )
    index = IndexBuilder()
    for rel in releases:
        match = TAG_RE.match(rel.tag_name)
        if match is None:
            continue
        assets = {a.name: a.browser_download_url for a in rel.assets if ASSET_RE.match(a.name)}
        index.add_version(match["version"], assets=assets, prerelease=False)
    sys.stderr.write(f"generate: {len(index)} versions\n")
    index.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
