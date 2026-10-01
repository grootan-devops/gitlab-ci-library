# Project jobs

A consumer `.gitlab-ci.yml` declares a few jobs that extend library templates; the library
does the work. Keep the project file to that minimum.

## The job wrappers

```yaml
Project:Version:Init:
  extends: .Node:Project:Version:Init

Node:Dependency:Download:
  extends:
    - .Node:24
    - .Node:Dependency:Download

Project:Build:
  extends:
    - .Node:24
    - .Node:Build
  needs:
    - job: Common:Init
      artifacts: true
      optional: true
    - job: Node:Dependency:Download
      artifacts: false
      optional: false

Project:Unit:Test:
  extends:
    - .Node:24
    - .Node:Test:Unit
  needs:
    - job: Project:Build
      artifacts: true
      optional: false
```

Python and Java use the same wrapper pattern (`.Python:12` + `.Python:Dependency:Download`,
`.Java:25` + `.Java:Dependency:Download`). `Go:Dependency:Download` is already a concrete
library job, so a Go project declares no wrapper for it.

- **Keep the canonical names.** `Image:Build` needs `Project:Build` for its artifacts and
  `Sonarqube` needs `Project:Build` and `Project:Unit:Test`. Those needs are optional, so a job
  under another name (`Node:Project:Build`) fails nothing: the image builds without the build
  output and the analysis runs without the test reports.
- **Runtime anchor first, job template second.** `.Node:24`, `.Python:12`, `.Go` and `.Java:25`
  set `image:` and the cache; the job template sets stage, rules, `needs:` and artifacts.
  `extends:` merges left to right with later entries winning, so the reverse order lets the
  anchor overwrite keys the template owns.
- **`PROJECT_CACHE_KEY` is one value** on the dependency-download job and on every cache
  reader, including `Image:Build` (see [Configuration](configuration.md)). Never revert a
  custom key the project team set.
- **Never override `image:` in a consumer job.** The runtime anchor owns it. When a job fails
  because of its image, fix the library or the base image, not the consumer; a consumer
  workaround outlives the fix.
- **Declare nothing the template already gives you** — `NODE_ENV: test` on
  `Project:Unit:Test`, `cache: policy: pull`, the template's `needs:`. A restated key stops
  tracking the library when the library changes.
- **Every `needs:` entry states `optional:`.** `true` where the upstream is gated out of some
  workflows, `false` where the artifact is genuinely required. Left out, it defaults to
  `false`, and pipeline creation fails with "job needs a job that is not in the pipeline" as
  soon as that upstream is gated out.

## `Project:Build` is optional

`Project:Build` (`.Node:Build`, `.Python:Build`, …) is a skeleton with no script — stage,
rules, cache and `needs` only — for a repository with a real compile or bundle step. Declare
it only then, and supply the script and the artifact:

```yaml
Project:Build:
  extends:
    - .Node:24
    - .Node:Build
  script:
    - npm ci --include=dev --offline --no-audit --no-fund
    - npm run build
  artifacts:
    paths:
      - dist/
```

A plain-JavaScript service with no `build` script declares neither `Project:Build` nor a unit
test job; the dependency download still warms the cache that `Image:Build` restores. There is
no separate install job: the image installs production dependencies itself (see the
[Dockerfile standards](docker.md)).

Only `Project:Build` and `Project:Unit:Test` override `script:`. Shared jobs — the dependency
downloads, `Chart:*`, `Release:*` and the scanners — are not overridden.

```yaml
# Python: no Project:Build for a containerised service
Project:Unit:Test:
  extends: .Python:Test:Unit
  script:
    - uv run pytest --cov --junitxml=junit.xml

# Go
Project:Unit:Test:
  extends: .Go:Test:Unit
  script:
    - go test -race -coverprofile=coverage.out ./...

# Java
Project:Build:
  extends: .Java:Build
  script:
    - mvn -B package -DskipTests
```

## Split or custom build and test jobs

`Sonarqube` defaults to `needs: [Common:Init, Project:Build, Project:Unit:Test]` and
`Image:Build` to `needs: [Common:Init, Project:Build, Node:Dependency:Download,
Python:Dependency:Download]`. When a repository splits them — `Project:Unit:Test:Frontend` and
`Project:Unit:Test:Backend`, or `Project:Build:Frontend` — the optional canonical needs match
nothing, so both jobs start right after `Common:Init`: SonarQube without the test reports and
coverage, and `Image:Build` before `dist/` exists. Override their `needs:`:

```yaml
Sonarqube:
  needs:
    - job: Common:Init
      artifacts: true
      optional: true
    - job: Project:Unit:Test:Frontend
      artifacts: true
      optional: true
    - job: Project:Unit:Test:Backend
      artifacts: true
      optional: true

Image:Build:
  needs:
    - job: Common:Init
      artifacts: true
      optional: true
    - job: Project:Build:Frontend
      artifacts: true
      optional: false
```

`artifacts: true` on jobs that produce reports or bundles (`junit.xml`, coverage, `dist/`);
`artifacts: false` on dependency downloads, which share a cache, not artifacts.

## Script formatting

Single-line list items, unless the logic is genuinely multi-line, then `- |`. Never wrap a
lone command in a block scalar; it hides the command from a quick scan.

```yaml
script:
  - echo "Checking ${RELEASE_VERSION} in ${CHANGELOG_FILE_NAME}..."
  - |
    if [[ ! -f ${CHANGELOG_FILE_NAME} ]]; then
      echo "${CHANGELOG_FILE_NAME} is missing in the repo"
      exit 1
    fi
```

[Documentation index](../README.md)
