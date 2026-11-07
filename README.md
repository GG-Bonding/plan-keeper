# Plan Keeper

Plan Keeper is an Agent Skill for keeping the implementation plan, approval history, and progress for a development task in one local Markdown file.

## Install

For personal use across Codex projects, clone the repository into your user skills directory.

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/GG-Bonding/plan-keeper.git ~/.agents/skills/plan-keeper
```

For project-scoped use, place the skill folder under `.agents/skills/` in the project. For another Agent Skills-compatible client, use that client's skill directory and invocation syntax. The helper requires Git and Python 3 and uses the Python standard library.

## Use in Codex

Start with a task and, if available, a stable issue ID.

> Use $plan-keeper to plan the Redis timeout fix for issue 421. Use task ID `issue-421` and show me the plan for approval.

The agent creates `.ai/plans/issue-421.md`, fills out the implementation plan, and asks you to approve its current revision. After approval, it updates that file as work progresses. Material changes go back through approval in the same file.

To resume in another session, open the original project working tree and say:

> Use $plan-keeper to resume `.ai/plans/issue-421.md`.

The agent checks the plan against the branch, working tree, and approval record. A new clone or a separate worktree has its own plan files. Keep a private copy if you need recovery after losing the working tree.

## Git protection

On creation, the helper checks for tracked or staged plan paths. If needed, it adds `/.ai/plans/` to the repository's local Git exclusion file, resolved via Git so linked worktrees work. Shared ignore rules can override the local rule. The helper refuses to create or validate a plan if Git would consider it for normal staging.

The helper's `check` command validates the local path and Git status without writing. If the rule was lost, use `git rev-parse --git-path info/exclude` from the project root to locate the local exclusion file and restore `/.ai/plans/`, then rerun `check`. Approval, scope discipline, and progress updates are handled by the agent workflow. A force-add bypasses Git ignores, and ignore rules do not remove a path from history. Stage project files by path and review the index before committing or publishing.

## Run the tests

```sh
python3 -B -m unittest discover -s tests -v
```

The tests run the helper against temporary Git repositories and a linked worktree.
