# 6. Terraform Infrastructure / Module Registry

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: terraform-vpc-module
  RELEASE_VERSION: 1.2.3

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/terraform/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/terraform/.test.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/<version>/release/.gitlab-ci.yml'
```

The release tags the repository; consumers pin that tag with `?ref=`:

```hcl
module "vpc" {
  source = "git::git@gitlab.contoso.com:infra/terraform-modules.git//modules/vpc?ref=<version>"
}
```

## Several Terraform roots

A repository with one root per environment or account runs the Terraform jobs once per root. Each
root gets its own `PROJECT_PATH` and `PROJECT_CACHE_KEY`, so it restores only its own
`.terraform`, and keeps its own README for `Terraform:Check:README`. The release jobs keep the
project's `PROJECT_PATH`.

Each root's `Terraform:Scan` reaches the release with no extra job: `Release:Upload` bundles
every root's Trivy reports in `trivy_scan_report.tar.gz` under that root's path
(`stacks/network/terraform_trivy_scan_report.json`), and merges each root's `TF_CVE.md` into the
release notes under a "Terraform root `stacks/network`" heading. A project that copied scan
reports to the repository root with a job of its own drops that job.

```yaml
.terraform-roots: &terraform-roots
  matrix:
    - PROJECT_PATH: stacks/network
      PROJECT_CACHE_KEY: terraform-network
    - PROJECT_PATH: stacks/platform
      PROJECT_CACHE_KEY: terraform-platform

Terraform:Init:
  parallel: *terraform-roots

Terraform:Validate:
  parallel: *terraform-roots

Terraform:Lint:
  parallel: *terraform-roots

Terraform:Check:README:
  parallel: *terraform-roots

Terraform:Scan:
  parallel: *terraform-roots
```

[Documentation index](../../README.md)
