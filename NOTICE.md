# NOTICE

This repository packages and redistributes upstream software published by the
[OpenTelemetry](https://github.com/open-telemetry/opentelemetry-collector-releases)
project. The Apache-2.0 license in [`LICENSE`](LICENSE) covers the OCX pipeline
files authored here. It does **not** cover any upstream-derived asset — each
package's redistributed bytes carry their own license, recorded below.

Each package's logo in this repository reproduces the **upstream project's own
mark** at 512 px, unmodified apart from scaling, solely to identify the
software being mirrored. No endorsement or affiliation is implied, and no
trademark right is claimed.

| Package | GHCR path | Upstream SPDX |
|---|---|---|
| `otelcol` | `ghcr.io/ocx-contrib/open-telemetry/otelcol` | `Apache-2.0` |

---

## `otelcol`

Upstream: <https://github.com/open-telemetry/opentelemetry-collector-releases>
Published to `ghcr.io/ocx-contrib/open-telemetry/otelcol`.

| Component | SPDX | Holder |
|---|---|---|
| OpenTelemetry Collector, core distribution (`otelcol`) | **Apache-2.0** | Copyright The OpenTelemetry Authors |

Verified at the license gate:
`gh api repos/open-telemetry/opentelemetry-collector-releases/license --jq '.license.spdx_id'`
→ `Apache-2.0`.

Apache-2.0 permits redistribution of the work in source and binary form. The
upstream license text is
<https://github.com/open-telemetry/opentelemetry-collector-releases/blob/main/LICENSE>
and the Apache License 2.0 is reproduced in full in [`LICENSE`](LICENSE) of this
repository; the same text governs the redistributed binary. The upstream
archive contains only the `otelcol` binary and a `README.md` — it carries no
`LICENSE` or `NOTICE` file of its own — so this notice is where the license
and holder are recorded for the mirrored bytes.

The published binary statically links third-party Go modules (the collector
core and a selection of contrib components, plus their dependencies), each
under its own permissive license, enumerated in the `go.mod`/`go.sum` of the
tagged upstream source for each mirrored version. Upstream also publishes an
SBOM per asset next to the release.

No modifications are made to any upstream artifact in this repository; they are
republished byte-for-byte inside an OCX bundle.
