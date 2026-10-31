# Configuration

## Key Variables & Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `PROJECT_CACHE_KEY` | Yes | — | Stable cache key shared by the stack's dependency-download job and every job that restores its dependency cache, including `Image:Build`. Use the stack name (`python`, `java`, `node`, `go`, or `terraform`), optionally followed by a monorepo scope or Terraform root such as `node-admin` or `terraform-network`; do not append a lockfile hash. `common/` defaults it to an empty string, but declare a nonempty value so cache readers restore the warmed cache. |
| `IMAGE_REGISTRY` | No | `CI_REGISTRY` | Image registry host. Leave it unset with `PROJECT_REGISTRY_NAME`. |
| `IMAGE_REPOSITORY` | Yes* | — | Image repository path in registry (e.g. `myorg/web-app`). With `PROJECT_REGISTRY_NAME`, the full repositories instead (e.g. `registry.example.com/myorg/web-app quay.io/myorg/web-app`), the first being the primary. |
| `CHART_REPOSITORY` | OCI publishing | `helm` | OCI namespace/path without the chart name. With `PROJECT_REGISTRY_NAME`, the full repositories instead (e.g. `registry.example.com/helm`), the first being the primary, or a value without a registry for GitLab packages. Set for your registry; Docker Hub uses the namespace root, e.g. `<namespace>`. Ignored by GitLab package publishing. |
| `CHART_REGISTRY` | No | Empty | OCI hostname, optionally with port. Empty selects the current project's GitLab Helm Package Registry. Leave it unset with `PROJECT_REGISTRY_NAME`. |
| `PROJECT_REGISTRY_NAME` | Several registries | — | The `REGISTRY_CONFIG` group to publish with, e.g. `oneuptime/prod`. `IMAGE_REPOSITORY` and `CHART_REPOSITORY` then list full repositories, and `IMAGE_REGISTRY` and `CHART_REGISTRY` must be unset. See [Publishing to several registries](#publishing-to-several-registries). |
| `REGISTRY_CONFIG` | With `PROJECT_REGISTRY_NAME` | — | Credential groups as YAML or JSON, each mapping registry hosts to a `username` and `password`; a File variable on the top-level group. |
| `CHART_DEV_REPOSITORY_SUFFIX` | No | `/dev` | Candidate OCI path suffix. Ignored on Docker Hub, where candidate and release versions share one repository. |
| `HELM_CHANNEL` | No | `dev` (RC builds) / `stable` (releases) | GitLab Helm Package Registry channel that `Chart:Push` publishes to. Set explicitly to override the automatic RC/release split. |
| `MIGRATION_FILE_NAME` | No | `./MIGRATION.md` | Path to the repository migration guide markdown file. |
| `RELEASE_MIGRATION_FILE_NAME` | No | `RELEASE_MIGRATION.md` | Target artifact file for extracted release migration notes. |
| `PROJECT_PATH` | No | `.` | Root directory of the application inside the git repository. |
| `DOCKERFILE` | No | `Dockerfile` | Path to Dockerfile for image linting and building. |
| `CHART_DIR` | No | `./chart` | Path to the Helm chart folder. |
| `RELEASE_VERSION` | No | — | Semantic version (e.g. `1.2.3`). If omitted, read from `version.env` or `Chart.yaml`. |
| `RELEASE_VERSION_SUFFIX` | No | — | Suffix appended to version (e.g. `backend` &rarr; `1.2.3-backend`). |
| `TARGET_VERSION` | No | — | Unified target version/tag (e.g. `1.2.3`, `latest`). Used as: deployment version override in `deploy`, image tag in `image-scan`, remote chart version in `chart-scan`, or release version override. |
| `DEPLOY_TARGET` | Manual deploy | `komodo-staging` | Target platform and environment when running manual `deploy` workflow. |
| `HELM_TEST_VALUES` | No | — | YAML override content supplied to Helm lint and chart scan. |
| `USE_DOCKER_BUILDX` | No | `"true"` | Set to `"true"` to build images using a dedicated Docker BuildKit container instance (supports multi-platform and advanced container builds). |
| `SONAR_SCANNER_CLI_IMAGE_REPO` / `SONAR_SCANNER_CLI_IMAGE_TAG` | No | Set in `common/.gitlab-ci.yml` | Image for the `Sonarqube` job. |
| `MD_LINT_IMAGE_REPO` / `MD_LINT_IMAGE_TAG` | No | Set in `common/.gitlab-ci.yml` | Image for `.MD:Lint`, `Changelog:Lint` and `Migration:Lint`. |
| `TRIVY_IGNORE_CONFIG_FILE` | No | `ignored-cves.yml` | Path to CVE and license suppression configuration. |
| `TRIVY_IGNORE_CVES` | No | `KSV-0011 ...` | Space-separated list of default suppressed K8s/IaC misconfiguration IDs. |
| `TRIVY_IGNORED_LICENSE_CLASSIFICATIONS` | No | `notice,permissive,unencumbered` | Comma-separated Trivy license classifications `License:Scan` does not report. Accepts classification names or the groups `low` (notice, permissive, unencumbered), `medium` (reciprocal, unrecognized) and `high` (restricted). Waive an individual license in `ignored-cves.yml`. |
| `RELEASE_MESSAGE_TEAMS_WORKFLOWS_URL` | Teams | — | Power Automate webhook URL(s) for release notification cards. |

## GitLab instance requirements

`Common:Init` hands its values to later jobs as a dotenv report. A release pipeline writes 21
keys, and a chart project's three more. GitLab.com allows 50; a self-managed instance defaults
to 20 and rejects the report with `Dotenv files cannot have more than 20 variables`, which fails
`Common:Init` and skips the release. An administrator raises the limit once for the instance:

```bash
curl --request PUT --header "PRIVATE-TOKEN: <admin-token>" \
  "https://<gitlab-host>/api/v4/application/plan_limits?plan_name=default&dotenv_variables=50"
```

## DevOps Reference & Platform Defaults

### Group-Injected CI/CD Variables

Configure at the top-level GitLab Group (or instance settings) to automatically propagate to all projects:

- **Registries**: `IMAGE_REGISTRY`, `IMAGE_REGISTRY_USERNAME`, `IMAGE_REGISTRY_PASSWORD`, `CHART_REGISTRY`, `CHART_REGISTRY_USERNAME`, `CHART_REGISTRY_PASSWORD`
  - Chart settings are independent of image settings. A nonempty `CHART_REGISTRY` selects OCI publishing; leave it unset for GitLab packages.
- **Registry credential groups**: `REGISTRY_CONFIG`, one File variable holding the credentials of every registry, grouped per client or organisation, so a project names its group with `PROJECT_REGISTRY_NAME` and needs no registry credentials of its own.
- **Security & Quality**: `SONAR_URL`, `SONAR_EXTERNAL_URL`, `SONARQUBE_TOKEN`, `TRIVY_HOST`
- **Deployment (GitOps)**: `ARGOCD_SERVER`, `ARGOCD_TOKEN`, `KOMODO_SERVER`, `KOMODO_API_KEY`, `KOMODO_API_SECRET`, `GITOPS_REPO_USERNAME`, `GITOPS_REPO_TOKEN`
  - `GITOPS_REPO_TOKEN` (or the `gitops_repo_token` input) clones and pushes the GitOps repository; without it the job uses `CI_JOB_TOKEN`, which can push to another project only from GitLab 19.
- **Notifications**: `RELEASE_MESSAGE_TEAMS_WORKFLOWS_URL`

### Helm Chart Publishing & Authentication

With **`CHART_REGISTRY` set**, charts publish over OCI. Set the hostname (no URL scheme),
`CHART_REPOSITORY`, and the masked `CHART_REGISTRY_USERNAME` / `CHART_REGISTRY_PASSWORD`
pair. No image credentials are used. Only when the hostname equals `CI_REGISTRY`, omitting
both chart credentials uses GitLab's job-scoped registry credentials. External registries
require their own explicit pair. Errors never switch the backend to GitLab packages.

- **Target**: `oci://${CHART_REGISTRY}/${CHART_REPOSITORY}`, or with `PROJECT_REGISTRY_NAME` each full repository `CHART_REPOSITORY` lists; Helm appends the chart name.
- **Auth**: the pair, or the job token on `CI_REGISTRY`; with a group, each registry's credentials in it.
- **Candidates**: append `CHART_DEV_REPOSITORY_SUFFIX` (default `/dev`) to the repository.
- **Docker Hub**: set `CHART_REGISTRY=registry-1.docker.io` and `CHART_REPOSITORY=<namespace>`.
  A chart named `<chart>` uses `<namespace>/<chart>` for candidates and releases.
- **Promotion**: pull a candidate from the primary repository, repackage at the release tag and
  publish to production there, then publish the same package to every other repository.
  Confirmed absence permits the existing warned working-tree fallback; lookup and pull
  errors stop the release instead.

With **`CHART_REGISTRY` unset or empty**, charts publish to the project's own
[GitLab Helm Package Registry](https://docs.gitlab.com/user/packages/helm_repository/).
The package registry must be enabled and the job token must have publishing access.

- **Endpoint**: `POST ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/helm/api/<channel>/charts`
- **Auth**: `gitlab-ci-token:${CI_JOB_TOKEN}`; no custom registry credentials are needed.
- **Channels**: `dev` for release-candidate builds (any version carrying `RC_VERSION_SUFFIX`), `stable` for releases. A `stable` publish is also mirrored into `dev` so downstream dev consumers resolve a single channel. Override with `HELM_CHANNEL`.
- **Consuming a published chart**:

  ```bash
  helm repo add myproj "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/helm/stable" \
    --username gitlab-ci-token --password "${CI_JOB_TOKEN}"
  ```

  Published charts are browsable under **Deploy → Package Registry** in the project.

`HELM_CHANNEL` overrides the push channel only. Automatic remote scans and promotion use
`dev` / `stable`, so keep those channels for automatic candidate promotion. Package version
collision checks match the exact name/version project-wide; API errors fail the check.
There is no HTTP backend selector or generic HTTP upload support.

### Private Chart Dependencies

For dependencies on a different OCI host, set `CHART_DEPENDENCY_REGISTRY` and the masked
`CHART_DEPENDENCY_REGISTRY_USERNAME` / `CHART_DEPENDENCY_REGISTRY_PASSWORD` pair.
These authenticate dependency pulls only and never select the publishing backend.
Without an override, the chart registry's credentials are reused; with a group, Helm logs in to
every registry `CHART_REPOSITORY` names. Public and `file://` dependencies need no separate
credentials. Leave `CHART_REGISTRY` empty when publishing to GitLab packages, even when a
private dependency needs this separate login.

### Container Image Publishing & Authentication

Images use the **OCI container registry** — not the Package Registry. `IMAGE_REGISTRY` defaults to `CI_REGISTRY`, the pipeline's own project registry, so the default path needs no configuration.

- **Target**: `${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}${IMAGE_REPOSITORY_SUFFIX}:${TAG}`; with `PROJECT_REGISTRY_NAME`, each full repository `IMAGE_REPOSITORY` lists takes the place of `${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}`. When `IMAGE_REGISTRY` is unset without a group, every image job defaults it to `CI_REGISTRY` and re-derives `IMAGE_REPOSITORY` to `${CI_PROJECT_PATH}` — any value not already rooted at the project path is replaced. Chart repositories are configured independently.
- **Docker Hub**: has no nested repositories, so the `/dev` candidate suffix becomes `-dev` there (`<namespace>/web-app-dev`).
- **Auth**: `.image-registry-login` runs `docker login` to the primary registry only, with the first credential that resolves — `IMAGE_REGISTRY_USERNAME` → `CI_REGISTRY_USER` → `gitlab-ci-token`, and `IMAGE_REGISTRY_PASSWORD` → `CI_REGISTRY_PASSWORD` → `CI_JOB_TOKEN` — or, with a group, the primary registry's credentials in it. For the project's own registry `CI_JOB_TOKEN` is always sufficient. Jobs that write to the other repositories log in to each of their registries once.
- **Pushing to another project's registry requires an explicit credential.** `CI_JOB_TOKEN` only authenticates against the pipeline's own project, or one that allowlists it under **Settings → CI/CD → Token Access**. Otherwise set `IMAGE_REGISTRY_USERNAME` / `IMAGE_REGISTRY_PASSWORD` to a deploy token carrying `read_registry` + `write_registry` on the *target* project.
- **Dependency proxy**: when `CI_DEPENDENCY_PROXY_*` are present, a second `docker login` authenticates the proxy so base images pull through it rather than from Docker Hub.
- **Dev vs production**: candidate builds push to `${IMAGE_REPOSITORY}${IMAGE_DEV_REPOSITORY_SUFFIX}`. At release, `Image:Promote` uses **Crane** to copy the manifest layerlessly from the dev path to the production path and tags it `${TAG}`, `latest`, `${MAJOR_VERSION}`, `${MINOR_VERSION}`. With a group this happens in the primary repository, and the released image is then copied by digest, with the same tags, to every other repository.

### Publishing to several registries

A project publishes each artifact to one registry, set by `IMAGE_REGISTRY` and
`CHART_REGISTRY`, or to several with a credential group. `REGISTRY_CONFIG`, a File variable on
the top-level group, holds the groups: each maps the registries one client or organisation uses
to their credentials. `PROJECT_REGISTRY_NAME` names the group a project publishes with, and its
`IMAGE_REPOSITORY` and `CHART_REPOSITORY` list the full repositories to publish to.

```yaml
# REGISTRY_CONFIG, a File variable on the top-level group
oneuptime/prod:
  registry.example.com:
    username: 'robot$ci'
    password: '<token>'
  quay.io:
    username: 'oneuptime+ci'
    password: '<token>'
  docker.io:
    username: 'oneuptime'
    password: '<access token>'
oneuptime/dev:
  registry.example.com:
    username: 'robot$dev'
    password: '<token>'
```

```yaml
variables:                        # IMAGE_REGISTRY and CHART_REGISTRY left unset
  PROJECT_REGISTRY_NAME: oneuptime/prod
  IMAGE_REPOSITORY: "registry.example.com/core/api quay.io/oneuptime/api docker.io/oneuptime/api"  # the first is the primary
  CHART_REPOSITORY: "registry.example.com/helm registry-1.docker.io/oneuptime"
```

A merge request pipeline of version `1.4.0` with these variables publishes:

| Repository | Candidate |
| --- | --- |
| `registry.example.com/core/api` | `registry.example.com/core/api/dev:1.4.0-rc.<pipeline>-<mr>` |
| `quay.io/oneuptime/api` | `quay.io/oneuptime/api/dev:1.4.0-rc.<pipeline>-<mr>` |
| `docker.io/oneuptime/api` | `docker.io/oneuptime/api-dev:1.4.0-rc.<pipeline>-<mr>` |
| `registry.example.com/helm` | `oci://registry.example.com/helm/dev/<chart>`, version `1.4.0-rc.<pipeline>-<mr>` |
| `registry-1.docker.io/oneuptime` | `oci://registry-1.docker.io/oneuptime/<chart>`, version `1.4.0-rc.<pipeline>-<mr>` |

- **A group** is any name without spaces, such as `client/org`, mapping registry hosts,
  optionally with a port, to a `username` and a `password`. A registry appears once in a
  group, so the repositories on it share its account. Hosts match ignoring case, and
  `docker.io`, `index.docker.io` and `registry-1.docker.io` are one registry. Several groups
  can share an account through a YAML anchor, and JSON is read as well.
- **Quote every username and password.** YAML reads an unquoted `0123` as a number, which is
  refused, and ends an unquoted value at a space followed by `#`, which cannot be detected.
  Single quotes keep every character as written; write a `'` inside them as `''`.
- **The project's own registry needs no entry.** A repository on `CI_REGISTRY` logs in with the
  CI job token, unless the group holds credentials for that registry.
- **Full repositories.** With a group, each entry of `IMAGE_REPOSITORY` and `CHART_REPOSITORY`
  is `<registry>/<path>`, separated by spaces or commas, and its registry must be in the group
  or be `CI_REGISTRY`. A chart's may start with `oci://`; neither carries a tag. A
  `CHART_REPOSITORY` without a registry, such as the default `helm`, still selects the project's
  Helm package registry. The first of each is the artifact's primary: base images are pulled
  from it, scans and the deploy components read from it, and `Common:Init` writes its host to
  `init.env` as `IMAGE_REGISTRY` and `CHART_REGISTRY`, and its paths as
  `IMAGE_CHECK_REPOSITORY`, `IMAGE_PUSH_REPOSITORY`, `CHART_DEV_REPOSITORY` and
  `CHART_PUSH_REPOSITORY`. `IMAGE_REPOSITORY` and `CHART_REPOSITORY` keep the full
  repositories, comma-joined. No `init.env` key is added. Docker Hub rules apply per
  repository.
- **Docker Hub**: write images as `docker.io/<namespace>/<name>` and charts as
  `registry-1.docker.io/<namespace>`, the host Helm pushes to. A group's `docker.io` serves both.
- **Checked before anything is built.** `Common:Init` resolves the full repositories and checks
  that each registry has a username and password in the group, or is `CI_REGISTRY`, so a
  missing account or a registry outside the group stops the pipeline there.
- **Buildah projects publish to one registry.** The Buildah `Image:Build` is for internal
  images, so a project that includes `image/.buildah.gitlab-ci.yml` keeps a single
  `IMAGE_REGISTRY` rather than `PROJECT_REGISTRY_NAME`.
- **Every candidate and release reaches every repository.** `Image:Push` and `Chart:Push`
  publish to each one; a release is promoted once, in the primary, and the released image is
  then copied by digest, with its `latest`, major and minor tags, so every repository ships the
  bytes that were scanned. A released chart is published as the same package.
- **Every repository is tried before a job fails**, and the job names each one that was
  refused. **Collision checks** look for the release tag and chart version in every repository.
- **One way or the other.** `PROJECT_REGISTRY_NAME` set together with `IMAGE_REGISTRY` or
  `CHART_REGISTRY` is ambiguous: `Common:Init` fails as its very first step, naming both, so no
  other job runs. `Workflow:Validate:Variables` does the same for the `image-scan`,
  `chart-scan` and `deploy` workflows, which skip `Common:Init`. To use a credential group in
  one project while its GitLab group sets `IMAGE_REGISTRY`, override `IMAGE_REGISTRY` with an
  empty value on that project. With a credential group, the `IMAGE_`/`CHART_REGISTRY_USERNAME`
  and `_PASSWORD` variables are ignored.
- **Errors name the group and the registry, never their values**: a group `REGISTRY_CONFIG`
  does not define, a registry the group does not have, a repository that is not
  `<registry>/<path>` or is listed twice, a registry without a quoted username and password,
  two keys for one registry, and AWS ECR (`rolearn`, `*.dkr.ecr.*`), which is not supported.
- **Define `REGISTRY_CONFIG` once**, as a **File** variable on the top-level group; an inline
  value works too. Turn off **Expand variable reference** for it, because Harbor robot accounts
  contain `$`.
- **It cannot be masked**, so never print it, and avoid `CI_DEBUG_TRACE` in projects that use
  it; the functions suspend shell tracing while they handle credentials.
- **A protected variable is not available to merge request pipelines** from unprotected
  branches, and every candidate build needs it.
- **Check the file before saving it** with `yq '.' registry-config.yaml`, and create the
  repository, or the Harbor project, in every registry before the first push.

> [!IMPORTANT]
> **Upgrade every include together.** The image, chart and deploy templates of `1.13.0` load
> the registry functions from `common`, so every include must point at the same release.
> Releases before `1.13.0` ignore `PROJECT_REGISTRY_NAME` and would take a full repository for
> a path: set the group and the full repositories on a project as it moves to `1.13.0`, or on a
> GitLab group only once every project below it includes `1.13.0` or later.

---

### Chart unit tests (optional, chart-publishing repositories only)

`.Chart:UnitTest` is a hidden template, so it costs nothing until a repository asks for it:

```yaml
Chart:UnitTest:
  extends: .Chart:UnitTest
  variables:
    MOCK_CHART: tests
```

It renders a mock consumer chart with [helm-unittest](https://github.com/helm-unittest/helm-unittest)
and attaches the JUnit report to the merge request. Declare it when the repository
**publishes a chart other charts depend on** — a library chart, or a widely reused
component — where a template change can break consumers silently. An application chart
that only deploys its own service has nothing to assert here that `Chart:Lint` does not
already cover.

Prerequisites: the `unittest` plugin must be present in the job image, and the mock
consumer chart must depend on the chart under test (e.g. `repository: "file://.."`).

[Documentation index](../README.md)
