---
name: plan-keeper
description: Create, approve, maintain, and resume a single local implementation plan for a development task in a Git repository. Use when a user requests a persistent plan, plan approval before coding, progress tracking against a plan, or continuation of an existing plan.
---

# Plan Keeper

Use one canonical `.ai/plans/<task-id>.md` in the current Git working tree for the entire task. Resolve paths to scripts and assets relative to this skill's folder. Run the helper from within the target project.

## Find or create the plan

- Start with the plan path or task ID the user supplied, or the one established earlier in the chat. Otherwise look for a matching plan in the current working tree's `.ai/plans/`. Skip symlinks and run the helper's `check` on candidates before reading them. Match by objective and scope as well as filename. If several plans could match, ask which one to resume.
- For a genuinely new task, use the issue ID if available or choose a date and descriptive slug, such as `20261107-redis-timeout`. Run `python3 <skill-dir>/scripts/plan_keeper.py init <task-id>`. The helper copies [the template](assets/implementation-plan.md) and refuses to overwrite an existing plan. If the ID already exists, inspect that plan before deciding whether this is the same task or a different one.
- For an existing plan, run `python3 <skill-dir>/scripts/plan_keeper.py check <task-id>` before reading or editing it. If either command fails, resolve the reported issue before storing task details. Keep the path stable and share it whenever asking for approval or handing off the task.

## Plan and get approval

1. Inspect the relevant code and tests within the user's scope and repository rules. Fill in the objective, acceptance criteria, current behavior with evidence, proposed files or components, exclusions, implementation steps, verification, risks, and rollback. Record the current branch and HEAD, or that HEAD is unborn.
2. Present the plan path and request explicit approval for its current revision. Leave it in `DRAFT` or `REPLANNING` while waiting. Read-only investigation and plan updates can continue while approval is pending. Project implementation edits and implementation side effects require approval.
3. Record the user's approval in the plan with the revision and a chat reference or dated summary, then set `APPROVED`. Approval must be traceable to the user. A plan status, a previous revision's approval, or a request to resume does not by itself authorize implementation. Existing repository or action-specific approval requirements still apply.
4. Start only approved steps. If a material change is needed in scope, approach, or risk, log what changed, increment the revision, set `REPLANNING`, and request approval for the revised plan before continuing implementation. Keep prior approvals in the same file.

## Execute, sync, and resume

- Set `IN_PROGRESS` when starting. After each meaningful step, update its checkbox and record affected files, decisions, and observed results. For a blocker, set `BLOCKED` and record its cause, last completed step, and next action. Progress-only updates keep the same revision.
- On return, read the entire plan and compare its branch, HEAD, and execution record with the actual working tree and diff. Preserve unrelated changes. Reconcile discrepancies before relying on completion marks or approvals. If evidence of approval is missing or the approved work materially changed, obtain approval before resuming. Plans stay in the working tree where they were created. Ask for the original plan or working tree if recovery points elsewhere.
- Set `VERIFYING` when running checks. Record commands and observed outcomes, skipped checks with reasons, changed files, and commit or PR links if available. Set `COMPLETED` after the acceptance criteria are met and record any remaining verification gaps. Keep this plan for follow-ups on the same task.
- Re-run `check` before staging, committing, or publishing. Stage project files by path and inspect the staged file list. Never force-add, commit, or publish plans or copy sensitive plan contents into public artifacts. If any plan path is tracked or staged, stop and report it before further Git publication. Exclusion rules cannot remove existing Git history.
