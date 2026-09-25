# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-09-25

### Changed

- Excluded `RELEASE_MIGRATION.md` from package registry uploads in `Release:Upload`; preserved as a job artifact for release notes.
- Removed remote registry `buildcache` layer pushes and pulls (`--cache-from` and `--cache-to`) from BuildKit image builds.
- Restricted `Common:Check:Library:Pin` to PRs/MRs, `check`, and `full-pipeline` workflows (excluded from single-purpose image build/scan jobs).
- Cleaned up orphan Python unit test suite in favor of repository self-linting.
- Bumped default container base and builder images in `common/.gitlab-ci.yml` to latest stable releases (`micro-root:1.1.0`, `micro-nginx:1.1.1`, `micro-python-3-12:1.1.1`, `micro-java-25:1.1.1`, `micro-node-24:1.1.1`, `toolkit:1.1.0`).
- Pinned repository CI reusable workflow callers to `@1.3.1`.

### Fixed

- Propagate `/etc/hosts` and Docker authentication credentials (`config.json`) to the BuildKit container.
- Safeguard Dependency Proxy docker login with conditional credential check and graceful fallback.

## [1.3.0] - 2026-09-25

### Fixed

- Exclude `.venv` and `.uv` directories across Python linting jobs (`ruff`, `mypy`, `isort`, `pycodestyle`).
- Authenticate GitLab Dependency Proxy when present during container image builds.

## [1.2.0] - 2026-09-23

### Changed

- Use `tests` as the default mock consumer chart directory for `.Chart:UnitTest` and
  explicitly select its nested suite files.
- Split the README into a task index with focused module, configuration and integration guides.
- Restore stack-scoped dependency download examples and use the shared `PROJECT_CACHE_KEY` for cache handoff into image builds.
- Refresh the Python microservice example with the tested BuildKit `.uv` bind mount and application layout.
- Clarify that Python and Java CI anchors use build images, not production micro images, and document the Docker build path arguments.
- Preserve complete examples while reducing the documentation loaded for a single task.
- Describe each module's purpose in the module index.
- Select OCI publishing when `CHART_REGISTRY` is configured; otherwise use the current project's GitLab Helm Package Registry.
- Support independent private-dependency authentication without changing the publishing backend.

### Fixed

- Define chart helper anchors under hidden-job `script` fields so GitLab schema validation accepts them.
- Clear the Python runtime entrypoint so GitLab Runner can launch its shell instead of Bash reading a shell binary as a script.
- Make the required initialization and release-upload dependencies explicit with `optional: false`.
- Fail chart checks and promotion on registry/API errors instead of interpreting them as absent candidates.
- Scan dependencies from the pulled chart and keep Docker Hub candidate/release charts in one repository.

## [1.1.0] - 2026-09-22

### Changed

- Pinned the repository's GitHub Actions audit workflows to `github-ci-library` 1.0.0.
- Refreshed release metadata and documentation.

## [1.0.0] - 2026-09-19

### Added

- Initial public release.
