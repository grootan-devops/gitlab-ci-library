# Migration Guide & Standard

This document defines the **Migration Standard** for the GitLab CI/CD Library and contains the historical, version-by-version migration instructions for all **major releases** (breaking changes).

This standard is designed specifically to be consumed by **AI Coding Assistants & Migration Skills** (e.g., Google Antigravity, Cursor, Claude Code, custom CLI migration agents) as well as platform engineers upgrading consumer repositories from one major version to another.

---

## [7.0.0...7.1.0] - 2026-09-16

### 1. Overview
Removes the Terraform module packaging and registry-publish job. Terraform resolves modules
directly from git, so the tarball and registry upload duplicated what the git ref already
provides.

### 2. Breaking Changes & Upgrade Steps

| # | Change | Action required |
|---|---|---|
| 1 | `terraform/.module.gitlab-ci.yml` removed | Delete the `include:` entry. There is no replacement job. |
| 2 | `Terraform:Module:Push` removed | Consumers pin the git ref instead of a registry version (see §3). |
| 3 | `.terraform-publish-rules` renamed to `.terraform-module-test-rules` | Update any project-level `extends:` referencing the old name. |
| 4 | `TF_MODULE_NAME`, `TF_MODULE_SYSTEM`, `TF_FILE_PATH`, `TF_MD_FILE_NAME` removed | Delete them from project `variables:`. They are now inert. |
| 5 | `Terraform:Module:Test` now needs `Terraform:Validate` | None — automatic. |

### 3. Consuming a module after this change

The release still tags the repository. Consumers pin that tag:

```hcl
module "vpc" {
  source = "git::git@gitlab.example.com:infra/terraform-modules.git//modules/vpc?ref=2.1.0"
}

module "eks" {
  # git::<repo_url>//<sub_folder>?ref=<tag | branch | commit>
  source = "git::git@gitlab.example.com:infra/terraform-modules.git//modules/eks?ref=b4f8d29"
}
```

Pin `?ref=` to a tag or commit SHA. A branch ref re-resolves on every `terraform init`, so a
plan can change without the consuming repository changing.

---

## [6.5.0...7.0.0] - 2026-09-14

### 1. Overview
Version `7.0.0` introduces automated migration guide enforcement, release note consolidation with extracted migration notes, fixes `workflow:` regex evaluations for master branches, and rectifies container/chart release scanning and upload pathways.

### 2. Breaking Changes & Upgrade Steps

#### 1. Migration Guide Enforcement (`readme/.migration-guide.gitlab.yml`)
- **Requirement**: Every release (major, minor, or patch) now strictly enforces the presence of documented upgrade/migration notes in `MIGRATION_FILE_NAME` (default `./MIGRATION.md`).
- **Action**: Ensure your repository contains `MIGRATION.md` with a heading matching `## [<prev>...<curr>]` or `## [<curr>]`. If a release has no breaking changes or manual steps, explicitly state `No migration required`.
- **Include Template**: Repositories generating documentation can include:
  ```yaml
  include:
    - project: 'devops/cicd/ci-templates'
      ref: '7.0.0'
      file:
        - '/readme/.migration-guide.gitlab.yml'
  ```

#### 2. Master Branch Regex Split
- `MASTER_BRANCH_REGEX` is now strictly slash-delimited for GitLab CI `rules:` matching (e.g., `/^(master|main)$/`).
- `MASTER_BRANCH_PATTERN` is used for POSIX shell tests. If your custom pipelines overrode `MASTER_BRANCH_REGEX` with a shell pattern, split it into `MASTER_BRANCH_REGEX` and `MASTER_BRANCH_PATTERN`.

#### 3. Consolidated Release Migration Notes
- Release jobs automatically include `RELEASE_MIGRATION_FILE_NAME` (default `RELEASE_MIGRATION.md`) in `${CONSOLIDATED_RELEASE_CHANGELOG_FILE_NAME}` and attach it to GitLab Releases.

