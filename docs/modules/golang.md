# golang

Go microservice and CLI pipeline with automated formatting, vet directives, and security scanning.

```mermaid
flowchart LR
    CI["Common:Init<br/>[stage: init]"] --> GDD["Go:Dependency:Download<br/>[stage: prepare]"]
    GDD --> GF["Go:Fmt<br/>[stage: lint]"]
    GDD --> GV["Go:Vet<br/>[stage: lint]"]
    GDD --> GL["Go:Lint<br/>[stage: lint]"]
    GDD --> GSS["Go:Security:Scan<br/>[stage: lint]"]
    GDD --> GTU[".Go:Test:Unit<br/>[stage: test]"]
    GDD --> GB[".Go (Build)<br/>[stage: build]"]
```

| Job / Template | Type | Stage | Description |
| --- | --- | --- | --- |
| `Go:Dependency:Download` | Job | `prepare` | Warms Go module cache via `go mod download`. |
| `Go:Fmt` | Job | `lint` | Enforces `go fmt` compliance. |
| `Go:Vet` | Job | `lint` | Runs `go vet` with `// govet:ignore` suppression support. |
| `Go:Lint` | Job | `lint` | Comprehensive linting with `golangci-lint`. |
| `Go:Security:Scan` | Job | `lint` | Static security audit with `gosec`. |
| `.Go` | Template | `build` | Go build base image + cache configuration. |
| `.Go:Test:Unit` | Template | `test` | Unit test runner with JUnit conversion. |

[Documentation index](../../README.md)
