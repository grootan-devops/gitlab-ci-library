# Gitlab CI/CD Library

Release `1.2.0` · [Compatibility](https://github.com/grootan-devops/ai-skills/blob/main/COMPATIBILITY.md) · [Security](./SECURITY.md) · [Contributing](./CONTRIBUTING.md)

Shared GitLab CI/CD library

## Quick start

Choose your project shape in the [integration examples](docs/examples/README.md), then follow the
[getting-started guide](docs/getting-started.md). Keep only the modules your project needs.

Language modules use stack-specific dependency download jobs: `Python:Dependency:Download`,
`Java:Dependency:Download`, and `Node:Dependency:Download`. Go provides
`Go:Dependency:Download` directly. Their cache is warmed once and restored by `Image:Build`
with the same `PROJECT_CACHE_KEY`; see the [Python service example](docs/examples/python.md).
The Python CI download job uses the toolkit build image; the Dockerfile's micro image is
reserved for the production container.

## Documentation

| Task | Read |
| --- | --- |
| Set up a pipeline | [Getting started](docs/getting-started.md) |
| Understand triggers, dependencies and release promotion | [Pipeline lifecycle](docs/pipeline-lifecycle.md) |
| Configure variables, secrets and registries | [Configuration](docs/configuration.md) |
| Select reusable jobs and their contracts | [Module catalog](docs/modules/README.md) |
| Package an application and set Docker ignore rules | [Dockerfile standards](docs/docker.md) |
| Configure scanning, ignored CVEs and scan exit codes | [Security and scanning](docs/security.md) |
| Copy a complete project integration | [Integration examples](docs/examples/README.md) |
| Maintain this library and follow release conventions | [Maintainer guide](docs/maintainer-guide.md) |

## Reading with an AI assistant

Start here, select the relevant task, and follow only the linked pages needed for it.
Resolve relative links from the containing document and keep every page on the same
branch, tag, commit or local checkout, including uncommitted edits. Do not concatenate `docs/`.
Example pins such as `1.0.0` show syntax; they do not override the selected library source/ref.
Generate references from the resolved source and verify that it supports the feature being used.
For upgrades, also read [MIGRATION.md](MIGRATION.md) and [CHANGELOG.md](CHANGELOG.md).

## License

Copyright 2026 Grootan Technologies Pvt Ltd.

Licensed under the [GNU Affero General Public License v3.0](./LICENSE.md)
(`AGPL-3.0-only`). External contributions are not accepted; see
[CONTRIBUTING.md](./CONTRIBUTING.md) for bug and security reporting.
