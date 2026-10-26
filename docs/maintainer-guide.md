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

A job extends a rule anchor from `common/` when one admits the workflows it needs. A new
rule set starts with `- !reference [.verify-rules, rules]` (merge requests to a protected
master, and monorepo child pipelines), adds one manual-run line,
`'$CI_PIPELINE_SOURCE =~ /^(web|api)$/ && $WORKFLOW =~ /^(full-pipeline|lint)$/'`, and ends
with `- when: never`. An identical set references the existing one instead of copying it. Keep
anchors that no library job uses, such as `.mr-only-rules`, `.master-fast-track-rules`,
`.deploy-workflow-rules` and `.full-and-mr-rules`: projects extend them in their own overrides.

## Self-linting

`.github/workflows/pr.yml` runs Actionlint and ShellCheck for repository-owned
workflows and standalone shell scripts. Its reusable lint job runs Yamllint on
tracked YAML and Markdownlint on Markdown, including changelog and migration
notes. The reusable release check verifies the required changelog and migration
sections. The same lint and check workflows can be dispatched separately.

## Migration Guide & Standard

The initial public release is `1.0.0`. No migration is required. Future breaking releases will document consumer actions in [`MIGRATION.md`](../MIGRATION.md).

[Documentation index](../README.md)
