#!/usr/bin/env python3
"""Create and check local implementation plans in a Git working tree."""

import argparse
import re
import subprocess
from pathlib import Path


PLANS = Path(".ai/plans")
EXCLUDE_RULE = b"/.ai/plans/"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "implementation-plan.md"


class PlanError(Exception):
    """An unsafe or unavailable plan location."""


def git(*args, cwd=None, allowed=(0,)):
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode not in allowed:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise PlanError(f"git {args[0]} failed: {detail}")
    return result


def plan_location(task_id):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id) or len(task_id) > 80:
        raise PlanError("use a task ID of up to 80 lowercase letters, digits, and single hyphens")

    root = Path(git("rev-parse", "--show-toplevel").stdout.rstrip("\n"))
    relative = PLANS / f"{task_id}.md"
    path = root / relative
    for component in (root / ".ai", root / PLANS, path):
        if component.is_symlink():
            raise PlanError(f"refusing symlink: {component}")

    indexed = git("ls-files", "-z", "--", ":(icase).ai", cwd=root).stdout.lower()
    if any(entry in (".ai", ".ai/plans") or entry.startswith(".ai/plans/")
           for entry in indexed.split("\0")):
        raise PlanError("Git tracks or stages a plan path. Review the index before continuing.")

    return root, relative, path


def ignored(root, relative):
    result = git("check-ignore", "-q", "--", relative.as_posix(), cwd=root, allowed=(0, 1))
    return result.returncode == 0


def ensure_ignored(root, relative):
    if ignored(root, relative):
        return

    exclude = Path(git("rev-parse", "--git-path", "info/exclude", cwd=root).stdout.rstrip("\n"))
    if not exclude.is_absolute():
        exclude = root / exclude
    if exclude.parent.is_symlink() or exclude.is_symlink():
        raise PlanError(f"refusing symlink in Git exclusion path: {exclude}")
    if exclude.exists() and not exclude.is_file():
        raise PlanError(f"Git exclusion path is not a regular file: {exclude}")
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("a+b") as file:
        file.seek(0)
        contents = file.read()
        if EXCLUDE_RULE not in contents.splitlines():
            if contents and not contents.endswith(b"\n"):
                file.write(b"\n")
            file.write(EXCLUDE_RULE + b"\n")

    if not ignored(root, relative):
        raise PlanError(f"Git does not ignore {relative}. Check for overriding ignore rules.")


def run(command, task_id):
    root, relative, path = plan_location(task_id)
    if command == "init":
        if path.exists():
            raise PlanError(f"plan already exists: {path}. Resume it with check.")
        contents = TEMPLATE.read_text(encoding="utf-8").replace("{{TASK_ID}}", task_id)
        ensure_ignored(root, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as plan:
            plan.write(contents)
    else:
        if not path.is_file():
            raise PlanError(f"plan not found: {path}")
        if not ignored(root, relative):
            raise PlanError(f"Git does not ignore {relative}. Restore the local exclusion before proceeding.")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "check"))
    parser.add_argument("task_id")
    args = parser.parse_args()
    try:
        print(run(args.command, args.task_id))
    except (OSError, PlanError) as error:
        parser.exit(1, f"plan-keeper: {error}\n")


if __name__ == "__main__":
    main()
