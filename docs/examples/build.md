# 9. Standalone Build & Unit Test Verification (`WORKFLOW: build`)

Fast verification pipeline for rapid developer testing without container image builds or Helm packaging:

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: myapp-build-test

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/nodejs/.gitlab-ci.yml'

Project:Version:Init:
  extends: .Node:Project:Version:Init

Dependency:Download:
  extends:
    - .Node:24
    - Dependency:Download

Project:Build:
  extends:
    - .Node:24
    - .Node:Build
  script:
    - npm ci --include=dev --offline --no-audit --no-fund
    - npm run build

Project:Unit:Test:
  extends:
    - .Node:24
    - .Node:Test:Unit
  script:
    - npm ci --offline --no-audit --no-fund
    - npm test
```

> **Trigger via GitLab UI / API / Rules**:
>
> - Manual Web Dispatch: Set variable `WORKFLOW = "build"`
> - **Executed Stages & Jobs**:
>   1. `.pre`: `Project:Version:Init`
>   2. `init`: `Common:Init`
>   3. `prepare`: `Node:Dependency:Download`
>   4. `build`: `Project:Build`
>   5. `test`: `Project:Unit:Test`

[Documentation index](../../README.md)
