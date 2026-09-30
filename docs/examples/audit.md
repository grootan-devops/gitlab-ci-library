# 8. Security & Code Quality Audit Only Pipeline

For repositories wanting lightweight security and quality gates without packaging containers:

```yaml
# .gitlab-ci.yml
variables:
  PROJECT_CACHE_KEY: node-audit

include:
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/common/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/nodejs/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/sonarqube/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/secret-scanning/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/license/.gitlab-ci.yml'
  - remote: 'https://raw.githubusercontent.com/grootan-devops/gitlab-ci-library/1.8.1/sbom/.gitlab-ci.yml'
```

[Documentation index](../../README.md)
