# otelcol/tests/smoke.star — stable across upstream otelcol releases.
# Asserts the contract (version shape, a config that validates, a config that
# does not), never help/version prose. See ocx.mirror testing-practices.md.
#
# otelcol is a telemetry pipeline, so its offline contract is its config
# validator: `otelcol validate` resolves a config, instantiates the component
# factories it names and checks the pipeline wiring — without starting the
# collector, so no ports are bound and nothing touches the network. Both
# directions are asserted: a valid config exits 0, and a pipeline that
# references an exporter nobody declared exits non-zero, so a build that
# validated everything (or nothing) cannot pass.
#
# Component names (`otlp` receiver, `debug` exporter) were confirmed against
# `otelcol components` on 0.165.0. The config is passed as a RELATIVE path:
# the test cwd is the scratch root, and a relative name sidesteps the Windows
# `C:\…` drive-letter being read as a config-provider scheme.

OTELCOL = "otelcol.exe" if ocx.target_platform.os == ocx.os.Windows else "otelcol"

# ── Tier 1 + 2: liveness on the composed PATH + version SHAPE ───────────────
# The digits are the contract; the banner around them is not.
r_version = ocx.run(OTELCOL, "--version")
expect.ok(r_version)
expect.matches(r_version.stdout, r"\d+\.\d+\.\d+")

# ── Tier 3: a valid config validates ────────────────────────────────────────
ocx.write_file("good.yaml", """receivers:
  otlp:
    protocols:
      grpc:
exporters:
  debug:
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [debug]
""")
r_good = ocx.run(OTELCOL, "validate", "--config=good.yaml")
expect.eq(r_good.exit_code, 0)

# ── Negative control — states what would go red ─────────────────────────────
# Same config, but the pipeline names an exporter that is not declared.
# Validation must fail (measured exit 1, `references exporter "nosuch" which
# is not configured`); without this, a validator that accepted everything
# would pass the assertion above.
ocx.write_file("bad.yaml", """receivers:
  otlp:
    protocols:
      grpc:
exporters:
  debug:
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [nosuch]
""")
r_bad = ocx.run(OTELCOL, "validate", "--config=bad.yaml")
expect.ne(r_bad.exit_code, 0)
