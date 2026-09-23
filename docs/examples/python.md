# 2. Python FastAPI / Service (App + Docker + Helm)

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: myapp-python
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
    - uv run --no-sync pytest --junitxml=${TEST_REPORT_DIR}/junit.xml --cov=src

Image:Build:
  cache:
    key: ${PROJECT_CACHE_KEY}
    policy: pull
    paths:
      - ${PROJECT_PATH}/.uv/
  before_script:
    - mkdir -p ${PROJECT_PATH}/.uv
```

> **Note on Python Microservices:** Unlike compiled languages (Go binaries, Java JARs, Node dist), containerized Python services run directly against interpreted `src/`. Dependency virtualenvs are installed offline during Docker build by mounting the `.uv` cache via BuildKit (`--mount=type=bind,source=.uv,target=/tmp/.uv`). Consequently, containerized Python services omit `Project:Build` and do not generate or artifact unused `dist/` packages.

```dockerfile
# Dockerfile (Packaging-Only - Pattern A Cache-Only with BuildKit Bind Mount)
ARG PYTHON_312_MICRO_BASE_IMAGE
FROM ${PYTHON_312_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# Copy locked dependency manifests
COPY pyproject.toml uv.lock ./

# Mount pre-warmed CI cache via Buildx, install production dependencies offline, set ownership
RUN --mount=type=bind,source=.uv,target=/tmp/.uv \
    uv sync --frozen --no-dev --no-install-project --no-install-workspace --offline --cache-dir /tmp/.uv && \
    chown -R 10001:10001 /app

# Copy application source code with non-root ownership
COPY --chown=10001:10001 src/ /app/src/

USER 10001:10001
EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
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

# Application source code
!src
!src/**
```

[Documentation index](../../README.md)
