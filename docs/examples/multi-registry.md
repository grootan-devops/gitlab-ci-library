# 11. Publishing to Several Registries

One image published to the group's Harbor, to Quay and to Docker Hub, and one chart published
to Harbor and Docker Hub. The credentials of every registry live once, in a group-level
`REGISTRY_CONFIG` File variable; the project names its credential group and lists the full
repositories it publishes to:

```yaml
# .gitlab-ci.yml — IMAGE_REGISTRY and CHART_REGISTRY stay unset
variables:
  PROJECT_REGISTRY_NAME: oneuptime/prod
  IMAGE_REPOSITORY: "registry.example.com/core/api quay.io/oneuptime/api docker.io/oneuptime/api"  # the first is the primary
  CHART_REPOSITORY: "registry.example.com/helm registry-1.docker.io/oneuptime"

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
```

`REGISTRY_CONFIG`, a **File** variable on the top-level group with "Expand variable reference"
turned off, holds one credential group per client or organisation, every value quoted:

```yaml
oneuptime/prod:
  registry.example.com:
    username: 'robot$ci'
    password: '<token>'
  quay.io:
    username: 'oneuptime+ci'
    password: '<token>'
  docker.io:
    username: 'oneuptime'
    password: '<access token>'
oneuptime/dev:
  registry.example.com:
    username: 'robot$dev'
    password: '<token>'
```

> **What a merge request pipeline publishes** for version `1.4.0`:
>
> - `Image:Push`: `registry.example.com/core/api/dev`, `quay.io/oneuptime/api/dev` and
>   `docker.io/oneuptime/api-dev`, all at `1.4.0-rc.<pipeline>-<mr>`. Each registry is logged in
>   to once, with its credentials in `oneuptime/prod`.
> - `Chart:Push`: `oci://registry.example.com/helm/dev` and `oci://registry-1.docker.io/oneuptime`,
>   the namespace root Docker Hub keeps candidates and releases in.
>
> **On merge**, `Image:Promote` and `Chart:Promote` release `1.4.0` in `registry.example.com`,
> then copy the image by digest, with `latest`, `1` and `1.4`, to Quay and Docker Hub, and
> publish the same chart package to Docker Hub.
>
> A repository on this project's own `CI_REGISTRY`, such as
> `registry.gitlab.example.com/core/api`, needs no entry in the group: the CI job token logs in
> to it. Setting `IMAGE_REGISTRY` or `CHART_REGISTRY` as well stops the pipeline in
> `Common:Init`, before any other job runs.

[Documentation index](../../README.md)
