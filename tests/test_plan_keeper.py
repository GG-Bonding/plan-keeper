from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plan_keeper.py"
PLAN = ".ai/plans/issue-421.md"


class PlanKeeperTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "project"
        self.root.mkdir()
        self.git("init", "-q")

    def git(self, *args, cwd=None, check=True):
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, text=True,
            capture_output=True, check=check,
        )

    def cli(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], cwd=cwd or self.root,
            text=True, capture_output=True,
        )

    def test_creation_and_recovery_use_one_local_file(self):
        nested = self.root / "src"
        nested.mkdir()
        exclude = self.root / ".git/info/exclude"
        exclude.write_bytes(b"# keep my existing local rules")
        created = self.cli("init", "issue-421", cwd=nested)
        self.assertEqual(created.returncode, 0, created.stderr)
        plan = Path(created.stdout.strip())
        self.assertEqual(plan, self.root.resolve() / PLAN)
        self.assertIn("Task ID: issue-421", plan.read_text())
        self.assertIn("Status: DRAFT", plan.read_text())

        plan.write_text("Existing execution record", encoding="utf-8")
        duplicate = self.cli("init", "issue-421")
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn("already exists", duplicate.stderr)
        recovered = self.cli("check", "issue-421")
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(recovered.stdout, created.stdout)
        self.assertEqual(plan.read_text(), "Existing execution record")
        another = self.cli("init", "issue-422")
        self.assertEqual(another.returncode, 0, another.stderr)
        self.assertNotEqual(another.stdout, created.stdout)

        self.git("add", ".")
        self.assertEqual(self.git("ls-files").stdout, "")
        self.assertEqual(exclude.read_bytes(), b"# keep my existing local rules\n/.ai/plans/\n")

    def test_override_prevents_writing_plan(self):
        (self.root / ".gitignore").write_text("!/.ai/plans/\n", encoding="utf-8")
        result = self.cli("init", "issue-421")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overriding ignore rules", result.stderr)
        self.assertFalse((self.root / PLAN).exists())

    def test_check_detects_lost_exclusion(self):
        created = self.cli("init", "issue-421")
        self.assertEqual(created.returncode, 0, created.stderr)
        (self.root / ".git/info/exclude").write_text("", encoding="utf-8")
        checked = self.cli("check", "issue-421")
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("does not ignore", checked.stderr)

    def test_force_staged_plan_blocks_creation_and_recovery(self):
        created = self.cli("init", "issue-421")
        self.assertEqual(created.returncode, 0, created.stderr)
        self.git("add", "-f", "--", PLAN)
        for command, task_id in (("init", "issue-422"), ("check", "issue-421")):
            with self.subTest(command=command):
                result = self.cli(command, task_id)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("tracks or stages", result.stderr)

    def test_module_record_is_ignored_and_force_staging_blocks_recovery(self):
        created = self.cli("init", "issue-421")
        self.assertEqual(created.returncode, 0, created.stderr)

        module = ".ai/plans/issue-421/sdk.md"
        record = self.root / module
        record.parent.mkdir()
        record.write_text("Latest SDK progress", encoding="utf-8")

        self.git("check-ignore", "-q", "--", module)
        self.git("add", ".")
        self.assertEqual(self.git("ls-files").stdout, "")

        self.git("add", "-f", "--", module)
        result = self.cli("check", "issue-421")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tracks or stages", result.stderr)

    def test_case_variant_index_entry_blocks_creation(self):
        tracked = self.root / ".AI/Plans/older.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("Previously staged", encoding="utf-8")
        self.git("add", "-f", "--", ".AI/Plans/older.md")
        result = self.cli("init", "issue-421")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tracks or stages", result.stderr)

    def test_rejects_traversal_and_symlinks(self):
        invalid = self.cli("init", "../outside")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("task ID", invalid.stderr)

        outside = self.root.parent / "outside"
        outside.mkdir()
        (self.root / ".ai").symlink_to(outside, target_is_directory=True)
        result = self.cli("init", "issue-421")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_linked_worktree_uses_git_resolved_exclude(self):
        self.git("-c", "user.name=Plan Test", "-c", "user.email=plan@example.invalid",
                 "commit", "-qm", "Initialize", "--allow-empty")
        linked = self.root.parent / "linked"
        self.git("worktree", "add", "-q", "--detach", str(linked))
        result = self.cli("init", "issue-421", cwd=linked)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((linked / PLAN).is_file())
        self.assertFalse((self.root / PLAN).exists())
        self.git("add", ".", cwd=linked)
        self.assertEqual(self.git("ls-files", cwd=linked).stdout, "")
