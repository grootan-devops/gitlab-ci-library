# Quick Start

Include the shared templates from the library repository in your project's `.gitlab-ci.yml`:

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'
```

> [!IMPORTANT]
> This library is hosted on GitHub, so it is included with `remote:` and a raw URL — **not**
> `project:`. `include: project:` only resolves against another project on the same GitLab
> instance; pointed at a GitHub path it fails at resolution. `remote:` takes one URL per
> entry, so a multi-file include becomes one line per file.
>
> [!IMPORTANT]
> The `1.0.0` segment in these URLs is the **git ref**. Use the published stable ref selected
> for your project and verify it with `git ls-remote --tags --heads` before copying the
> examples. Read the documentation at that same ref. Branch refs such as `dev` move and
> should be used only for deliberate development testing, not stable releases.
>
> [!NOTE]
> `include: remote:` supports **no authentication**, so every file it fetches must be
> publicly readable. This repository is public, which is what makes the URLs above work. If
> it is ever made private, `remote:` stops working and the templates have to be mirrored to
> a project on your own GitLab instance and included with `project:` instead.

[Documentation index](../README.md)
