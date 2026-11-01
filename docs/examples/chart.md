# 5. Pure Helm Chart Repository

For repositories containing only Helm charts (no application code or Dockerfile), `Chart.yaml`
is the version source. With nothing configured the chart goes to
`oci://${CI_REGISTRY_IMAGE}/helm` (candidates in `/helm/dev`) with the job token. Another
registry, or several, are configured as in [Registries](../configuration.md#registries).

```yaml
# .gitlab-ci.yml
variables:
  CHART_DIR: .

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'
```

[Documentation index](../../README.md)
