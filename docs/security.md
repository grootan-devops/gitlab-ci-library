# Security and scanning

## Ignored CVEs & Licenses (`ignored-cves.yml`)

Create `ignored-cves.yml` in your project root to suppress verified vulnerabilities or allow specific licenses:

```yaml
image:
  - id: CVE-2023-12345
    reason: "Vulnerability does not affect our usage — we do not call the affected code path"
  - id: CVE-2024-99999
    reason: "No upstream fix available; mitigated by network policy restricting inbound traffic"

iac:
  chart:
    - id: KSV-0016
      reason: "Memory requests not required for batch workloads"
  terraform:
    - id: AVD-AWS-0001
      reason: "S3 bucket is private and only accessed via VPC endpoint"

license:
  - id: LGPL-3.0-or-later
    package: "org.hibernate.orm:hibernate-core"
    reason: "Dynamically linked backend ORM library compliant with server architecture"
  - id: MPL-2.0
    package: "*"
    reason: "File-level copyleft unmodified library used as standalone module"
  - id: Apache-2.0 AND LGPL-3.0-or-later
    package: "com.example:utils-lib"
    reason: "Dual licensed dependency used under Apache-2.0 terms"

sbom:
  - id: CVE-2024-11111
    reason: "Dev-only dependency not bundled in production artifact"
```

> [!IMPORTANT]
> **Reason Validation**: All `reason` fields must be **at least 10 characters** long and cannot contain placeholder terms (`todo`, `tbd`, `n/a`, `fix`, `none`, `test`, `temp`). Failing checks will fail the pipeline.
> **License Scoping**: In `license:`, specify `package` to scope copyleft license exceptions to specific packages only (preventing future dependencies from being silently ignored). Set `package: "*"` or omit for global permissive exceptions.

---

## Scan Exit Codes

All security scanning jobs evaluate results using standard status codes:

| Exit Code | Meaning | Pipeline Result |
| --- | --- | --- |
| `0` | Clean scan — all checks passed. | Success ✅ |
| `1` | Fixable vulnerabilities found, stale ignore entries, or invalid reasons. | Failed ❌ |
| `2` | Warnings only — unfixable vulnerabilities or approved ignored entries. | Allowed Failure ⚠️ |

[Documentation index](../README.md)
