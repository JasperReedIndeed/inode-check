import importlib.util
import contextlib
import io
from unittest import mock
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "inode-check.py"


class InodeCheckTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
        self.addCleanup(shutil.rmtree, self.dir)

    def run_cli(self, *paths):
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, paths)],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_two_separate_files_are_distinct(self):
        a = Path(self.dir) / "a"
        b = Path(self.dir) / "b"
        a.mkdir()
        b.mkdir()
        code, out = self.run_cli(a, b)
        self.assertEqual(code, 0, out)

    def test_hard_linked_database_reports_same_file(self):
        a = Path(self.dir) / "alpha.sqlite"
        b = Path(self.dir) / "beta.sqlite"
        a.write_text("x")
        os.link(a, b)
        code, out = self.run_cli(a, b)
        self.assertEqual(code, 1)
        self.assertIn("SAME FILE", out)

    def test_nested_directory_reports_nested(self):
        outer = Path(self.dir) / "outer"
        inner = outer / "inner"
        inner.mkdir(parents=True)
        code, out = self.run_cli(outer, inner)
        self.assertEqual(code, 1)
        self.assertIn("NESTED", out)

    def test_symlink_to_same_directory_is_caught(self):
        real = Path(self.dir) / "real"
        real.mkdir()
        link = Path(self.dir) / "alias"
        link.symlink_to(real, target_is_directory=True)
        code, out = self.run_cli(real, link)
        self.assertEqual(code, 1, out)

    def test_missing_path_is_an_error_not_a_pass(self):
        code, out = self.run_cli(Path(self.dir) / "nope", self.dir)
        self.assertEqual(code, 2)
        self.assertIn("cannot stat", out)

    def test_invalid_path_returns_safe_error(self):
        spec=importlib.util.spec_from_file_location('inodecheck_bad',SCRIPT)
        assert spec is not None and spec.loader is not None
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        err=io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(module.main(['BAD_SECRET\x00',self.dir]),2)
        self.assertNotIn('BAD_SECRET',err.getvalue())

    def test_content_open_calls_are_forbidden(self):
        target=Path(self.dir)/'secret.sqlite';target.write_text('DO-NOT-READ')
        spec=importlib.util.spec_from_file_location('inodecheck_noopen',SCRIPT)
        assert spec is not None and spec.loader is not None
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with mock.patch('builtins.open',side_effect=AssertionError('content read')),mock.patch('os.open',side_effect=AssertionError('content read')),mock.patch.object(Path,'open',side_effect=AssertionError('content read')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(module.main([str(target),self.dir]),1)

    def test_never_opens_file_contents(self):
        target = Path(self.dir) / "secret.sqlite"
        target.write_text("DO-NOT-READ")
        os.chmod(target, 0o000)
        try:
            code, out = self.run_cli(target, self.dir)
            self.assertIn(code, (0, 1), out)
        finally:
            os.chmod(target, 0o600)


if __name__ == "__main__":
    unittest.main()
