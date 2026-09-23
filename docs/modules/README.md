# Module catalog

Choose the module you are integrating; unrelated modules need not be loaded.

- [common](common.md) — Shared stages, rules, version initialization, release guards and scanner helpers.
- [nodejs](nodejs.md) — Node.js and TypeScript dependencies, npm builds, tests and linting.
- [python](python.md) — Python dependencies with uv, package builds, tests and code-quality checks.
- [golang](golang.md) — Go modules, binary builds, tests, formatting and static/security analysis.
- [java](java.md) — Java/Maven dependency preparation, builds, tests and version handling.
- [image](image.md) — Docker/BuildKit and Buildah packaging, testing, publishing, scanning and promotion.
- [chart](chart.md) — Helm validation, optional unit tests, packaging, registry publishing, scanning and promotion.
- [terraform](terraform.md) — Terraform validation, formatting, documentation, module testing and infrastructure lifecycle jobs.
- [sonarqube](sonarqube.md) — Source analysis and quality gates, including available test-coverage reports.
- [secret-scanning](secret-scanning.md) — Git-history scanning to detect exposed credentials before release.
- [license](license.md) — Dependency-license compliance checks and documented license exceptions.
- [sbom](sbom.md) — CycloneDX dependency inventories and vulnerability scanning.
- [gitops](gitops.md) — Argo CD and Komodo deployment configuration, target validation and delivery.
- [release-notify](release-notify.md) — Release assets, notes, publication and Teams notifications.
- [migration-guide](migration-guide.md) — Migration Markdown validation, release-section checks and upgrade-note extraction.
- [mono](mono.md) — Path-based child pipelines and shared initialization for monorepo projects.

[Documentation index](../../README.md)
