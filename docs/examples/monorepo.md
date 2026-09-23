# 7. Monorepo with Triggered Child Pipelines

**Root `.gitlab-ci.yml`:**

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/mono/.gitlab-ci.yml'

backend:
  stage: trigger
  trigger:
    include: "backend/.gitlab-ci.yml"
    strategy: depend
    forward:
      yaml_variables: true
      pipeline_variables: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
      when: manual
    - if: '$CI_PIPELINE_SOURCE != "web"'
      changes:
        - backend/**/*

frontend:
  stage: trigger
  trigger:
    include: "frontend/.gitlab-ci.yml"
    strategy: depend
    forward:
      yaml_variables: true
      pipeline_variables: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
      when: manual
    - if: '$CI_PIPELINE_SOURCE != "web"'
      changes:
        - frontend/**/*
```

**`backend/.gitlab-ci.yml` (Child pipeline):**

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.mono.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'

variables:
  PROJECT_CACHE_KEY: myapp-backend
  IMAGE_REPOSITORY: myteam/myapp-backend
  PROJECT_PATH: ./backend

Project:Version:Init:
  extends: .Node:Project:Version:Init

Node:Dependency:Download:
  extends:
    - .Node:24
    - .Node:Dependency:Download

Project:Build:
  extends:
    - .Node:24
    - .Node:Build
  script:
    - npm ci --include=dev --offline
    - npm run build

Project:Unit:Test:
  extends:
    - .Node:24
    - .Node:Test:Unit
  script:
    - npm ci --offline
    - npm test
```

[Documentation index](../../README.md)
