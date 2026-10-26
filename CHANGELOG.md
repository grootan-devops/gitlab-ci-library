# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.10.0] - 2026-10-26

### Added

- `.verify-rules` (`common/.gitlab-ci.yml`): merge requests to the default branch or a protected `*/master`, and monorepo child pipelines. Rule sets start with `- !reference [.verify-rules, rules]` instead of repeating both conditions.
- `.check-workflow-rules`: the `check` workflow's rule set, shared by `Chart:Check:Dependency` and `Terraform:Check:README`.
- `docs/workflow-map.json`: the `WORKFLOW` options each module provides and the job that shows an option is active, for audit tools to read at the release a project pins. `docs/maintainer-guide.md` says how to keep it in step with the modules.

### Changed

- Docker Hub image candidates go to `<repo>-dev`, because Docker Hub has no nested repositories and the `/dev` path was not valid there.
- `Deploy:ArgoCD:Validate:Chart`: logs in to the chart registry with its `CHART_REGISTRY_USERNAME` / `CHART_REGISTRY_PASSWORD` pair, or reads it anonymously when it has none. The CI job token is sent only to `CI_REGISTRY`.
- Every job that extends `.image-registry-login` defaults `IMAGE_REGISTRY` to `CI_REGISTRY`, as `Common:Init` does.
- `docs/maintainer-guide.md`: the release and versioning policy (public interface, semantic versioning, deprecations) replaces the initial-release note.
- Terraform jobs no longer look for `${PROJECT_PATH}/main.tf`: including `terraform/` opts a project in, as with every other module. `Terraform:Init`, `Terraform:Validate` and `Terraform:Lint` use the shared `.lint-workflow-rules`, and `Terraform:Module:Test` uses `.terraform-scan-rules`, as `Terraform:Scan` does.
- `Terraform:Init` no longer runs in the `build` and `check` workflows, where no job needs it.
- `Trivy:Cache:Warm` runs only in workflows with a Trivy scan. A repository with a `main.tf` no longer warms the cache in release pipelines or in the `lint`, `check` and `secret-scanning` workflows.
- Rule sets name their manual workflows with one regular expression, such as `$WORKFLOW =~ /^(full-pipeline|lint)$/`, instead of a chain of comparisons. Every job is admitted to exactly the pipelines it was before.
- `.unit-test-workflow-rules`, `.lifecycle-rules`, `.master-fast-track-rules` and `.terraform-check-rules` reference their identical `.build-test-rules`, `.common-init-rules`, `.release-rules` and `.check-workflow-rules` instead of copying them, and stay for projects that extend them. `.Node:Test:Unit` extends `.build-test-rules`, as the other unit-test templates do. `Chart:Values:Lint` and `Chart:Check:Dependency` extend `.lint-workflow-rules` and `.check-workflow-rules` instead of copying them.

### Removed

- `.terraform-workflow-rules` and `.terraform-module-test-rules`. Use `.lint-workflow-rules` and `.terraform-scan-rules`.

### Fixed

- Buildah `Image:Build`: the truncated `needs:` entry that stopped any pipeline including `image/.buildah.gitlab-ci.yml` from being created. It needs only `Common:Init`: Buildah builds micro images, not application images, so there is no `Project:Build` or dependency download to wait for. It takes the docker job's rules (`.image-build-workflow-rules`), so it runs only for merge request verification and `full-pipeline` or `image-build-and-push` runs. Without them it would have built an unused image in every pipeline, release pipelines included.
- Docker `Image:Build`, `Chart:Promote`: a relative `PROJECT_PATH` is no longer applied twice when `before_script` has already entered it.
- `WORKFLOW=image-scan`, `Deploy:Komodo:Validate:Image`: check the image in `CI_REGISTRY` when `IMAGE_REGISTRY` is unset, instead of `/<repository>`.
- `docs/modules/image.md`: lists `Image:Promote`, which is where the alias tags are applied (not `Image:Push`).
- `docs/pipeline-lifecycle.md`: a Terraform repository's `WORKFLOW` options include `secret-scanning`, which its include set has, and not `build`, where no Terraform job runs.
- A Terraform repository without `${PROJECT_PATH}/main.tf` no longer has its pipeline refused. `Terraform:Validate` and `Terraform:Lint` needed `Terraform:Init`, which that check had skipped.
- `Terraform:Lint`: restores the `terraform` cache that `Terraform:Init` fills, so `tflint --call-module-type=all` finds git and registry modules instead of failing with `module is not found. Did you run "terraform init"?`.

## [1.9.0] - 2026-10-01

### Added

- `docs/project-jobs.md`: job wrappers, the canonical `Project:Build` / `Project:Unit:Test` names, extends order, `optional:` on every `needs:`, inherited keys, `Project:Build`, split build and test jobs, script formatting.
- `docs/getting-started.md`: the complete include set, image-only repositories, conditional modules, module prerequisites and `.gitignore` entries.
- `docs/pipeline-lifecycle.md`: job responsibilities, declaring `WORKFLOW` options per project shape, the job class each workflow admits, and disabling an inherited job.
- `docs/docker.md`: micro base image limits, `DOCKER_BUILD_ARG_<NAME>` build arguments, the cache handoff to `Image:Build`, final-layer cleanup, `.dockerignore` rules, and a project base image with its `Dockerfile.base` and builder.
- `docs/security.md`: reviewing a consumer repository — secrets by value, pipeline posture and GitLab specifics.
- The per-stack project rules in the Node.js, Python, Go, Java and chart module guides; the SemVer requirement and changelog heading rule in `docs/modules/common.md`; `.betterleaksignore` baselines in `docs/modules/secret-scanning.md`.

### Changed

- `docs/docker.md`: PID 1 is always `ENTRYPOINT ["/usr/bin/dumb-init", "--"]` with the process or start script in `CMD`; `# renovate:` annotations are required only for public-registry image versions held in an `ARG`; comments are one line saying why; runtime-writable paths are chart mounts; never `ARG` a secret; the stack examples follow these rules, and the SPA example no longer copies `nginx.conf` into the image.

### Fixed

- `Terraform:Check:README` runs in the `check` workflow instead of `lint`, like every other drift check (new `.terraform-check-rules`).
- `argocd_server` / `ARGOCD_SERVER` take the Argo CD host without a scheme, as `argocd --server` expects: the input description, the `common/` example and the GitOps guide no longer show `https://`, and the sync-failure log prints a full link.
- `docs/pipeline-lifecycle.md`: the stage diagram and table follow the order `common/.gitlab-ci.yml` declares (`check` runs after `lint`) and list each job in the stage it runs in, including `Image:Promote` and `Chart:Promote`.
- `docs/configuration.md` documents `TRIVY_IGNORED_LICENSE_CLASSIFICATIONS` instead of the unused `TRIVY_IGNORED_LICENSES`.
- `docs/docker.md` numbers its rules continuously; the Python examples expose port 8080 and run under `dumb-init`.

## [1.8.2] - 2026-10-01

### Fixed

- `Deploy:ArgoCD:<env>` and `Deploy:Komodo:<env>` edit the GitOps file in place. Only the text of the
  value being set changes, and blank lines, spacing, comments and quoting are left as they were.
  Previously `yq -i` rewrote the whole file and dropped blank lines and extra spaces. A new key, or a
  value that cannot be edited in place, still goes through `yq`, applied as a patch that keeps blank
  lines where possible.

## [1.8.1] - 2026-09-30

### Added

- `gitops_repo_username` and `gitops_repo_token` inputs on the ArgoCD and Komodo GitOps components
  (defaults `GITOPS_REPO_USERNAME` / `GITOPS_REPO_TOKEN`) to clone and push the GitOps repository with
  a custom credential. `CI_JOB_TOKEN` stays the fallback; it can push to another project only from
  GitLab 19.

### Fixed

- `Deploy:ArgoCD:Validate:Image:<env>` now runs for every ArgoCD deploy, including chart-only
  deploys; it previously ran only when an image values file, image yq path or manifest file was set.
  A new `validate_image` input (default `true`) turns it off.
- `Deploy:ArgoCD:Validate:Image:<env>` applies the `Common:Init` registry defaults
  (`IMAGE_REGISTRY` from `CI_REGISTRY`, `IMAGE_REPOSITORY` from `CI_PROJECT_PATH`), which were
  missing for `WORKFLOW=deploy`.
- `Deploy:ArgoCD:<env>` writes `.chart.repoURL` for the channel that holds `TARGET_VERSION`
  (GitLab Helm `dev` for candidates, `stable` for releases, `HELM_CHANNEL` when set) instead of
  always `stable`, and resolves the OCI candidate path from `TARGET_VERSION` for `WORKFLOW=deploy`.
- `Deploy:ArgoCD:Validate:Chart:<env>` verifies the chart in that same GitLab Helm channel instead
  of in any channel.
- Documentation caught up with earlier releases: `.Java:Build`,
  `Common:Check:Library:Pin` run conditions, `SONAR_SCANNER_CLI_IMAGE_*` / `MD_LINT_IMAGE_*`,
  Python lint `.venv`/`.uv` exclusions, and removal of the non-existent `deploy/gitlab` component
  section.
- Documentation no longer hard-codes versions: include examples use a `<version>` placeholder and
  default image names and tags are referenced by variable (defaults live in `common/.gitlab-ci.yml`).
  The ArgoCD example shows the `WORKFLOW=deploy`, `DEPLOY_TARGET` and `TARGET_VERSION` setup.

## [1.8.0] - 2026-09-30

### Changed

- Updated sonarqube cli and mdl to use different image for running jobs instead of toolkit

## [1.7.0] - 2026-09-30

### Changed

- Bumped the Java 25 micro base image to `micro-java-25:1.2.0`, which adds `libstdc++` so JNI
  libraries linked against the C++ runtime (for example RocksDB) load at runtime.

## [1.6.0] - 2026-09-30

### Added

- Java build job

## [1.5.0] - 2026-09-29

### Changed

- Bumped micro python base iamge to `1.1.2`
- change mvn dep download command for verbose output

## [1.4.0] - 2026-09-25

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
