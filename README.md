<div align="center">

# Plan Keeper

**One development task. One plan you can approve, update, and resume.**

A local-first Agent Skill for writing reviewable technical designs and keeping decisions, approvals, and verification in one Git-ignored Markdown plan.

[Quickstart](#quickstart) · [Workflow](#workflow) · [Contributing](#contributing) · [简体中文](README.zh-CN.md)

</div>

## Why Plan Keeper?

When a coding task spans multiple sessions, the agent needs to know what you approved, what has already changed, and which checks actually ran. Plan Keeper gives that work a stable home at `.ai/plans/<task-id>.md` in your Git working tree.

- **Review before coding.** Get a plan with acceptance criteria, scope, implementation steps, risks, and verification.
- **Keep scope changes visible.** Material changes create a new revision in the same file and require fresh approval.
- **Resume from the record.** The agent checks the saved plan against the branch, HEAD, and working tree before continuing.
- **Keep plans out of normal staging.** A local Git exclusion protects the plan without editing the project's shared `.gitignore`.

## Technical design format

The [UTF-8 Markdown template](assets/implementation-plan.md) opens with a review summary and records scope, evidence, and design trade-offs. Use focused Mermaid flowcharts or sequence diagrams for key behavior, then tie short code diffs to acceptance checks. Larger tasks can link to [module design records](assets/module-record.md).

## Quickstart

You need Git and Python 3.7 or later. The helper uses the Python standard library.

### 1. Install the skill

For personal use across Codex projects, clone it into your user skills directory.

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/GG-Bonding/plan-keeper.git ~/.agents/skills/plan-keeper
```

For project-scoped use, place the skill folder under `.agents/skills/` in that project. For another Agent Skills-compatible client, use its skill directory and invocation syntax.

### 2. Plan a task and approve the revision

Open a Git project in Codex and try this prompt.

> Use $plan-keeper to plan the Redis timeout fix for issue 421. Use task ID `issue-421` and show me the plan for approval.

Review `.ai/plans/issue-421.md`. When the current revision is ready, explicitly approve it.

> I approve revision 1 of `.ai/plans/issue-421.md`. Implement the approved scope and record the verification results.

### 3. Resume in a later session

Open the original working tree and ask Codex to resume.

> Use $plan-keeper to resume `.ai/plans/issue-421.md`.

## Workflow

| Phase | What the plan records |
| --- | --- |
| `DRAFT` | Current behavior, acceptance criteria, scope, steps, and proposed checks. |
| `APPROVED` → `IN_PROGRESS` | Approval tied to the current revision, completed steps, and decisions. |
| `BLOCKED` or `REPLANNING` | What stopped progress or changed materially, and the next action. A revised scope needs fresh approval. |
| `VERIFYING` → `COMPLETED` | Commands run, observed results, remaining gaps, and any delivery links. |

The [skill instructions](SKILL.md) define the approval and execution workflow. The [implementation plan template](assets/implementation-plan.md) defines the record. The helper provides `init <task-id>` and `check <task-id>` for plan creation and Git safety checks.

## Backfill an existing implementation

Use the same plan path when code already exists. The agent inspects the current code, relevant commits, and available test evidence. It records implemented behavior, verified results, and remaining work separately. A documentation-only backfill can proceed without a new implementation approval. Any proposed follow-up code change goes through the plan approval workflow.

> Use $plan-keeper to backfill issue 421 from the existing SDK and business interaction code. Record what is verified and what still needs work.

## Split one task into module records

Keep one parent plan and link a separate document for each module.

```text
.ai/plans/
├── issue-421.md
└── issue-421/
    ├── sdk.md
    └── business-interaction.md
```

The parent owns shared scope, approvals, and acceptance criteria. Module records hold the latest local progress and verification, so you can open the SDK or business interaction record directly. Resume through the parent and follow its module links. Module records follow the same local Git protection as the parent. See the [module record template](assets/module-record.md).

## Local storage and Git

- Plans stay in the working tree where they were created. A separate clone or worktree has its own plan files.
- When needed, the helper adds `/.ai/plans/` to the Git-resolved `info/exclude` file. It rejects tracked or staged plan paths and checks whether the target path is ignored.
- Shared ignore rules can override the local rule, and a force-add can bypass it. If the local rule was removed, run `git rev-parse --git-path info/exclude` from the project root, restore the rule in that file, and rerun the helper's `check` command.
- Approval and scope checks are agent workflow rules. The helper checks local storage and Git state.

## Contributing

Open an [issue](https://github.com/GG-Bonding/plan-keeper/issues/new) with the expected behavior, what happened, and a minimal way to reproduce it. Use sanitized examples in public issues and pull requests.

Run the test suite from the repository root before submitting a change.

```sh
python3 -B -m unittest discover -s tests -v
```

The tests use temporary Git repositories and cover duplicate plans, session recovery, ignore overrides, staged files, and linked worktrees.
