# python

Python service lifecycle management powered by `uv`, Ruff, and MyPy.

The `.Python:12` runtime clears the container entrypoint with `entrypoint: [""]`.
GitLab Runner supplies the shell command; do not override this with `["/bin/bash"]`,
which can cause Bash to interpret Runner's shell executable as a script and fail with
`cannot execute binary file`. Consumers extending `.Python:12` inherit this setting.

```mermaid
flowchart LR
    PVI[".Python:Project:Version:Init<br/>[stage: .pre]"] --> CI["Common:Init<br/>[stage: init]"]
    CI --> PDD[".Python:Dependency:Download<br/>[stage: prepare]"]
    PDD --> PLR["Python:Lint:Ruff<br/>[stage: lint]"]
    PDD --> PLM["Python:Lint:MyPy<br/>[stage: lint]"]
    PDD --> PLI["Python:Lint:ISort<br/>[stage: lint]"]
    PDD --> PLP["Python:Lint:PyCodeStyle<br/>[stage: lint]"]
    PDD --> PTU[".Python:Test:Unit<br/>[stage: test]"]
    PDD --> PB[".Python:Build<br/>[stage: build]"]
```

| Job / Template | Type | Stage | Description |
| --- | --- | --- | --- |
| `.Python:12` | Template | — | Python 3.12 runtime base image + `.uv` cache. |
| `.Python:Project:Version:Init` | Template | `.pre` | Extracts version from `pyproject.toml`. |
| `.Python:Dependency:Download` | Template | `prepare` | Warms `.uv` cache via `uv sync --frozen --no-install-project --no-install-workspace`. |
| `.Python:Build` | Template | `build` | Compiles wheel/sdist archives to `dist/` via `uv build --offline`. |
| `Python:Lint:Ruff` | Job | `lint` | Ruff linting. |
| `Python:Lint:MyPy` | Job | `lint` | Static type checking. |
| `Python:Lint:ISort` | Job | `lint` | Import order formatting validation. |
| `Python:Lint:PyCodeStyle` | Job | `lint` | PEP8 code style enforcement. |
| `.Python:Test:Unit` | Template | `test` | Unit test execution base with JUnit report collection. |

[Documentation index](../../README.md)
