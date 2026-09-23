# Migration Guide

This document records required consumer actions when upgrading between releases.
Breaking changes must include an entry before release.

## 1.2.0

The documentation restructuring requires no consumer configuration changes; update bookmarks
to moved sections and start from the README index.

The Python runtime now clears the image entrypoint for GitLab Runner. If a consumer
overrides it with `["/bin/bash"]`, remove that override to inherit `.Python:12`'s
`entrypoint: [""]`. No micro-image rebuild is required for this template fix.

Chart publishing now selects OCI when `CHART_REGISTRY` is nonempty. To keep publishing to the
current project's GitLab Helm Package Registry, leave it unset or empty, including inherited
group settings. Initialization no longer substitutes `CI_REGISTRY`.

For OCI, set `CHART_REPOSITORY` to the namespace/path without the chart name, and supply
`CHART_REGISTRY_USERNAME` / `CHART_REGISTRY_PASSWORD`. Docker Hub uses the namespace root
for both candidate and release charts. Image settings are independent.

If `CHART_REGISTRY` previously authenticated only private dependencies, move that host and
credential pair to `CHART_DEPENDENCY_REGISTRY`, `CHART_DEPENDENCY_REGISTRY_USERNAME` and
`CHART_DEPENDENCY_REGISTRY_PASSWORD`. Keep publishing settings separate.

Registry/API failures now block checks, scans and promotion instead of allowing a false
availability result or a local-chart substitution. Fix access/connectivity rather than bypassing
the check. See [configuration](docs/configuration.md#helm-chart-publishing--authentication).

## 1.1.0

No migration is required. The GitLab template API remains unchanged.

## 1.0.0

No migration is required for the initial release.
