# Maintainer guide

## Repository layout

Each module directory (`common/`, `chart/`, `image/`, `release/`, and the
language and deployment modules) owns reusable `.gitlab-ci.yml` templates.
The `.github/workflows/` directory runs this repository's own verification;
it is not a consumer pipeline. Start from [the module index](modules/README.md)
when changing a template.

## Template and script conventions

Keep public job names, `extends` relationships, inputs, and artifact paths
compatible with the selected migration guide. Shell commands live in YAML
`script`, `before_script`, or `after_script` blocks; keep them valid Bash and
do not print credentials. New standalone `.sh` files are checked by ShellCheck.

## Self-linting

`.github/workflows/pr.yml` runs Actionlint and ShellCheck for repository-owned
workflows and standalone shell scripts. Its reusable lint job runs Yamllint on
tracked YAML and Markdownlint on Markdown, including changelog and migration
notes. The reusable release check verifies the required changelog and migration
sections. The same lint and check workflows can be dispatched separately.

## Migration Guide & Standard

The initial public release is `1.0.0`. No migration is required. Future breaking releases will document consumer actions in [`MIGRATION.md`](../MIGRATION.md).

[Documentation index](../README.md)
