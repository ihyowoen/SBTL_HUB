# Temporary PR374 A007 artifact remediation seed

This file exists only to seed an artifact-only follow-up PR after #373. Before the PR becomes merge-ready, remove this file.

Required remediation scope: no canonical data changes. Correct the Sep-9 run artifacts so A007 (`STD26_0909_A_007`) no longer persists stale Reuters owner metadata or an invalid media-only single-source exception. Regenerate/reconcile Stage B and Stage C (and any downstream run-bound artifacts required by the active contracts) using verified multi-owner evidence if valid, rerun the artifact contract checks, and expose the new exact Stage B artifact SHA for PR #374 to bind. Keep this follow-up artifact-only and fail closed.
