# mono

- **Root Pipeline (`mono/.gitlab-ci.yml`)**: Includes common module and handles path-based child pipeline triggering.
- **Child Pipeline (`common/.mono.gitlab-ci.yml`)**: Keeps `Common:Init` and release checks while setting rules to `when: always` for parent-triggered runs.

[Documentation index](../../README.md)
