# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Use `tests` as the default mock consumer chart directory for `.Chart:UnitTest` and
  explicitly select its nested suite files.

## [1.2.0] - 2026-09-23

### Changed

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
