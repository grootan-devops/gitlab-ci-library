# 4. Java / Spring Boot Microservice

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: java
  IMAGE_REPOSITORY: myorg/payment-service
  CHART_REPOSITORY: myorg/helm

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/java/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'

Project:Version:Init:
  extends: .Java:Project:Version:Init

Java:Dependency:Download:
  extends:
    - .Java:25
    - .Java:Dependency:Download

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

`Project:Build` can instead extend the library template, which runs `mvn clean install`:

```yaml
Project:Build:
  extends:
    - .Java:25
    - .Java:Build
```

[Documentation index](../../README.md)
