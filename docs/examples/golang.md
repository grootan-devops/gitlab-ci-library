# 3. Golang Service / Binary Distribution

```yaml
# .gitlab-ci.yml
variables:
  RELEASE_VERSION: 1.0.0
  BINARY_NAME: auth-service
  PROJECT_CACHE_KEY: go
  IMAGE_REPOSITORY: myorg/auth
  CHART_REPOSITORY: myorg/helm

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
    - !reference [.release-packages-publish-rc, script]
  artifacts:
    name: Binary
    paths:
      - ${PROJECT_PATH}/${BINARY_NAME}
      - .release/package-metadata-${CI_JOB_ID}.json

Project:Unit:Test:
  extends: .Go:Test:Unit
  script:
    - go test ./... -v -json | go-junit-report > ${TEST_REPORT_DIR}/junit.xml
```

[Documentation index](../../README.md)
