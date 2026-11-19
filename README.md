# mirror-open-telemetry

OCX mirror for the [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-releases)
**core** distribution. One repository, one spec directory per package.

| Package | Spec | Publishes to | Announced as | Upstream SPDX |
|---|---|---|---|---|
| [otelcol](https://github.com/open-telemetry/opentelemetry-collector-releases) | [`otelcol/mirror.yml`](otelcol/mirror.yml) | `ghcr.io/ocx-contrib/open-telemetry/otelcol` | [`ocx.sh/open-telemetry/otelcol`](https://index.ocx.sh/open-telemetry/otelcol) | `Apache-2.0` |

Each upstream release is discovered, re-bundled, smoke-tested per
`(version, platform)` and only then pushed with cascade tags, after which the
result is announced into the OCX index.

The GitHub org is the project's own brand, so the org names the namespace
(`open-telemetry`). Only the **core** distribution (`otelcol_<V>_<os>_<arch>.tar.gz`)
is mirrored; `otelcol-contrib`, `-k8s`, `-otlp`, `-prometheus`,
`-ebpf-profiler`, the `.deb`/`.rpm`/`.msi` installers and the sidecars in the
same release are not.

## Layout

```
mirror-base.yml         repo-wide policy every spec inherits via `extends:`
otelcol/
├── mirror.yml          the spec — never at the repo root
├── metadata.json       bundle interface
├── CATALOG.md          → ocx package describe
├── logo.svg / logo.png describe assets, 512px PNG
└── tests/smoke.star    Starlark smoke test
```

`LICENSE` and `NOTICE.md` are shared at the root. The logo lives inside the
package directory so that replacing it falls inside the package's workflow
`paths:` filter.

⚠️ `extends:` is a **shallow** merge of top-level keys. A spec that restates
`platforms:` to change one runner drops every `containers:` entry with it, and
nothing reds. `otelcol/mirror.yml` does not restate it at all.

## Platforms

Rollout is staged (linux first, then darwin, then windows). **Pass 1 — active:**
`linux/amd64` and `linux/arm64`. **Pre-written but commented**, in lockstep in
`otelcol/mirror.yml` `assets:` and `mirror-base.yml` `platforms:`:
`darwin/amd64`, `darwin/arm64`, `windows/amd64`, `windows/arm64`. A declared
platform with no asset boots a runner and tests nothing, so a pass is a pure
uncomment of both blocks, then `generate ci`.

Upstream's Linux binaries are Go builds with cgo disabled; both declared arches
were measured `statically linked` with zero `PT_INTERP` and zero `DT_NEEDED`, so
both Linux keys are **bare** and the `alpine:3.20` leg is the proof. The
measurement transcript sits above `assets:` in `otelcol/mirror.yml`, together
with the list of upstream platforms ocx cannot express (`linux_386`, `armv7`,
`ppc64le`, `riscv64`, `s390x`, `windows_386`, `aix_ppc64`).

⚠️ The upstream repo also tags `cmd/builder/v…` and `cmd/opampsupervisor/v…`;
the spec's anchored `tag_pattern` keeps those out.

## Editing

| File | Edit | Regenerate after |
|------|------|------------------|
| `mirror-base.yml`, `otelcol/mirror.yml` | hand | yes — see below |
| `otelcol/{metadata.json,CATALOG.md,logo.*}` | hand | — |
| `otelcol/tests/smoke.star` | hand | — |
| `.github/workflows/*.yml` | **generated — never hand-edit** | re-run when a spec changes |

```bash
ocx-mirror package pipeline generate ci --spec otelcol/mirror.yml
```

**Name every spec** — `--spec` appends rather than replaces. `verify-generated.yml`
exits 65 on drift. Run `direnv allow` once to put the pinned toolchain on
`PATH`, and invoke `ocx-mirror` directly — never `ocx run -- ocx-mirror`.

## The binaries claim

`otelcol/metadata.json` declares `binaries: ["otelcol"]` by hand and the spec sets
`bin_scan: "off"` — forced: the archives are flat (`otelcol(.exe)` and
`README.md` at the root), so the scan has no `${installPath}/<dir>` to inspect
and `auto`/`verify` fail spec load at exit 65.

## The smoke test

`otelcol/tests/smoke.star` asserts the version shape, then runs
`otelcol validate` on a minimal OTLP-receiver → debug-exporter config written to
scratch (must exit 0) and on the same config with the pipeline pointing at an
undeclared exporter (must exit non-zero). The collector is never started, so no
port is bound and no network is used.

## Required secrets

| Secret | Use |
|--------|-----|
| `OCX_ANNOUNCE_TOKEN` | opens the index pull request from the `ocx-contrib/index` fork |
| `OCX_MIRROR_DISCORD_HOOK` | notify-stage Discord webhook URL |

(Inherited from the `ocx-contrib` org. GHCR pushes use the run's own `GITHUB_TOKEN`.)

## License

Apache-2.0 — see [`LICENSE`](LICENSE). Upstream assets are out of scope; each
package's redistribution license is recorded in [`NOTICE.md`](NOTICE.md).
