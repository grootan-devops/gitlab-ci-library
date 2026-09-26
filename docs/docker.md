# Dockerfile standards

## Dockerfile Standards & Multi-Stack Reference (Packaging-Only & Non-Root 10001:10001)

Every container image built by this platform adheres strictly to the **Packaging-Only Standard** and **Non-Root Runtime Enforcement**:

1. **Packaging-Only Standard (Zero Compilation in Dockerfile)**:
   - All compiling, bundling, transpile steps (`npm run build`, `mvn package`, `go build`, `uv build`), linting, and tests **MUST** execute strictly in GitLab CI stages (`prepare`, `build`, `test`).
   - The `Dockerfile` serves purely as an artifact packaging manifest. It copies pre-built artifacts emitted by `Project:Build`.
   - Where an interpreted stack must install dependencies, it installs **offline** from the CI package cache, bind-mounted by BuildKit — never resolving over the network, which would re-resolve what the pipeline already pinned and scanned. The `--mount` source must name the directory the pipeline actually cached (`.uv`, `.npm`), and `.dockerignore` must admit it.
2. **Non-Root User & Group (10001:10001)**:
   - For security compliance, containers must never execute as `root` (UID `0`).
   - Every Dockerfile declares `USER 10001:10001`.
   - All copied application files and artifacts must be owned by the non-root user using `COPY --chown=10001:10001 ...`.
   - If the application writes logs, cache, or PID files at runtime, ensure the target directories exist and are owned by `10001:10001` before the `USER` directive.
   - Non-privileged listening port: standard application port is `EXPOSE 8080`.
3. **Automatic CI Build-Arg Base Images**:
   The `image/.docker.gitlab-ci.yml` builder automatically resolves and injects the following build-args into `docker build`. A Dockerfile pins nothing itself — bumping a base image is a change to one CI/CD variable pair in `common/.gitlab-ci.yml`.

| Tech Stack | Injected CI Build-Arg | Variable pair | Current default |
| --- | --- | --- | --- |
| **Java** | `JAVA_25_MICRO_BASE_IMAGE` | `JAVA_25_MICRO_BASE_IMAGE_REPO` / `_TAG` | `grootantech/micro-java-25:1.1.1` |
| **Golang** | `MICRO_ROOT_BASE_IMAGE` | `MICRO_ROOT_BASE_IMAGE_REPO` / `_TAG` | `grootantech/micro-root:1.1.0` |
| **Python** | `PYTHON_312_MICRO_BASE_IMAGE` | `PYTHON_312_MICRO_BASE_IMAGE_REPO` / `_TAG` | `grootantech/micro-python-3-12:1.1.1` |
| **Node.js Backend** | `NODE_JS_24_MICRO_BASE_IMAGE` | `NODE_JS_24_MICRO_BASE_IMAGE_REPO` / `_TAG` | `grootantech/micro-node-24:1.1.1` |
| **Node.js Frontend** | `NGINX_MICRO_BASE_IMAGE` | `NGINX_MICRO_BASE_IMAGE_REPO` / `_TAG` | `grootantech/micro-nginx:1.1.1` |
| **Multi-stage builder** | `TOOLKIT_BUILD_IMAGE` | `TOOLKIT_BUILD_IMAGE_REPO` / `_TAG` | `grootantech/toolkit:1.1.0` |
| **All** | `VERSION` | — | `${APP_PUSH_VERSION}` |

   GitLab additionally injects `CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX` (with a trailing `/`), so a public base image is written `FROM ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}redhat/ubi9-minimal:${TAG}` with no separator. **GitHub has no Dependency Proxy and injects no equivalent** — a Dockerfile shared between the two platforms must give that ARG a default.

1. **Base image selection**:
   Use the runtime image matching the project language; fall back to `MICRO_ROOT_BASE_IMAGE` when no language image fits. **A runtime stage is never built `FROM` a build image.** A `*_BUILD_IMAGE` carries compilers, package managers and credential helpers, all of which would ship to production — it belongs in a builder stage only.

2. **Tags are pinned, never floating**:
   No `:latest`, and no untagged reference. A literal image carries an explicit tag with a `# renovate:` annotation on the line above so the bot can bump it. A `FROM ${VAR}` reference needs no tag: CI resolves it from the variable pair above.

3. **Runtime instructions**:
   - `EXPOSE` is required on a service image. It is the image's only self-describing contract, and the chart's `containerPort` is unverifiable without it.
   - **Prefer `CMD`.** It states the default command while leaving an operator free to override it with `docker run <image> <cmd>`.
   - Use `ENTRYPOINT` only to invoke a pre-start shim — a script that must substitute configuration before the service starts. If that shim `exec`s the service as its last action it becomes PID 1 and needs nothing further. If it forks, or leaves children running, `exec` through `dumb-init` so signals and zombie reaping work: `exec /usr/bin/dumb-init -- nginx -g "daemon off;"`.

4. **Layout: the `USER` bracket, grouping and layers**:
   - `USER 0` immediately after the runtime stage's `FROM`, opening the root setup phase. `USER 10001:10001` closes it, before the runtime instructions. A builder stage is discarded and needs no `USER 0` — declaring one there trips hadolint `DL3002` ("last USER should not be root"), which is evaluated per stage and gates `Docker:Lint`.
   - Group by instruction kind and separate groups with one blank line. Instructions that form a single unit — a run of `COPY`s, one install-and-chown `RUN` — stay together with no blank line between them, under one comment saying what the group is for.
   - **Merge consecutive `RUN`s.** Each one is a layer, and a layer keeps whatever the previous one left behind. Chain with `&& \` instead.
   - Group related `ARG`s into one continued statement. The exception is a version pin: an `ARG` carrying a `# renovate:` annotation stays on its own line, because the annotation binds to the line below it.
   - Copy source **after** the dependency install, never before, or every source edit invalidates the dependency layer.

---

### 1. Java / Spring Boot Microservice

- **Base Image**: `${JAVA_25_MICRO_BASE_IMAGE}`
- **Build Artifacts Copied**: Pre-built executable fat JAR from `target/*.jar` (Maven) or `build/libs/*.jar` (Gradle).
- **File Ownership & Permissions**: `COPY --chown=10001:10001 target/*.jar /app/app.jar`
- **JVM Container Options**: Configured with `-XX:+UseContainerSupport` and `-XX:MaxRAMPercentage=75.0` for dynamic cgroup memory limits.

```dockerfile
ARG JAVA_25_MICRO_BASE_IMAGE
FROM ${JAVA_25_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app

# Copy pre-compiled executable JAR from CI Project:Build stage with non-root ownership
COPY --chown=10001:10001 target/*.jar /app/app.jar

USER 10001:10001
EXPOSE 8080

CMD ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "/app/app.jar"]
```

```dockerignore
# .dockerignore (Inverted Allowlist)
**
*

!target/*.jar
!build/libs/*.jar
```

---

### 2. Golang Microservice (Static Binary)

- **Base Image**: `${MICRO_ROOT_BASE_IMAGE}` (distroless minimal root container).
- **Build Artifacts Copied**: Statically compiled binary built in CI (`CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/api-service .`).
- **File Ownership & Permissions**: `COPY --chown=10001:10001 bin/api-service /app/api-service`
- **Executable Permissions**: `chmod +x` is set during `Project:Build` stage before packaging.

```dockerfile
ARG MICRO_ROOT_BASE_IMAGE
FROM ${MICRO_ROOT_BASE_IMAGE}

USER 0

WORKDIR /app

# Copy statically linked binary from CI Project:Build stage with non-root ownership
COPY --chown=10001:10001 bin/api-service /app/api-service

USER 10001:10001
EXPOSE 8080

CMD ["/app/api-service"]
```

```dockerignore
# .dockerignore (Inverted Allowlist)
**
*

!bin/
!bin/*
```

---

### 3. Python Microservice (FastAPI / Flask / Worker with `uv`)

- **Base Image**: `${PYTHON_312_MICRO_BASE_IMAGE}`
- **CI/runtime image distinction**: `Python:Dependency:Download` uses the Python 3.12 CI build image through `.Python:12`; the Dockerfile uses `${PYTHON_312_MICRO_BASE_IMAGE}` as the production runtime.
- **Storage Strategy**: **Cache-only with a BuildKit bind mount** — no dependency artifacts are uploaded. `Python:Dependency:Download` warms `.uv`, and `Image:Build` restores the same cache key/path for the Docker build. Containerized Python services do not need `Project:Build` unless they separately produce a build artifact.
- **BuildKit Bind Mount**: The `.uv` cache folder is mounted read-write temporarily via `--mount=type=bind,source=.uv,target=/tmp/.uv,rw`. It is **never copied** into the image filesystem, ensuring zero layer bloat.
- **Environment**: `ENV PATH="/app/.venv/bin:$PATH"` (`PYTHONUNBUFFERED=1` is pre-configured in the base image).
- **File Ownership & Permissions**: `COPY --chown=10001:10001 ...` and `chown -R 10001:10001 /app`
- **Zero Internet Access**: `uv sync` installs strictly offline from the mounted `/tmp/.uv` in milliseconds.

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

---

### 4. Node.js Backend (NestJS, Strapi, Express)

- **Base Image**: `${NODE_JS_24_MICRO_BASE_IMAGE}`
- **Build Artifacts Copied**: Pre-compiled TypeScript output (`dist/`) and `package*.json`. Production dependencies are installed **offline in the image** from the `.npm` cache `Node:Dependency:Download` warmed — `node_modules/` is cached, never artifacted.
- **File Ownership & Permissions**: `COPY --chown=10001:10001 ...`
- **Runtime Environment**: `ENV NODE_ENV=production PORT=8080`

```dockerfile
ARG NODE_JS_24_MICRO_BASE_IMAGE
FROM ${NODE_JS_24_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080

# Copy locked dependency manifests
COPY --chown=10001:10001 package*.json /app/

# Mount the pre-warmed CI cache via Buildx, install production dependencies offline,
# and set ownership
RUN --mount=type=bind,source=.npm,target=/tmp/.npm,rw \
    npm ci --omit=dev --offline --no-audit --no-fund --cache /tmp/.npm && \
    chown -R 10001:10001 /app

# Copy pre-compiled dist/ with non-root ownership
COPY --chown=10001:10001 dist/ /app/dist/

USER 10001:10001
EXPOSE 8080

CMD ["node", "dist/main.js"]
```

```dockerignore
# .dockerignore (Inverted Allowlist)
**
*

!package*.json
!.npm
!.npm/**
!dist/
!dist/**
```

---

### 5. Node.js Frontend SPA (React, Vue, Angular, Vite with Nginx)

- **Base Image**: `${NGINX_MICRO_BASE_IMAGE}`
- **Build Artifacts Copied**:
  1. Static HTML/JS/CSS distribution bundle: `dist/` or `build/`
  2. SPA reverse proxy configuration: `nginx.conf`
- **Nginx Non-Root Operation**:
  - `micro-nginx` base image is pre-configured for unprivileged non-root operation:
    - Listens on non-root port `8080`.
    - PID stored in `/tmp/nginx.pid`.
    - Temporary cache paths pre-configured in `/tmp/client_temp`, `/tmp/proxy_temp`.
    - Client-side router support via `try_files $uri $uri/ /index.html;`.
- **File Ownership & Permissions**: `COPY --chown=10001:10001 ...`

```dockerfile
ARG NGINX_MICRO_BASE_IMAGE
FROM ${NGINX_MICRO_BASE_IMAGE}

USER 0

# Copy pre-compiled static distribution and SPA nginx configuration with non-root ownership
COPY --chown=10001:10001 dist/ /usr/share/nginx/html/
COPY --chown=10001:10001 nginx.conf /etc/nginx/conf.d/default.conf

USER 10001:10001
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

```dockerignore
# .dockerignore (Inverted Allowlist)
**
*

!dist/
!dist/**
!build/
!build/**
!nginx.conf
```

---

### 6. Multi-Stage (only when the pipeline cannot produce the artifact)

Most images need no builder stage: `Project:Build` produces the artifact and the Dockerfile
copies it. Where a builder stage is genuinely needed, it uses `${TOOLKIT_BUILD_IMAGE}` and
the runtime stage copies out of it — the runtime stage itself is always a micro base image.

- **Builder Stage**: `${TOOLKIT_BUILD_IMAGE}`, discarded after the build. No `USER 0` here — hadolint `DL3002` is evaluated per stage.
- **Runtime Stage**: the language micro base image, or `${MICRO_ROOT_BASE_IMAGE}` as fallback.
- **File Ownership & Permissions**: `COPY --from=builder --chown=10001:10001 ...`

```dockerfile
ARG TOOLKIT_BUILD_IMAGE \
    MICRO_ROOT_BASE_IMAGE

FROM ${TOOLKIT_BUILD_IMAGE} AS builder

WORKDIR /src

COPY . .

RUN make build

FROM ${MICRO_ROOT_BASE_IMAGE}

USER 0

WORKDIR /app

# Copy only the built artifact out of the builder stage
COPY --from=builder --chown=10001:10001 /src/bin/app /app/app

USER 10001:10001

EXPOSE 8080

CMD ["/app/app"]
```

---

## The Inverted `.dockerignore` Allowlist Standard (Default Deny)

To enforce strict packaging hygiene, minimize Docker build context transfer to under 100 KB, and guarantee that zero sensitive local files (`.git/`, `.env`, secrets, test caches, local virtual environments) leak into image builds, all projects must employ an **Inverted Allowlist `.dockerignore`**:

1. **Default Deny**: Block everything recursively by placing `**` and `*` at the top of the file.
2. **Explicit Allowlist (`!`)**: Strictly unignore only the exact files, build output, or manifests required by that specific stack's `Dockerfile`.

### Stack-by-Stack `.dockerignore` Reference

| Tech Stack | Allowlisted Packaging Targets | Sample `.dockerignore` |
| --- | --- | --- |
| **Python** (`uv` + `src/` layout) | `pyproject.toml`, `uv.lock`, `.uv/`, `src/` | `**`, `*`, `!pyproject.toml`, `!uv.lock`, `!.uv`, `!.uv/**`, `!src`, `!src/**` |
| **Java** (Spring Boot Fat JAR) | Maven (`target/*.jar`) or Gradle (`build/libs/*.jar`) | `**`, `*`, `!target/*.jar`, `!build/libs/*.jar` |
| **Golang** (Static Binary) | Pre-compiled binary (`bin/`) | `**`, `*`, `!bin/`, `!bin/*` |
| **Node.js Frontend** (Nginx SPA) | Static bundle (`dist/`), `nginx.conf` | `**`, `*`, `!dist/`, `!dist/**`, `!nginx.conf` |
| **Node.js Backend** (Express / NestJS) | `dist/`, `.npm` cache, `package*.json` | `**`, `*`, `!dist/`, `!dist/**`, `!package.json`, `!package-lock.json`, `!.npm`, `!.npm/**` |

[Documentation index](../README.md)
