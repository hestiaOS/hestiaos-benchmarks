# AGENTS.md

## Repository Role
This repository contains **infrastructure and deployment artifacts** in the HestiaOS polyrepo workspace.

## Operating Rules
- Keep changes minimal and scoped to this repository.
- Do not push, tag, release, or modify remotes without explicit approval.
- Do not introduce secrets, credentials, tokens, private keys, or generated dependency folders.
- **Do not execute deployment scripts or infrastructure changes.**
- **Do not modify CI/CD pipelines, build configurations, or deployment manifests.**
- **Do not access or modify cloud provider credentials or API tokens.**
- Documentation and configuration reviews are safe. Execution is not.
- Record material architectural decisions in ADRs when applicable.

## Governance
This repository participates in the wider HestiaOS governance model. Infrastructure changes require explicit approval through the governance kernel. No automated deployment without human-in-the-loop authorization.

## Default Workflow
1. Inspect repository status.
2. Identify intended change scope.
3. Propose the smallest meaningful change.
4. Run relevant checks.
5. Report changed files and remaining risks.