# Publishing to several registries

A service publishes its image and chart to its own GitLab registry, which is the primary, and
copies both to Quay and Docker Hub. Deploys to a customer cluster pull from Docker Hub.

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: node
  IMAGE_REPOSITORY: "${CI_REGISTRY_IMAGE} quay.io/company/payment-service docker.io/company/payment-service"
  CHART_REPOSITORY: "${CI_REGISTRY_IMAGE}/helm docker.io/company"

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'
```

```yaml
# REGISTRY_CONFIG: File variable on the group (variable expansion off)
quay.io:   { username: "company+ci", password: "..." }
docker.io: { username: "company-ci", password: "...", dev: "-dev" }
```

| Artifact | Destination | Release | Candidate |
| --- | --- | --- | --- |
| Image | GitLab (primary) | `${CI_REGISTRY_IMAGE}` | `${CI_REGISTRY_IMAGE}/dev` |
| Image | Quay | `quay.io/company/payment-service` | `quay.io/company/payment-service/dev` |
| Image | Docker Hub | `docker.io/company/payment-service` | `docker.io/company/payment-service-dev` |
| Chart | GitLab (primary) | `oci://${CI_REGISTRY_IMAGE}/helm` | `oci://${CI_REGISTRY_IMAGE}/helm/dev` |
| Chart | Docker Hub | `oci://docker.io/company` | the same repository |

To make the customer environment pull from Docker Hub, set environment-scoped variables on
that environment:

```yaml
DEPLOY_IMAGE_REPOSITORY: docker.io/company/payment-service
DEPLOY_CHART_REPOSITORY: docker.io/company
```

The project's own registry needs no entry in `REGISTRY_CONFIG`: the job token is added for it.
See [Registries](../configuration.md#registries) for the rules.

[Documentation index](../../README.md)
