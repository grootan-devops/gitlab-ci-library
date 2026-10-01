# Quick Start

Include the shared templates from the library repository in your project's `.gitlab-ci.yml`:

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.docker.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/image/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/chart/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sbom/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'
```

> [!IMPORTANT]
> This library is hosted on GitHub, so it is included with `remote:` and a raw URL — **not**
> `project:`. `include: project:` only resolves against another project on the same GitLab
> instance; pointed at a GitHub path it fails at resolution. `remote:` takes one URL per
> entry, so a multi-file include becomes one line per file.
>
> [!IMPORTANT]
> The `<version>` segment in these URLs is the **git ref**. Replace it with the published stable tag
> selected for your project and verify it with `git ls-remote --tags --heads` before copying the
> examples. Read the documentation at that same ref. Branch refs such as `dev` move and
> should be used only for deliberate development testing, not stable releases.
>
> [!NOTE]
> `include: remote:` supports **no authentication**, so every file it fetches must be
> publicly readable. This repository is public, which is what makes the URLs above work. If
> it is ever made private, `remote:` stops working and the templates have to be mirrored to
> a project on your own GitLab instance and included with `project:` instead.

## Start from the complete include set

A service repository starts from the list above and removes only what it can justify; a
list of only `common`, the language module, `image/*` and `chart/` looks tidy and silently
gives up SonarQube, secret scanning, licence compliance, SBOM and releases. `common` is
required by every pipeline. Use the stack's own module in place of `nodejs` (`python`,
`golang`, `java`); `image/.docker.gitlab-ci.yml` is the builder (`.buildah` is the
alternative); secret scanning reads the whole git history. Move every include to a new
version together, and declare `WORKFLOW` to match the modules included (see
[Pipeline lifecycle](pipeline-lifecycle.md#declaring-workflow-in-a-project)).

An **image-only** repository — a Dockerfile with no application dependency manifest —
includes only `common`, the image builder, the image lifecycle, secret scanning and release:
there is no source dependency graph for the language, SonarQube, licence or SBOM modules. The
image vulnerability scan still applies.

Two modules are conditional:

| Module | Add when | Leave out when |
| --- | --- | --- |
| `readme/.migration-guide.gitlab.yml` | the repository publishes a versioned contract others upgrade against | it is an application nobody pins — `Migration:Check Existence` blocks every release for a `MIGRATION.md` nobody reads |
| `deploy/gitops/.komodo` or `.argocd` | the GitOps repository, branch and application are known | the deployment target is still undecided |

A module whose repository-level file is missing fails at runtime, not at pipeline creation:

| Module | Requires in the repository |
| --- | --- |
| `sonarqube/` | `sonar.properties`, plus `SONARQUBE_TOKEN` and `SONAR_URL` |
| `readme/.migration-guide.gitlab.yml` | `MIGRATION.md` with a `## [<prev>...<curr>]` heading |
| `license/`, `sbom/`, `image/` | `ignored-cves.yml` when any CVE or licence is waived |

Declare the project's own jobs as described in [Project jobs](project-jobs.md).

## Repository ignore files

`.gitignore` keeps generated and secret files out of history: `.env` and `.env.*` (with
`!.env.example` re-admitted), `*.pem`, `*.key`, and the outputs of the stacks the project
actually uses — `node_modules/` and `dist/` (Node), `__pycache__/`, `.venv/`, `.uv/` and
`.pytest_cache/` (Python), `target/` and `.gradle/` (Java), `bin/` (Go). A chart adds
`charts` and `Chart.lock` (helm-tpl-library chart standards). The `.dockerignore` rules are in
the [Dockerfile standards](docker.md).

[Documentation index](../README.md)
