# 10. Standalone Release Prerequisites & Conflict Check (`WORKFLOW: check`)

Pre-flight dry-run guard to verify release availability, tag uniqueness, container image/chart conflicts, README documentation sync, and dependency rules before merging code:

```yaml
# .gitlab-ci.yml
variables:
  IMAGE_REPOSITORY: myorg/web-app
  CHART_REPOSITORY: myorg/helm

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'

Project:Version:Init:
  extends: .Node:Project:Version:Init
```

> **Trigger via GitLab UI / API / Rules**:
>
> - Manual Web Dispatch: Set variable `WORKFLOW = "check"`
> - **Executed Stages & Jobs**:
>   1. `.pre`: `Project:Version:Init`
>   2. `init`: `Common:Init`
>   3. `check`:
>      - `Tag:Tag Existence` (queries git repository for tag collision)
>      - `Image:Check Existence` (asserts remote image tag is available)
>      - `Chart:Check Existence` (asserts availability in configured OCI, or GitLab packages when `CHART_REGISTRY` is empty)
>      - `Chart:Check:README` (verifies committed README.md matches helm-docs)
>      - `Chart:Check:Dependency` (ensures no dev registry dependencies exist)
>      - `Changelog:Lint` (verifies CHANGELOG.md contains release notes)
>      - `Migration:Check Existence` (strictly enforces migration guide for breaking major releases)

[Documentation index](../../README.md)
