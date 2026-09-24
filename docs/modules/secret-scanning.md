# secret-scanning

```mermaid
flowchart LR
    CI["Common:Init<br/>[stage: init]"] --> GSS["Git:Secret:Scan<br/>[stage: security]"]
```

`Git:Secret:Scan` (stage `security`): Betterleaks secret detection across complete repository commit history. Detected secrets are masked from job logs.

[Documentation index](../../README.md)
