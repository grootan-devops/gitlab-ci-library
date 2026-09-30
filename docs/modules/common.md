# common

The core backbone included in all pipelines. Computes semantic versions, manages `init.env`, and provides standard rule anchors and Trivy scanner scripts.

```mermaid
flowchart LR
    WVV["Workflow:Validate:Variables<br/>[stage: .pre]"] --> CI["Common:Init<br/>[stage: init]"]
    CI --> CL["Changelog:Lint<br/>[stage: lint]"]
    CI --> YL[".YAML:Lint<br/>[stage: lint]"]
    CI --> CCE["Changelog:Check Existence<br/>[stage: check]"]
    CI --> TTE["Tag:Tag Existence<br/>[stage: check]"]
```

| Job / Template | Stage | Description |
| --- | --- | --- |
| `Common:Init` | `init` | Calculates `RELEASE_VERSION`, `APP_PUSH_VERSION`, `TAG`, `MAJOR_VERSION`, `MINOR_VERSION`, `CHART_NAME`, `CHART_PUSH_VERSION`. Exports `init.env`. |
| `Changelog:Lint` | `lint` | Validates keepachangelog format in `CHANGELOG.md`. Runs in the Markdownlint image (`MD_LINT_IMAGE_REPO` / `MD_LINT_IMAGE_TAG`). |
| `Changelog:Check Existence` | `check` | Ensures `CHANGELOG.md` contains an entry for the version being released. |
| `Common:Check:Library:Pin` | `check` | Fails when an `include:` pins a branch, a commit or a pre-release instead of a published tag. Covers both `project:`/`ref:` and a `remote:` raw URL whose ref is a path segment. Set `ALLOW_UNSTABLE_LIBRARY_REFS: "true"` to downgrade it to a warning — testing only. Runs on MRs to the default or a protected master branch, in child pipelines, and for Web/API `full-pipeline` / `check` runs; never on default-branch pushes. |
| `Tag:Tag Existence` | `check` | Fails if the git tag already exists in the repository. |
| `Workflow:Validate:Variables` | `.pre` | Validates required inputs during manual `deploy` (checks `DEPLOY_TARGET`), `image-scan` (checks `TARGET_VERSION`), and `chart-scan` (checks local or remote chart). |
| `.scan-script` | — | Base Trivy scanning engine supporting image, config, license, and SBOM scanners. |
| `.MD:Lint` | `lint` | Reusable Markdownlint template for `LINT_MD_FILES`, run in `${MD_LINT_IMAGE_REPO}:${MD_LINT_IMAGE_TAG}` (default `markdownlint/markdownlint:0.18.1`). |
| `.YAML:Lint` | `lint` | Reusable yamllint template for `LINT_YAML_FILES`. |

[Documentation index](../../README.md)
