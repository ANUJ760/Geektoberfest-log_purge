import os
import time

from log_purge import cli

DAY = 86_400


def make_old(path, age_days=40):
    path.write_text("data")
    t = time.time() - age_days * DAY
    os.utime(path, (t, t))
    return path


def test_dry_run_deletes_nothing(tmp_path, capsys):
    f = make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--dry-run"]) == 0
    assert f.exists()
    assert "Would delete 1" in capsys.readouterr().out


def test_yes_deletes(tmp_path):
    f = make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--yes"]) == 0
    assert not f.exists()


def test_prompt_declined_keeps_files(tmp_path, monkeypatch):
    f = make_old(tmp_path / "a.log")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert cli.main([str(tmp_path), "-d", "30"]) == 0
    assert f.exists()


def test_prompt_accepted_deletes(tmp_path, monkeypatch):
    f = make_old(tmp_path / "a.log")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert cli.main([str(tmp_path), "-d", "30"]) == 0
    assert not f.exists()


def test_non_interactive_without_yes_is_refused(tmp_path, monkeypatch):
    f = make_old(tmp_path / "a.log")
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert cli.main([str(tmp_path), "-d", "30"]) == 2
    assert f.exists()


def test_bad_directory_and_root(tmp_path):
    assert cli.main([str(tmp_path / "nope"), "-d", "1"]) == 2
    assert cli.main([os.path.abspath(os.sep), "-d", "1", "--yes"]) == 2


def test_quiet_mode_deletes_silently(tmp_path, capsys):
    f = make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--yes", "--quiet"]) == 0
    assert not f.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_quiet_mode_short_flag(tmp_path, capsys):
    f = make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--yes", "-q"]) == 0
    assert not f.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_quiet_mode_dry_run(tmp_path, capsys):
    f = make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--dry-run", "-q"]) == 0
    assert f.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_quiet_mode_nothing_to_delete(tmp_path, capsys):
    assert cli.main([str(tmp_path), "-d", "30", "-q"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_quiet_mode_errors_still_printed(tmp_path, capsys):
    assert cli.main([str(tmp_path / "nope"), "-d", "1", "-q"]) == 2
    captured = capsys.readouterr()
    assert "error: not a directory" in captured.err


def test_quiet_mode_deletion_failures_printed_to_stderr(tmp_path, capsys, monkeypatch):
    make_old(tmp_path / "a.log")

    def fake_unlink(self):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("pathlib.Path.unlink", fake_unlink)
    assert cli.main([str(tmp_path), "-d", "30", "--yes", "-q"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "could not be deleted" in captured.err


def test_log_file_records_deletions(tmp_path):
    import re

    f1 = make_old(tmp_path / "a.log")
    f2 = make_old(tmp_path / "b.log")
    log_file = tmp_path / "audit.log"

    assert cli.main([str(tmp_path), "-d", "30", "--yes", "--log-file", str(log_file)]) == 0
    assert not f1.exists()
    assert not f2.exists()
    assert log_file.exists()

    content = log_file.read_text()
    lines = content.strip().splitlines()
    assert len(lines) == 3

    iso_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z "
    assert re.search(iso_regex + r"DELETED .*a\.log \d+ bytes", lines[0])
    assert re.search(iso_regex + r"DELETED .*b\.log \d+ bytes", lines[1])
    assert re.search(iso_regex + r"SUMMARY Deleted 2 file\(s\), freed \d+ bytes", lines[2])


def test_log_file_appends_across_runs(tmp_path):
    log_file = tmp_path / "audit.log"

    make_old(tmp_path / "a.log")
    assert cli.main([str(tmp_path), "-d", "30", "--yes", "--log-file", str(log_file)]) == 0

    make_old(tmp_path / "b.log")
    assert cli.main([str(tmp_path), "-d", "30", "--yes", "--log-file", str(log_file)]) == 0

    content = log_file.read_text()
    assert "DELETED " in content
    assert content.count("SUMMARY") == 2
    assert "a.log" in content
    assert "b.log" in content


def test_log_file_dry_run_records_would_delete(tmp_path):
    f = make_old(tmp_path / "a.log")
    log_file = tmp_path / "audit.log"

    assert cli.main([str(tmp_path), "-d", "30", "--dry-run", "--log-file", str(log_file)]) == 0
    assert f.exists()
    content = log_file.read_text()
    assert "WOULD_DELETE " in content
    assert "a.log" in content
    assert "[dry-run]" in content


def test_unwritable_log_path_fails_safely(tmp_path, capsys):
    f = make_old(tmp_path / "a.log")
    dir_as_file = tmp_path / "dir_log"
    dir_as_file.mkdir()

    assert cli.main([str(tmp_path), "-d", "30", "--yes", "--log-file", str(dir_as_file)]) == 2
    assert f.exists()  # Nothing deleted!
    captured = capsys.readouterr()
    assert "error: cannot write to log file" in captured.err

