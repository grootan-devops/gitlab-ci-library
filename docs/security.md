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

## Reviewing a consumer repository

The pipeline's own checks are exact and structural. What follows needs someone to read a value
and judge what it means.

### Secrets — classify by value, not by key name

Ask of every value in the repository, its CI variables, `.env` and compose files:

- **Does a URL embed a credential?** A connection string with `user:password@` before its host
  (Postgres, AMQP, MongoDB, a Git remote with a token) is a live credential, however innocuous
  its key.
- **Is it high-entropy?** Long random-looking strings are keys even in a field called `id` or
  `ref`; `API_KEY: ""` or a vault reference is fine.
- **Is a private key or certificate inlined?** `-----BEGIN ... PRIVATE KEY-----` anywhere.
- **Is a real value posing as a placeholder?** `changeme`, `admin` or `test123` shipped to an
  environment is a credential.
- **Is a non-secret value in the secret store?** Over-classification hides which values matter.
- **Is a secret transformed before it is printed?** Masking covers the known value, not its
  base64 encoding, a `jq` extract or a slice.

### Pipeline posture

- Prefer a short-lived, job-scoped token to a long-lived one; a static credential is
  read-only unless the job pushes.
- Every secret variable is both masked and protected.
- No secret is echoed, including through `set -x` or a constructed URL.
- Third-party components are pinned when the job holds credentials.
- Failures do not pass silently: no `curl` without `--fail`, no `|| true` around an auth step.
- A job publishing outside its own project uses an explicitly granted credential; if it "just
  works", something is over-permissioned.

### GitLab specifics

A GitLab pipeline normally runs on your code with your credentials, so the pressure is on
token scope, variable exposure and cross-project access.

| Context | Who can trigger | Secrets available |
| --- | --- | --- |
| Push or MR from a branch in the project | members with write access | all, subject to protection |
| MR from a **fork** | any user | no protected variables; `CI_JOB_TOKEN` is fork-scoped |
| Scheduled pipeline | the schedule owner | runs as that user |
| Downstream or multi-project trigger | the upstream project | what the trigger passes |

- **Fork MRs**: the failure is someone unprotecting a variable to "make the fork pipeline
  work", so every unprotected branch can read it.
- **`CI_JOB_TOKEN`** is scoped to the project and expires with the job. It reaches another
  project only through that project's **Settings → CI/CD → Token Access** allowlist. A personal
  or deploy token used where the job token would do is a standing liability; scope one that is
  genuinely needed to `read_registry` unless the job pushes.
- **Variables**: masking has format constraints, and a value that fails them is silently not
  masked. Group-level variables reach every project in the group. `CI_DEBUG_TRACE` prints the
  whole environment.
- **Rules**: a job with no `rules:` runs in every workflow; `when: manual` is a convenience,
  not a control — use protected environments and branches for a real gate; a `rules:` entry
  without `when:` defaults to `on_success`, so a cleanup job never runs after the failure it
  exists for.
- **Runners**: shared runners on a public project run fork MR code; a `privileged` runner can
  escape to the host; a long-lived self-hosted runner inherits whatever the last job left.
- **Supply chain**: an `include:` ref that is a branch or tag can change under you, a commit
  SHA cannot; a repository that includes itself uses `local:`; public images route through the
  Dependency Proxy or a mirror.

[Documentation index](../README.md)
