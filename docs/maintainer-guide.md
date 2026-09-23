# Maintainer guide

## Chart registry regression tests

Run `python3 -m unittest discover -s tests -v` from the repository root with Python, PyYAML,
Bash, `jq` and `yq` available. The suite executes the actual YAML script blocks against
isolated Helm/curl doubles; it never publishes to a real registry. It covers empty-registry
package fallback, OCI, credentials, checks, remote scans, promotion and initialization.

## Migration Guide & Standard

The initial public release is `1.0.0`. No migration is required. Future breaking releases will document consumer actions in [`MIGRATION.md`](../MIGRATION.md).

[Documentation index](../README.md)
