# Configuration

## Key Variables & Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `PROJECT_CACHE_KEY` | Yes | — | Stable cache key shared by the stack's dependency-download job and every job that restores its dependency cache, including `Image:Build`. Use the stack name (`python`, `java`, `node`, `go`, or `terraform`), optionally followed by a monorepo scope such as `node-admin`; do not append a lockfile hash. `common/` defaults it to an empty string, but declare a nonempty value so cache readers restore the warmed cache. |
| `IMAGE_REPOSITORY` | Yes* | — | Image repository path in registry (e.g. `myorg/web-app`). |
| `CHART_REPOSITORY` | OCI publishing | `helm` | OCI namespace/path without the chart name. Set for your registry; Docker Hub uses the namespace root, e.g. `grootantech`. Ignored by GitLab package publishing. |
| `CHART_REGISTRY` | No | Empty | OCI hostname, optionally with port. Empty selects the current project's GitLab Helm Package Registry. |
| `CHART_DEV_REPOSITORY_SUFFIX` | No | `/dev` | Candidate OCI path suffix. Ignored on Docker Hub, where candidate and release versions share one repository. |
| `HELM_CHANNEL` | No | `dev` (RC builds) / `stable` (releases) | GitLab Helm Package Registry channel that `Chart:Push` publishes to. Set explicitly to override the automatic RC/release split. |
| `MIGRATION_FILE_NAME` | No | `./MIGRATION.md` | Path to the repository migration guide markdown file. |
| `RELEASE_MIGRATION_FILE_NAME` | No | `RELEASE_MIGRATION.md` | Target artifact file for extracted release migration notes. |
| `PROJECT_PATH` | No | `.` | Root directory of the application inside the git repository. |
| `DOCKERFILE` | No | `Dockerfile` | Path to Dockerfile for image linting and building. |
| `CHART_DIR` | No | `./chart` | Path to the Helm chart folder. |
| `RELEASE_VERSION` | No | — | Semantic version (e.g. `1.5.0`). If omitted, read from `version.env` or `Chart.yaml`. |
| `RELEASE_VERSION_SUFFIX` | No | — | Suffix appended to version (e.g. `backend` &rarr; `1.5.0-backend`). |
| `TARGET_VERSION` | No | — | Unified target version/tag (e.g. `1.8.0`, `latest`). Used as: deployment version override in `deploy`, image tag in `image-scan`, remote chart version in `chart-scan`, or release version override. |
| `DEPLOY_TARGET` | Manual deploy | `komodo-staging` | Target platform and environment when running manual `deploy` workflow. |
| `HELM_TEST_VALUES` | No | — | YAML override content supplied to Helm lint and chart scan. |
| `USE_DOCKER_BUILDX` | No | `"false"` | Set to `"true"` to enable BuildKit container layer caching. |
| `TRIVY_IGNORE_CONFIG_FILE` | No | `ignored-cves.yml` | Path to CVE and license suppression configuration. |
| `TRIVY_IGNORE_CVES` | No | `KSV-0011 ...` | Space-separated list of default suppressed K8s/IaC misconfiguration IDs. |
| `TRIVY_IGNORED_LICENSES` | No | `MIT,Apache-2.0,...` | Comma-separated list of default suppressed safe/permissive licenses. |
| `RELEASE_MESSAGE_TEAMS_WORKFLOWS_URL` | Teams | — | Power Automate webhook URL(s) for release notification cards. |

## DevOps Reference & Platform Defaults

### Group-Injected CI/CD Variables

Configure at the top-level GitLab Group (or instance settings) to automatically propagate to all projects:

- **Registries**: `IMAGE_REGISTRY`, `IMAGE_REGISTRY_USERNAME`, `IMAGE_REGISTRY_PASSWORD`, `CHART_REGISTRY`, `CHART_REGISTRY_USERNAME`, `CHART_REGISTRY_PASSWORD`
  - Chart settings are independent of image settings. A nonempty `CHART_REGISTRY` selects OCI publishing; leave it unset for GitLab packages.
- **Security & Quality**: `SONAR_URL`, `SONAR_EXTERNAL_URL`, `SONARQUBE_TOKEN`, `TRIVY_HOST`
- **Deployment (GitOps)**: `ARGOCD_SERVER`, `ARGOCD_TOKEN`, `KOMODO_SERVER`, `KOMODO_API_KEY`, `KOMODO_API_SECRET`
- **Notifications**: `RELEASE_MESSAGE_TEAMS_WORKFLOWS_URL`

### Helm Chart Publishing & Authentication

With **`CHART_REGISTRY` set**, charts publish over OCI. Set the hostname (no URL scheme),
`CHART_REPOSITORY`, and the masked `CHART_REGISTRY_USERNAME` / `CHART_REGISTRY_PASSWORD`
pair. No image credentials are used. Only when the hostname equals `CI_REGISTRY`, omitting
both chart credentials uses GitLab's job-scoped registry credentials. External registries
require their own explicit pair. Errors never switch the backend to GitLab packages.

- **Target**: `oci://${CHART_REGISTRY}/${CHART_REPOSITORY}`; Helm appends the chart name.
- **Candidates**: append `CHART_DEV_REPOSITORY_SUFFIX` (default `/dev`) to the repository.
- **Docker Hub**: set `CHART_REGISTRY=registry-1.docker.io` and `CHART_REPOSITORY=grootantech`.
  A chart named `tpl-library` uses `grootantech/tpl-library` for candidates and releases.
- **Promotion**: pull a candidate, repackage at the release tag and publish to production.
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
Without an override, configured OCI publishing credentials are reused. Public and `file://`
dependencies need no separate credentials. Leave `CHART_REGISTRY` empty when publishing to
GitLab packages, even when a private dependency needs this separate login.

### Container Image Publishing & Authentication

Images use the **OCI container registry** — not the Package Registry. `IMAGE_REGISTRY` defaults to `CI_REGISTRY`, the pipeline's own project registry, so the default path needs no configuration.

- **Target**: `${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}${IMAGE_REPOSITORY_SUFFIX}:${TAG}`. When `IMAGE_REGISTRY` is unset, `Common:Init` defaults it to `CI_REGISTRY` and re-derives `IMAGE_REPOSITORY` to `${CI_PROJECT_PATH}` — any value not already rooted at the project path is replaced. Chart repositories are configured independently.
- **Auth**: `.image-registry-login` runs `docker login` with the first credential that resolves — `IMAGE_REGISTRY_USERNAME` → `CI_REGISTRY_USER` → `gitlab-ci-token`, and `IMAGE_REGISTRY_PASSWORD` → `CI_REGISTRY_PASSWORD` → `CI_JOB_TOKEN`. For the project's own registry `CI_JOB_TOKEN` is always sufficient.
- **Pushing to another project's registry requires an explicit credential.** `CI_JOB_TOKEN` only authenticates against the pipeline's own project, or one that allowlists it under **Settings → CI/CD → Token Access**. Otherwise set `IMAGE_REGISTRY_USERNAME` / `IMAGE_REGISTRY_PASSWORD` to a deploy token carrying `read_registry` + `write_registry` on the *target* project.
- **Dependency proxy**: when `CI_DEPENDENCY_PROXY_*` are present, a second `docker login` authenticates the proxy so base images pull through it rather than from Docker Hub.
- **Dev vs production**: candidate builds push to `${IMAGE_REPOSITORY}${IMAGE_DEV_REPOSITORY_SUFFIX}`. At release, `Image:Promote` uses **Crane** to copy the manifest layerlessly from the dev path to the production path and tags it `${TAG}`, `latest`, `${MAJOR_VERSION}`, `${MINOR_VERSION}`.

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
