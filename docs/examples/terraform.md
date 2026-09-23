# 6. Terraform Infrastructure / Module Registry

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: terraform-vpc-module
  RELEASE_VERSION: 1.0.0
  TF_STATE_NAME: vpc-infrastructure

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/terraform/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/terraform/.test.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.0.0/release/.gitlab-ci.yml'
```

The release tags the repository; consumers pin that tag with `?ref=`:

```hcl
module "vpc" {
  source = "git::git@gitlab.contoso.com:infra/terraform-modules.git//modules/vpc?ref=1.0.0"
}
```

[Documentation index](../../README.md)
