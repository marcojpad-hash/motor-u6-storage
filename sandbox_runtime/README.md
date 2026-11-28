U6 sandbox-testing — PREPARADO / NO EJECUTADO / NO ACTIVADO

This is an initial fail-closed preflight scaffold, not a production sandbox.
It validates the versioned job/bridge schemas and source identity. It does not invoke Engine, factory, search providers, LLMs, shell commands, or arbitrary adapters.

The workflow is manual-only on ubuntu-24.04, contents:read, checkout persist-credentials:false, no secrets and no write token. It has not been dispatched.

IMPORTANT BLOCKER: policy/protected-paths.json has complete=false. Only two known canonical paths are listed; the full protected inventory and official manifests have not been reconciled. The runner must block while incomplete. This is not evidence of complete Engine/244 protection.

The Actions runner is ephemeral hosted infrastructure, not a persistent VM service or a separate microVM. No hostile-code isolation is claimed. Docker/Compose is intentionally not introduced in this first pass.
