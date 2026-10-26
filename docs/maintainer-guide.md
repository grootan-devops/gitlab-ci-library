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

Registry targets, credential groups and logins go through the functions in
`.registry-functions` (`common/.gitlab-ci.yml`). YAML anchors do not cross
included files, so a job loads them with `- !reference [.registry-functions, script]`
as its own list item before any `registry_*` call; never put the reference inside
an anchored scalar such as `.chart-registry`. The functions do not exist in
`after_script`, which runs in a separate shell. They take the password on stdin
only, suspend shell tracing while they hold credentials, and log each tool in to a
registry once per job, so a loop over the repositories calls `registry_login` for
each one and repeats nothing.

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

## Releases and versioning

`VERSION` holds the release. A merge to the default branch tags it, and consumers pin that tag;
a branch is never a release reference. Every release adds a [`CHANGELOG.md`](../CHANGELOG.md)
entry and a [`MIGRATION.md`](../MIGRATION.md) section split into Required, Recommended and
Verify, even when nothing is required.

Releases follow semantic versioning for the public interface: job names, rule anchors,
variables, inputs, artifact paths and `docs/workflow-map.json`. Patch and minor releases stay
backward compatible within a major version. A breaking change needs a new major version and a
Required migration step. A deprecation is announced in the changelog and, where practical, kept
through at least the next minor release; security, correctness or upstream requirements may
remove unsafe behaviour sooner. A page describes the release it ships in: history belongs in the
changelog and migration guide.

## Workflow map

[`docs/workflow-map.json`](workflow-map.json) is the machine-readable form of the
[`WORKFLOW` options](pipeline-lifecycle.md#declaring-workflow-in-a-project) each module
provides. Audit tools read it at the release a project pins and refuse a release without it,
so change it in the same commit as the module:

- `modules.<file>.provides`: the options that dispatch the module's jobs.
- `modules.<file>.signature_jobs`: the job whose presence shows an option is active, so a
  project that disables it with `rules: [{when: never}]` has retired the option deliberately.
- `shared_options`: options several modules provide, such as `build` from every language
  module.

`schema` is the version of this contract. Raise it when a change to the file's shape, or to a
module, option or job name the file refers to, would make an older reader misjudge a project:
readers refuse a schema they do not know instead of guessing.

[Documentation index](../README.md)
