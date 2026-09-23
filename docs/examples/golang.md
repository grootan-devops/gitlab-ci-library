# 3. Golang Service / Binary Distribution

```yaml
# .gitlab-ci.yml
variables:
  BINARY_NAME: auth-service
  PROJECT_CACHE_KEY: auth-service-go
  IMAGE_REPOSITORY: myorg/auth
  CHART_REPOSITORY: myorg/helm
  ADDITIONAL_RELEASE_ARTIFACT: ${BINARY_NAME}

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/golang/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'

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
