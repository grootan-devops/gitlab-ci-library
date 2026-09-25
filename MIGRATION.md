# Migration Guide

This document records required consumer actions when upgrading between releases.
Breaking changes must include an entry before release.

## 1.4.0

No consumer pipeline migration is required. Release migration notes (`RELEASE_MIGRATION.md`) are exported as job artifacts for the release notes description and are no longer uploaded to the Generic Package Registry as downloadable release assets. Default container base and builder images have been upgraded to their latest stable releases (`micro-root:1.1.0`, `micro-nginx:1.1.1`, `micro-python-3-12:1.1.1`, `micro-java-25:1.1.1`, `micro-node-24:1.1.1`, `toolkit:1.1.0`). Repositories that override these variables (`MICRO_*_BASE_IMAGE_TAG` or `TOOLKIT_IMAGE_TAG`) retain their pinned values.

## 1.3.0

No migration is required. The GitLab template API remains unchanged.

## 1.2.0

The documentation restructuring requires no consumer configuration changes; update bookmarks
to moved sections and start from the README index.

`.Chart:UnitTest` now defaults `MOCK_CHART` to `tests` instead of `test`. Rename the
mock consumer chart directory to `tests/`, or keep the old location temporarily by setting
`MOCK_CHART: test`. Its unit-test suites must be under
`${CHART_DIR}/${MOCK_CHART}/tests/*_test.yaml`.

Python, Java, and Node consumers define stack-scoped dependency jobs:
`Python:Dependency:Download`, `Java:Dependency:Download`, or `Node:Dependency:Download`,
extending the matching language runtime and hidden template. Go retains the library-provided
`Go:Dependency:Download` job. If you copied an interim generic `Dependency:Download` example,
rename it to the appropriate stack job and extend the matching hidden template.

Dependency caches now use the stable `PROJECT_CACHE_KEY` directly instead of adding a
`cache:key:files` lockfile digest. Keep the same key and cache path on the dependency warmer
and `Image:Build`; the latter must restore the `.uv`, `.npm`, `.m2`, or `.cache` directory
from the runner cache so the Dockerfile can install dependencies offline. No cache key
override is needed when the existing project key is already shared by those jobs.
Use read-write (`rw`) BuildKit bind mounts for these package-manager caches, and ensure the
mount source is admitted by `.dockerignore`.

The Python CI anchor now uses the toolkit Python 3.12 build image (not the production micro
image) and clears its entrypoint for GitLab Runner. If a consumer
overrides it with `["/bin/bash"]`, remove that override to inherit `.Python:12`'s
`entrypoint: [""]`. No micro-image rebuild is required for this template fix.
The Python container example now uses the `app/`, `main.py`, and `config.py` layout and a
read-write `.uv` BuildKit bind mount. Adapt those source paths and the exposed port to the
actual service when copying the example.

The Docker image build passes `CI_PROJECT_DIR` and `PROJECT_PATH` as build arguments. Use
`PROJECT_PATH` in Dockerfiles that need to locate an application in a monorepo; do not rely
on `CI_BUILDS_DIR`, which is no longer passed.

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
