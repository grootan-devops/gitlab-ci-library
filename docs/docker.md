# Dockerfile standards

## Dockerfile Standards & Multi-Stack Reference (Packaging-Only & Non-Root 10001:10001)

Every container image built by this platform adheres strictly to the **Packaging-Only Standard** and **Non-Root Runtime Enforcement**:

1. **Packaging-Only Standard (Zero Compilation in Dockerfile)**:
   - All compiling, bundling, transpile steps (`npm run build`, `mvn package`, `go build`, `uv build`), linting, and tests **MUST** execute strictly in GitLab CI stages (`prepare`, `build`, `test`).
   - The `Dockerfile` serves purely as an artifact packaging manifest. It copies pre-built artifacts emitted by `Project:Build`.
   - Where an interpreted stack must install dependencies, it installs **offline** from the CI package cache, bind-mounted by BuildKit — never resolving over the network, which would re-resolve what the pipeline already pinned and scanned. The `--mount` source must name the directory the pipeline actually cached (`.uv`, `.npm`), and `.dockerignore` must admit it.
   - The cache is the handoff, never an artifact: `Image:Build` restores the runner cache into its workspace with the same `PROJECT_CACHE_KEY` as the dependency-download job, and the Dockerfile bind-mounts it. `--offline` is what stops a silent fall-through to the network; the mount is never `COPY`d, so it adds no layer. `node_modules/`, `.venv/` and `vendor/` are never published as artifacts — only real build output (`dist/`, a jar, a binary) is.

     ```yaml
     Image:Build:
       cache:
         key: ${PROJECT_CACHE_KEY}
         when: always
         policy: pull
         paths:
           - .npm/
     ```

   - **Never `ARG` a secret.** Build arguments persist in the image history even when a later layer deletes the file (`ARG NPM_TOKEN`, a `PIP_INDEX_URL` with credentials). Use a BuildKit secret mount (`--mount=type=secret`) when a build genuinely needs one.
2. **Non-Root User & Group (10001:10001)**:
   - For security compliance, containers must never execute as `root` (UID `0`).
   - Every Dockerfile declares `USER 10001:10001`.
   - All copied application files and artifacts must be owned by the non-root user using `COPY --chown=10001:10001 ...`.
   - Paths the application writes at runtime — a cache, a lock or a PID file — are chart mounts, not directories chowned in the image: an `emptyDir` for scratch data, `persistence` for data that must survive a restart (see the helm-tpl-library configuration guide). The image owns only what it ships.
   - Non-privileged listening port: standard application port is `EXPOSE 8080`.
3. **Automatic CI Build-Arg Base Images**:
   The `image/.docker.gitlab-ci.yml` builder automatically resolves and injects the following build-args into `docker build`. A Dockerfile pins nothing itself — bumping a base image is a change to one CI/CD variable pair in `common/.gitlab-ci.yml`, which also holds each pair's default repository and tag.

   | Tech Stack | Injected CI Build-Arg | Variable pair |
   | --- | --- | --- |
   | **Java** | `JAVA_25_MICRO_BASE_IMAGE` | `JAVA_25_MICRO_BASE_IMAGE_REPO` / `_TAG` |
   | **Golang** | `MICRO_ROOT_BASE_IMAGE` | `MICRO_ROOT_BASE_IMAGE_REPO` / `_TAG` |
   | **Python** | `PYTHON_312_MICRO_BASE_IMAGE` | `PYTHON_312_MICRO_BASE_IMAGE_REPO` / `_TAG` |
   | **Node.js Backend** | `NODE_JS_24_MICRO_BASE_IMAGE` | `NODE_JS_24_MICRO_BASE_IMAGE_REPO` / `_TAG` |
   | **Node.js Frontend** | `NGINX_MICRO_BASE_IMAGE` | `NGINX_MICRO_BASE_IMAGE_REPO` / `_TAG` |
   | **Multi-stage builder** | `TOOLKIT_BUILD_IMAGE` | `TOOLKIT_BUILD_IMAGE_REPO` / `_TAG` |
   | **All** | `VERSION` | `${APP_PUSH_VERSION}` |

   GitLab additionally injects `CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX` (with a trailing `/`), so a public base image is written `FROM ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}redhat/ubi9-minimal:${TAG}` with no separator. **GitHub has no Dependency Proxy and injects no equivalent** — a Dockerfile shared between the two platforms must give that ARG a default.

   Any other CI/CD variable named `DOCKER_BUILD_ARG_<NAME>` reaches the Docker builder as `--build-arg <NAME>=<value>` — the way a [project base image](#7-project-base-image-heavy-os-stack) reaches a Dockerfile. The Buildah builder takes no build arguments.

4. **Base image selection**:
   Use the runtime image matching the project language; fall back to `MICRO_ROOT_BASE_IMAGE` when no language image fits. **A runtime stage is never built `FROM` a build image.** A `*_BUILD_IMAGE` carries compilers, package managers and credential helpers, all of which would ship to production — it belongs in a builder stage only.

   The micro images are deliberately minimal: no package manager and no `ps`, `awk`, `tar` or `which`; `linux/amd64` only; UID `10001` has no passwd entry and `HOME=/`. Anything the application or its scripts call must already be in the image — check a native dependency inside the built image (`ldd` on the shared object) before shipping. When a micro image lacks a small, general library, fix that base image and bump its default tag in this library instead of working around it in each consumer; never graft packages into a micro image from a builder stage. A heavy OS stack gets a [project base image](#7-project-base-image-heavy-os-stack).

5. **Tags are pinned, never floating**:
   No `:latest`, and no untagged reference, on a literal `FROM`. A `FROM ${VAR}` reference takes its tag from CI; give its `ARG` the approved image at `:latest` as the default, so a plain local `docker build` works and nobody reaches for an unapproved public image, while CI overrides it with the exact pinned tag. Renovate bumps a literal `FROM` tag by itself; an image version held in an `ARG` needs a `# renovate:` annotation on the line above — for images from a **public** registry (Docker Hub, GCR, Amazon ECR Public, Quay) only. Images in a private registry need none.

6. **Runtime instructions**:
   - `EXPOSE` is required on a service image. It is the image's only self-describing contract, and the chart's `containerPort` is unverifiable without it.
   - **Prefer `CMD`.** It states the default command while leaving an operator free to override it with `docker run <image> <cmd>`.
   - **PID 1 is always an init.** The runtime stage declares `ENTRYPOINT ["/usr/bin/dumb-init", "--"]` and names the process in `CMD`, even when the base image already sets an ENTRYPOINT: a base's ENTRYPOINT is invisible in review, and a shell-form one silently drops `CMD`. A bare runtime as PID 1 installs no SIGTERM handler, so the pod is killed only when its grace period runs out, and it never reaps orphaned children; dumb-init forwards signals to the process group and reaps zombies.
   - **A start script is the `CMD`, never the ENTRYPOINT**, so `docker run <image> sh` still runs under dumb-init. Every branch ends with `exec`, so no shell stays between dumb-init and the service and the service's exit code is the container's, and an unknown mode exits non-zero. A multi-mode image picks its process from a `MODE` variable the chart sets. Where the process needs shell expansion, `CMD ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]` keeps the JVM a direct child of dumb-init. The chart leaves `command` and `args` empty (see the helm-tpl-library chart standards).

     ```sh
     #!/bin/sh
     set -e

     case "${MODE:-api}" in
       api) exec node dist/main.js ;;
       worker) exec node dist/worker.js ;;
       *) echo "invalid MODE: ${MODE}" >&2; exit 1 ;;
     esac
     ```

7. **Layout: the `USER` bracket, grouping and layers**:
   - `USER 0` immediately after the runtime stage's `FROM`, opening the root setup phase. `USER 10001:10001` closes it, before the runtime instructions. A builder stage is discarded and needs no `USER 0` — declaring one there trips hadolint `DL3002` ("last USER should not be root"), which is evaluated per stage and gates `Docker:Lint`.
   - Group by instruction kind and separate groups with one blank line. Instructions that form a single unit — a run of `COPY`s, one install-and-chown `RUN` — stay together with no blank line between them.
   - **Comments are one line saying why**, only where something differs from the default. No banners, and no comment restating the next instruction: keep `# local builds only; CI passes the pinned tag` above an `ARG` default, drop `# Copy application source code` above a `COPY`.
   - **Merge consecutive `RUN`s.** Each one is a layer, and a layer keeps whatever the previous one left behind. Chain with `&& \` instead.
   - **Clean in the layer that created the files**: a later `RUN rm` cannot shrink an earlier layer. In the `RUN` that installs, remove build-only tools, package lists and caches, `/var/log`, `/root/.cache`, `/var/tmp` and `/tmp`. Leave any path that `RUN` bind-mounts; deleting a mount source fails the build.
   - Group related `ARG`s into one continued statement. The exception is a version pin: an `ARG` carrying a `# renovate:` annotation stays on its own line, because the annotation binds to the line below it.
   - Copy source **after** the dependency install, never before, or every source edit invalidates the dependency layer.

---

### 1. Java / Spring Boot Microservice

- **Base Image**: `${JAVA_25_MICRO_BASE_IMAGE}`
- **Build Artifacts Copied**: Pre-built executable fat JAR from `target/*.jar` (Maven) or `build/libs/*.jar` (Gradle).
- **File Ownership & Permissions**: `COPY --chown=10001:10001 target/*.jar /app/app.jar`
- **JVM Container Options**: Configured with `-XX:+UseContainerSupport` and `-XX:MaxRAMPercentage=75.0` for dynamic cgroup memory limits.

```dockerfile
ARG JAVA_25_MICRO_BASE_IMAGE=grootantech/micro-java-25:latest
FROM ${JAVA_25_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app

COPY --chown=10001:10001 target/*.jar /app/app.jar

USER 10001:10001
EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
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
ARG MICRO_ROOT_BASE_IMAGE=grootantech/micro-root:latest
FROM ${MICRO_ROOT_BASE_IMAGE}

USER 0

WORKDIR /app

COPY --chown=10001:10001 bin/api-service /app/api-service

USER 10001:10001
EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
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
ARG PYTHON_312_MICRO_BASE_IMAGE=grootantech/micro-python-3-12:latest

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
EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
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
ARG NODE_JS_24_MICRO_BASE_IMAGE=grootantech/micro-node-24:latest
FROM ${NODE_JS_24_MICRO_BASE_IMAGE}

USER 0

WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080

COPY --chown=10001:10001 package*.json /app/

RUN --mount=type=bind,source=.npm,target=/tmp/.npm,rw \
    npm ci --omit=dev --offline --no-audit --no-fund --cache /tmp/.npm && \
    chown -R 10001:10001 /app

COPY --chown=10001:10001 dist/ /app/dist/

USER 10001:10001
EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
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
- **Build Artifacts Copied**: the static HTML/JS/CSS bundle, `dist/` or `build/`.
- **Server configuration**: the micro-nginx default below serves the SPA. A per-environment
  `default.conf` is a chart file mount, not a file copied into the image (see the
  helm-tpl-library configuration guide, *File mounts*).
- **Nginx Non-Root Operation**:
  - `micro-nginx` base image is pre-configured for unprivileged non-root operation:
    - Listens on non-root port `8080`.
    - PID stored in `/tmp/nginx.pid`.
    - Temporary cache paths pre-configured in `/tmp/client_temp`, `/tmp/proxy_temp`.
    - Client-side router support via `try_files $uri $uri/ /index.html;`.
- **File Ownership & Permissions**: `COPY --chown=10001:10001 ...`

```dockerfile
ARG NGINX_MICRO_BASE_IMAGE=grootantech/micro-nginx:latest
FROM ${NGINX_MICRO_BASE_IMAGE}

USER 0

COPY --chown=10001:10001 dist/ /usr/share/nginx/html/

USER 10001:10001
EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
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
    MICRO_ROOT_BASE_IMAGE=grootantech/micro-root:latest

FROM ${TOOLKIT_BUILD_IMAGE} AS builder

WORKDIR /src

COPY . .

RUN make build

FROM ${MICRO_ROOT_BASE_IMAGE}

USER 0

WORKDIR /app

COPY --from=builder --chown=10001:10001 /src/bin/app /app/app

USER 10001:10001

EXPOSE 8080

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/app/app"]
```

---

### 7. Project base image (heavy OS stack)

When the application needs a heavy OS layer — database client libraries, PDF or office
tooling, a headless browser — install it once in a project base image rather than in every
pipeline:

- `Dockerfile.base` starts from the public runtime image, installs the OS packages the
  application runs with and `dumb-init`, cleans in the same layer and ends `USER 10001:10001`.
- Build it for `linux/amd64` with `docker buildx build --platform linux/amd64 --push` — not
  `--load` and a separate push, which loses the platform manifest on another architecture —
  and tag it like its runtime (`3.12-slim`), so the pin says what is inside.
- Push the base before the first pipeline that uses it, and bump its tag whenever
  `Dockerfile.base` changes.
- The application Dockerfile has one stage: `ARG APP_BASE_IMAGE` with no default,
  `FROM ${APP_BASE_IMAGE}`, then the usual packaging. The pipeline passes the base:

```yaml
variables:
  DOCKER_BUILD_ARG_APP_BASE_IMAGE: "${CI_REGISTRY_IMAGE}/base:3.12-slim"
```

`Dockerfile.base`:

```dockerfile
ARG RUNTIME_IMAGE
FROM ${RUNTIME_IMAGE}

USER 0

# OS packages the micro base cannot provide (libpq5 here); list only what the app runs with
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates dumb-init libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /var/log/* /tmp/* /var/tmp/* /root/.cache

USER 10001:10001
```

A builder that pushes `<registry>/<project path>/base:<tag>` once. It needs the registry host
(it never guesses one), uses the Docker credentials already configured without changing the
Docker config, and skips a tag that already exists unless `FORCE=1`:

```bash
#!/usr/bin/env bash
# Builds Dockerfile.base once and pushes <registry>/<project path>/base:<tag>; CI builds the app FROM it.
# Usage: ./base-image-builder.sh <runtime-image:tag> [base-tag]
#   e.g. ./base-image-builder.sh python:3.12-slim        -> .../base:3.12-slim
# Env:   REGISTRY (defaults to $CI_REGISTRY), PROJECT_PATH (defaults to the git remote path),
#        PLATFORM (default linux/amd64), FORCE=1 rebuilds a tag that already exists.
set -euo pipefail

RUNTIME_IMAGE="${1:?usage: $0 <runtime-image:tag> [base-tag]}"
BASE_TAG="${2:-${RUNTIME_IMAGE##*:}}"
REGISTRY="${REGISTRY:-${CI_REGISTRY:-}}"
PROJECT_PATH="${PROJECT_PATH:-$(git remote get-url origin | sed -E 's#^(https?://[^/]+/|[^@]+@[^:]+:)##; s#\.git$##')}"
PLATFORM="${PLATFORM:-linux/amd64}"

if [ -z "${REGISTRY}" ]; then
  echo "Set REGISTRY to the project's container registry host (ask if unsure)." >&2
  exit 1
fi
IMAGE="${REGISTRY}/${PROJECT_PATH}/base:${BASE_TAG}"

cd "$(dirname "$0")"

if ! python3 - "${REGISTRY}" <<'PY'
import json, os, sys
try:
    cfg = json.load(open(os.path.expanduser("~/.docker/config.json")))
except (OSError, ValueError):
    sys.exit(1)
reg = sys.argv[1]
sys.exit(0 if reg in cfg.get("credHelpers", {}) or reg in cfg.get("auths", {}) else 1)
PY
then
  echo "No Docker credentials for ${REGISTRY}. Log in first (docker login ${REGISTRY}); this script never changes your Docker config." >&2
  exit 1
fi

if [ "${FORCE:-0}" != "1" ] && docker manifest inspect "${IMAGE}" >/dev/null 2>&1; then
  echo ">> ${IMAGE} already exists; bump the tag when Dockerfile.base changes, or set FORCE=1"
  exit 0
fi

echo ">> Building and pushing ${IMAGE} (${PLATFORM})"
docker buildx build \
  --platform "${PLATFORM}" \
  --file Dockerfile.base \
  --build-arg "RUNTIME_IMAGE=${RUNTIME_IMAGE}" \
  --tag "${IMAGE}" \
  --push \
  .
echo ">> Pushed ${IMAGE}. Pass it to the app build as DOCKER_BUILD_ARG_<APP>_BASE_IMAGE."
```

---

## The Inverted `.dockerignore` Allowlist Standard (Default Deny)

To enforce strict packaging hygiene, minimize Docker build context transfer to under 100 KB, and guarantee that zero sensitive local files (`.git/`, `.env`, secrets, test caches, local virtual environments) leak into image builds, all projects must employ an **Inverted Allowlist `.dockerignore`**:

1. **Default Deny**: Block everything recursively by placing `**` and `*` at the top of the file, in that order, as the first two lines.
2. **Explicit Allowlist (`!`)**: Strictly unignore only the exact files, build output, or manifests required by that specific stack's `Dockerfile`.
3. **Anchor root-only patterns without a leading slash.** `!*.js` admits root modules and does not cross `/`; a leading `/` is `.gitignore` and `.helmignore` syntax, not a reliable anchor here.
4. **No re-deny section.** `**` already denied everything, so a trailing block of `test/` or `**/*.md` re-denies what was never admitted. If something unwanted reaches the image, narrow the `!` line that admits it.
5. **Admit the package-manager cache (`.npm`, `.uv`), never the installed tree** (`node_modules/`, `.venv/`): the image installs offline from the cache.

`COPY . .` is only as safe as the allowlist in front of it — review what the `!` lines admit, not that the file exists.

### Stack-by-Stack `.dockerignore` Reference

| Tech Stack | Allowlisted Packaging Targets | Sample `.dockerignore` |
| --- | --- | --- |
| **Python** (`uv` + `src/` layout) | `pyproject.toml`, `uv.lock`, `.uv/`, `src/` | `**`, `*`, `!pyproject.toml`, `!uv.lock`, `!.uv`, `!.uv/**`, `!src`, `!src/**` |
| **Java** (Spring Boot Fat JAR) | Maven (`target/*.jar`) or Gradle (`build/libs/*.jar`) | `**`, `*`, `!target/*.jar`, `!build/libs/*.jar` |
| **Golang** (Static Binary) | Pre-compiled binary (`bin/`) | `**`, `*`, `!bin/`, `!bin/*` |
| **Node.js Frontend** (Nginx SPA) | Static bundle (`dist/`) | `**`, `*`, `!dist/`, `!dist/**` |
| **Node.js Backend** (Express / NestJS) | `dist/`, `.npm` cache, `package*.json` | `**`, `*`, `!dist/`, `!dist/**`, `!package.json`, `!package-lock.json`, `!.npm`, `!.npm/**` |

[Documentation index](../README.md)
