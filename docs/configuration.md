# Configuration

## Key Variables & Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `PROJECT_CACHE_KEY` | Yes | — | Stable cache key shared by the stack's dependency-download job and every job that restores its dependency cache, including `Image:Build`. Use the stack name (`python`, `java`, `node`, `go`, or `terraform`), optionally followed by a monorepo scope or Terraform root such as `node-admin` or `terraform-network`; do not append a lockfile hash. `common/` defaults it to an empty string, but declare a nonempty value so cache readers restore the warmed cache. |
| `IMAGE_REPOSITORY` | No | `${CI_PROJECT_PATH}` in the GitLab registry | A path in `IMAGE_REGISTRY` (e.g. `myorg/web-app`), or one or more full refs `host/path` (primary first). See [Registries](#registries). |
| `IMAGE_REGISTRY` | No | `CI_REGISTRY` | Registry host for a path in `IMAGE_REPOSITORY`. |
| `CHART_REPOSITORY` | No | `helm`, i.e. `oci://${CI_REGISTRY_IMAGE}/helm` | An OCI path in `CHART_REGISTRY` without the chart name, or one or more full refs (primary first). Docker Hub uses the namespace root, e.g. `<namespace>`. |
| `CHART_REGISTRY` | No | Empty: the project's GitLab container registry | OCI host, optionally with a port, for a path in `CHART_REPOSITORY`. |
| `IMAGE_DEV_REPOSITORY_SUFFIX` / `CHART_DEV_REPOSITORY_SUFFIX` | No | `/dev` | Candidate repository suffix for every registry without its own `dev` in `REGISTRY_CONFIG`. On Docker Hub an image suffix uses `-`, and charts keep candidates in the release repository. |
| `REGISTRY_CONFIG` | Several registries | — | File variable, YAML or JSON: `<host>: {username, password, dev}`. Credentials and the candidate suffix per registry. |
| `DEPLOY_IMAGE_REPOSITORY` / `DEPLOY_CHART_REPOSITORY` | No | The primary destination | The destination (a full ref) that deploys, deploy validation and remote scans read. Set it per environment to make a cluster pull from its own registry. |
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

## Registries

Images and Helm charts are published to one or more OCI registries. Charts are OCI artifacts
in a container registry; the GitLab Helm *package* registry is not used.

### Defaults

With nothing configured, everything goes to the project's GitLab container registry with the
CI job token:

| Artifact | Release | Candidate |
| --- | --- | --- |
| Image | `${CI_REGISTRY_IMAGE}` | `${CI_REGISTRY_IMAGE}/dev` |
| Chart | `oci://${CI_REGISTRY_IMAGE}/helm` | `oci://${CI_REGISTRY_IMAGE}/helm/dev` |

The job token reads and writes only the project's own registry. Another project's registry,
even on the same instance, needs a deploy token with `write_registry` (see below).

### One registry

```yaml
variables:
  IMAGE_REGISTRY: registry.example.com
  IMAGE_REPOSITORY: company/payment-service
  IMAGE_DEV_REPOSITORY_SUFFIX: /dev
  CHART_REGISTRY: registry.example.com
  CHART_REPOSITORY: company/payment-service/charts
  CHART_DEV_REPOSITORY_SUFFIX: /dev
# CI/CD variables (masked): IMAGE_REGISTRY_USERNAME, IMAGE_REGISTRY_PASSWORD,
#                           CHART_REGISTRY_USERNAME, CHART_REGISTRY_PASSWORD
```

### Several registries

List full refs, primary first, and put the credentials in `REGISTRY_CONFIG`:

```yaml
variables:
  IMAGE_REPOSITORY: "${CI_REGISTRY_IMAGE} quay.io/company/payment-service docker.io/company/payment-service"
  CHART_REPOSITORY: "${CI_REGISTRY_IMAGE}/helm docker.io/company"
```

```yaml
# REGISTRY_CONFIG: a File variable on the group, YAML or JSON
quay.io:   { username: "robot$ci", password: "..." }
docker.io: { username: "ci-bot",   password: "...", dev: "-dev" }
# registry.gitlab.com: { dev: "/rc" }   # options only: keeps the job token
```

- **The project's own registry** needs no entry: the job token is always added for
  `CI_REGISTRY`. Listing `${CI_REGISTRY_IMAGE}` first makes it the primary; later, a copy.
- **`dev`** sets the candidate suffix for that registry. Without it the
  `*_DEV_REPOSITORY_SUFFIX` default applies.
- **Same host, different account.** Credentials are kept per host, so a client that needs
  its own account on a shared host sets its own `REGISTRY_CONFIG` on its subgroup. Pushing
  to another GitLab project on this instance needs a `registry.gitlab.com` entry with a group
  deploy token; it replaces the job token for that host.
- **Chart dependencies** on any listed host authenticate from the same entries.
  `CHART_DEPENDENCY_REGISTRY` with its username/password pair still works for a host that
  is not a destination.

### Credentials

Every job that talks to a registry writes one Docker `config.json` from the sources below and
points docker, buildx, crane, Trivy and helm at it (`DOCKER_CONFIG`,
`REGISTRY_AUTH_FILE`, `HELM_REGISTRY_CONFIG`). Buildah builds publish to one registry and
log in with `IMAGE_REGISTRY_USERNAME` / `_PASSWORD` as before. For the same host a later
source wins:

1. the CI job token for `CI_REGISTRY`;
2. the dependency proxy (`CI_DEPENDENCY_PROXY_*`), so base images pull through it;
3. the `IMAGE_`, `CHART_` and `CHART_DEPENDENCY_REGISTRY_USERNAME` / `_PASSWORD` pairs;
4. `REGISTRY_CONFIG`.

Docker Hub entries are written for `docker.io`, `index.docker.io`, `registry-1.docker.io`
and `https://index.docker.io/v1/`. Secrets are never echoed.

### Publishing and copies

- **Candidates** are pushed to the primary's candidate repository, then copied by digest to
  every other destination's candidate repository.
- **Releases** are promoted on the primary: `Image:Promote` copies the candidate with Crane,
  sets the version label and tags `${TAG}`, `latest`, `${MAJOR_VERSION}` and
  `${MINOR_VERSION}`; `Chart:Promote` repackages the candidate at the release version. The
  result is then copied by digest to every other destination, aliases included.
- **Collision checks** (`Image:Check Existence`, `Chart:Check Existence`) look in every
  destination.
- Copies are checked by digest and skipped when the destination already holds it, so a rerun
  is safe. A failed destination is named, after every destination has been tried.

### Which registry is read

Deploys (ArgoCD, Komodo), deploy validation and remote scans (`image-scan`, `chart-scan`)
read the primary, unless `DEPLOY_IMAGE_REPOSITORY` / `DEPLOY_CHART_REPOSITORY` name another
destination. Set them as environment-scoped variables to make each cluster pull from its own
registry; a value that is not a destination fails with the list of valid ones. Every
destination holds the same digest, so any of them is safe to deploy from.

### GitLab instance requirements

`Common:Init` hands its values to later jobs as a dotenv report of at most 15 keys, within
the default limit of 20 on a self-managed instance (50 on GitLab.com). A project that writes
its own dotenv keys keeps the total under that limit, or an administrator raises it:

```bash
curl --request PUT --header "PRIVATE-TOKEN: <admin-token>" \
  "https://<gitlab-host>/api/v4/application/plan_limits?plan_name=default&dotenv_variables=50"
```

## DevOps Reference & Platform Defaults

### Group-Injected CI/CD Variables

Configure at the top-level GitLab Group (or instance settings) to automatically propagate to all projects:

- **Registries**: either `IMAGE_REGISTRY`, `IMAGE_REGISTRY_USERNAME`, `IMAGE_REGISTRY_PASSWORD`, `CHART_REGISTRY`, `CHART_REGISTRY_USERNAME`, `CHART_REGISTRY_PASSWORD` (one registry), or the `REGISTRY_CONFIG` File variable (any number). A client subgroup with its own accounts sets its own `REGISTRY_CONFIG`.
- **Security & Quality**: `SONAR_URL`, `SONAR_EXTERNAL_URL`, `SONARQUBE_TOKEN`, `TRIVY_HOST`
- **Deployment (GitOps)**: `ARGOCD_SERVER`, `ARGOCD_TOKEN`, `KOMODO_SERVER`, `KOMODO_API_KEY`, `KOMODO_API_SECRET`, `GITOPS_REPO_USERNAME`, `GITOPS_REPO_TOKEN`
  - `GITOPS_REPO_TOKEN` (or the `gitops_repo_token` input) clones and pushes the GitOps repository; without it the job uses `CI_JOB_TOKEN`, which can push to another project only from GitLab 19.
- **Notifications**: `RELEASE_MESSAGE_TEAMS_WORKFLOWS_URL`

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
