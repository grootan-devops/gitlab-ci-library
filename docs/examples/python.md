# 2. Python FastAPI / Service (App + Docker + Helm)

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: python
  IMAGE_REPOSITORY: myorg/api-service
  CHART_REPOSITORY: myorg/helm

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/python/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'

Project:Version:Init:
  extends: .Python:Project:Version:Init

Python:Dependency:Download:
  extends:
    - .Python:12
    - .Python:Dependency:Download

Project:Unit:Test:
  extends:
    - .Python:12
    - .Python:Test:Unit
  script:
    - uv sync --frozen --offline --no-install-project
    - mkdir -p ${TEST_REPORT_DIR}
    - uv run --no-sync pytest --junitxml=${TEST_REPORT_DIR}/junit.xml --cov=app

Image:Build:
  cache:
    key: ${PROJECT_CACHE_KEY}
    when: always
    policy: pull
    paths:
      - ${PROJECT_PATH}/.uv/
  before_script:
    - mkdir -p ${PROJECT_PATH}/.uv
```

> **Note on Python microservices:** Python runs from its application source and does not need a `Project:Build` job. The Dockerfile installs production dependencies offline using the `.uv` cache warmed by `Python:Dependency:Download` and restored by `Image:Build`.

```dockerfile
ARG PYTHON_312_MICRO_BASE_IMAGE

FROM ${PYTHON_312_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN --mount=type=bind,source=.uv,target=/tmp/.uv,rw \
    uv sync --frozen --no-dev --no-install-project --no-install-workspace --offline --cache-dir /tmp/.uv && \
    chown -R 10001:10001 /app

COPY --chown=10001:10001 app/ /app/app/
COPY --chown=10001:10001 main.py config.py /app/

USER 10001:10001
EXPOSE 3000

CMD ["python", "main.py"]
```

```dockerignore
# .dockerignore (Inverted Allowlist)
**
*

# Dependency manifests
!pyproject.toml
!uv.lock

# CI cache for BuildKit bind mount
!.uv
!.uv/**

# Application source code and runtime entry files
!app
!app/**
!main.py
!config.py
```

[Documentation index](../../README.md)
