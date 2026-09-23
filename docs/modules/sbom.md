# sbom

CycloneDX Software Bill of Materials generation and vulnerability scanner:

```mermaid
flowchart LR
    CI["Common:Init<br/>[stage: init]"] --> SG["SBOM:Generate<br/>[stage: build]"]
    SG --> SS["SBOM:Scan<br/>[stage: security]"]
```

- `SBOM:Generate` (stage `build`): Generates `sbom.cdx.json`.
- `SBOM:Scan` (stage `security`): Scans SBOM components for CVEs via Trivy server.

[Documentation index](../../README.md)
