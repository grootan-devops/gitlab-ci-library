# 4. Java / Spring Boot Microservice

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: payment-java
  IMAGE_REPOSITORY: myorg/payment-service
  CHART_REPOSITORY: myorg/helm

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/java/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'

Project:Version:Init:
  extends: .Java:Project:Version:Init

Java:Dependency:Download:
  extends:
    - .Java:25
    - Dependency:Download

Project:Build:
  extends:
    - .Java:25
  stage: build
  cache:
    policy: pull
  script:
    - mvn -o clean package -DskipTests
  artifacts:
    name: JAR
    paths:
      - target/*.jar

Project:Unit:Test:
  extends:
    - .Java:Test:Unit
    - .Java:25
  script:
    - mvn test
```

[Documentation index](../../README.md)
