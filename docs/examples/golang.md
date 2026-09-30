# 3. Golang Service / Binary Distribution

```yaml
# .gitlab-ci.yml
variables:
  BINARY_NAME: auth-service
  PROJECT_CACHE_KEY: go
  IMAGE_REPOSITORY: myorg/auth
  CHART_REPOSITORY: myorg/helm
  ADDITIONAL_RELEASE_ARTIFACT: ${BINARY_NAME}

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/golang/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'

Project:Build:
  extends: .Go
  variables:
    GOFLAGS: -mod=readonly
    GOPROXY: "off"
  script:
    - go build -trimpath -ldflags "-s -w -X 'main.Version=${TAG}'" -o ${BINARY_NAME} ./cmd/server
  artifacts:
    name: Binary
    paths:
      - ${PROJECT_PATH}/${BINARY_NAME}

Project:Unit:Test:
  extends: .Go:Test:Unit
  script:
    - go test ./... -v -json | go-junit-report > ${TEST_REPORT_DIR}/junit.xml
```

[Documentation index](../../README.md)
