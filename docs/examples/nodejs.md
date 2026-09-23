# 1. Node.js Full Stack (App + Docker + Helm + Multi-Env GitOps Deploy)

```yaml
# .gitlab-ci.yml
variables:
  IMAGE_REPOSITORY: "myorg/web-app"
  CHART_REPOSITORY: "myorg/helm"
  PROJECT_CACHE_KEY: "myorg-website-backend"

  DEPLOY_TARGET:
    value: "komodo-staging"
    options:
      - "komodo-dev"
      - "komodo-staging"
      - "komodo-production"
      - "argocd-dev"
      - "argocd-staging"
      - "argocd-production"
    description: "Target platform and environment when running the 'deploy' workflow."

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'

  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/deploy/gitops/.komodo.gitlab-ci.yml'
    inputs:
      environment: dev
      gitops_repo_url: https://gitlab.contoso.com/devops/gitops/komodo.git
      gitops_branch: environments/dev
      gitops_compose_file: app/docker-compose.yml
      gitops_service_image_yq_path: .services.web.image
      komodo_stack_name: web-app-dev

  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/deploy/gitops/.komodo.gitlab-ci.yml'
    inputs:
      environment: staging
      gitops_repo_url: https://gitlab.contoso.com/devops/gitops/komodo.git
      gitops_branch: environments/staging
      gitops_compose_file: app/docker-compose.yml
      gitops_service_image_yq_path: .services.web.image
      komodo_stack_name: web-app-staging

  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/deploy/gitops/.argocd.gitlab-ci.yml'
    inputs:
      environment: production
      gitops_repo_url: https://gitlab.contoso.com/devops/gitops/website-gitops.git
      gitops_branch: myapp/prod
      gitops_chart_values_file: values.yaml
      gitops_chart_app_yq_path: .apps.web
      argocd_apps: web-app-production

Project:Version:Init:
  extends: .Node:Project:Version:Init

Node:Dependency:Download:
  extends:
    - .Node:24
    - Dependency:Download

Project:Build:
  extends:
    - .Node:24
    - .Node:Build
  script:
    - npm ci --include=dev --offline --no-audit --no-fund
    - npx tsc --noEmit
    - npm run build
  artifacts:
    name: Strapi Build
    expose_as: Strapi Build
    expire_in: 1 week
    when: always
    paths:
      - dist/
      - .strapi/

Project:Unit:Test:
  extends:
    - .Node:24
    - .Node:Test:Unit
  coverage: '/All files[^|]*\|[^|]*\s+([\d.]+)/'
  script:
    - mkdir -p ${TEST_REPORT_DIR}
    - npm ci --include=dev --offline --no-audit --no-fund
    - npx vitest run --reporter=default --reporter=junit --outputFile=${TEST_REPORT_DIR}/junit.xml --coverage

Image:Build:
  cache:
    key:
      files:
        - package-lock.json
      prefix: ${PROJECT_CACHE_KEY}
    policy: pull
    paths:
      - .npm/
```

[Documentation index](../../README.md)
