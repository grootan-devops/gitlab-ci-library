# 5. Pure Helm Chart Repository

For repositories containing only Helm charts (no application code or Dockerfile), `Chart.yaml`
is the version source. Leave `CHART_REGISTRY` unset or empty for this project's GitLab Helm
Package Registry. For OCI, configure the registry, repository and chart-specific credentials
from the [configuration guide](../configuration.md#helm-chart-publishing--authentication).
Dependency-only authentication has separate settings; it must not select the publishing backend.

```yaml
# .gitlab-ci.yml
variables:
  CHART_DIR: .

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'
```

[Documentation index](../../README.md)
