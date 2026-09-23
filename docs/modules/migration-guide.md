# migration-guide (`readme/.migration-guide.gitlab.yml`)

The `readme/.migration-guide.gitlab.yml` module provides automated migration guide validation and extraction for libraries and repositories tracking breaking changes or upgrade instructions:

- `Migration:Lint`: Validates markdown formatting of `${MIGRATION_FILE_NAME}` using Markdownlint (`.MD:Lint`).
- `Migration:Check Existence`: Strictly verifies that every release (major, minor, or patch) has a documented section in `${MIGRATION_FILE_NAME}`. If missing, the pipeline blocks with a failure. If no migration is required, the release entry must explicitly state "No migration required". Extracts the matched version notes into `${RELEASE_MIGRATION_FILE_NAME}` as a job artifact for automatic inclusion in GitLab Releases.

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/readme/.migration-guide.gitlab.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'
```

[Documentation index](../../README.md)
