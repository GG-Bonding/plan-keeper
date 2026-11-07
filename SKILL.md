---
name: plan-keeper
description: Create, approve, maintain, and resume a single local implementation plan for a development task in a Git repository. Use for technical design documents, persistent plans, approval before coding, reconstructing a plan from implemented code, tracking a task across modules, or resuming an existing plan.
---

# Plan Keeper

Use one canonical `.ai/plans/<task-id>.md` in the current Git working tree for the entire task. Resolve paths to scripts and assets relative to this skill's folder. Run the helper from within the target project.

## Find or create the plan

- Start with the plan path or task ID the user supplied, or the one established earlier in the chat. Otherwise look for a matching plan in the current working tree's `.ai/plans/`. Skip symlinks and run the helper's `check` on candidates before reading them. Match by objective and scope as well as filename. If several plans could match, ask which one to resume.
- When no plan exists for the task, use the issue ID if available or choose a date and descriptive slug, such as `20261107-redis-timeout`. Run `python3 <skill-dir>/scripts/plan_keeper.py init <task-id>`. The helper copies [the template](assets/implementation-plan.md) and refuses to overwrite an existing plan. If the ID already exists, inspect that plan before deciding whether this is the same task or a different one.
- For an existing plan, run `python3 <skill-dir>/scripts/plan_keeper.py check <task-id>` before reading or editing it. If either command fails, resolve the reported issue before storing task details. Keep the path stable and share it whenever asking for approval or handing off the task.

## Write a reviewable technical design

- Use UTF-8 Markdown and write the plan in the user's requested language. Start with a short review summary, then give the scope and current behavior with evidence. For material decisions, record the options, rationale, trade-offs, and status before the implementation details. If a decision changes, add its replacement and keep the original rationale.
- Use a focused Mermaid flowchart for branching or state changes and a sequence diagram for cross-module calls. Draw only paths needed for the review, including relevant failure paths and outcomes. Omit a diagram when the behavior is clearer in prose.
- Show the relevant code changes as short diffs or language snippets with real file and symbol references. Label proposed snippets as illustrative and distinguish them from observed code. When useful, use the same decision ID in the diagram caption, code discussion, and acceptance table.
- Keep the main plan focused on cross-module contracts and acceptance. Put module-specific diagrams, code, and results in the linked records. Replace placeholders and omit optional sections that add no value. Preserve existing plans and their history when resuming them.

## Backfill a plan for implemented work

- Find or create the canonical plan with the same workflow. Record the branch and HEAD inspected, then use relevant code, commits, diffs, and available test evidence to reconstruct what has landed. Separate implemented behavior, verified results, and remaining work. Mark missing evidence as unknown and label any checks run now as new verification.
- Record a historical approval or test outcome only when you can cite its evidence. For record-only requests, update the plan without editing project code or requesting retroactive approval. Replace the template's pending approval placeholder with a record-only note if there is no proposed work. Use `COMPLETED` only when the acceptance criteria are supported by evidence and no planned work remains. Record gaps and next actions otherwise.
- If the user wants follow-up implementation, separate the proposed work from the historical record and apply the approval gate to that proposal. For an existing plan, preserve its approval history and revise it when the proposed work materially changes.

## Split details by module

- Keep `.ai/plans/<task-id>.md` as the recovery entry point and the authority for overall scope, approvals, cross-module contracts, and acceptance. In the parent plan's module section, link each document with a relative path and a short description of its responsibility.
- Store one document per module at `.ai/plans/<task-id>/<module-slug>.md`, using lowercase letters, digits, and hyphens. Use the [module record template](assets/module-record.md). Keep the same path as the module evolves. Before reading or writing a module file, run the helper's `check <task-id>` for the parent plan, reject symlinks in the module directory or file, and verify the exact module path from the project root with `git check-ignore -q -- <module-path>`. Stop if either check fails.
- Update the module document for local progress and verification. Update the parent when a module's next action affects the task as a whole, or when cross-module contracts, overall acceptance, or approved scope change. Keep approval and revision history in the parent. A material scope, approach, or risk change still requires reapproval before implementation.
- Resume from the parent and open the linked documents relevant to the next action. If the user gives a module path, resolve its parent plan first and confirm the link there.

## Plan and get approval

1. Inspect the relevant code and tests within the user's scope and repository rules. Fill in the objective, acceptance criteria, current behavior with evidence, proposed files or components, exclusions, implementation steps, verification, risks, and rollback. Record the current branch and HEAD, or that HEAD is unborn.
2. Present the plan path and request explicit approval for its current revision. Leave it in `DRAFT` or `REPLANNING` while waiting. Read-only investigation and plan updates can continue while approval is pending. Project implementation edits and implementation side effects require approval.
3. Record the user's approval in the plan with the revision and a chat reference or dated summary, then set `APPROVED`. Approval must be traceable to the user. A plan status, a previous revision's approval, or a request to resume does not by itself authorize implementation. Existing repository or action-specific approval requirements still apply.
4. Start only approved steps. If a material change is needed in scope, approach, or risk, log what changed, increment the revision, set `REPLANNING`, and request approval for the revised plan before continuing implementation. Keep prior approvals in the same file.

## Execute, sync, and resume

- Set `IN_PROGRESS` when starting. After each meaningful step, update its step status and record affected files, decisions, and observed results. For a blocker, set `BLOCKED` and record its cause, last completed step, and next action. Progress-only updates keep the same revision.
- On return, read the entire plan and compare its branch, HEAD, and execution record with the actual working tree and diff. Preserve unrelated changes. Reconcile discrepancies before relying on completion marks or approvals. If evidence of approval is missing or the approved work materially changed, obtain approval before resuming. Plans stay in the working tree where they were created. Ask for the original plan or working tree if recovery points elsewhere.
- Set `VERIFYING` when running checks. Record commands and observed outcomes, skipped checks with reasons, changed files, and commit or PR links if available. Set `COMPLETED` after the acceptance criteria are met and record any remaining verification gaps. Keep this plan for follow-ups on the same task.
- Re-run the parent and module Git checks before staging, committing, or publishing. Stage project files by path and inspect the staged file list. Never force-add, commit, or publish plans or copy sensitive plan contents into public artifacts. If any plan path is tracked or staged, stop and report it before further Git publication. Exclusion rules cannot remove existing Git history.
