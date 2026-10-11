import os
import time

import pytest

from log_purge.purger import delete_files, find_old_files

DAY = 86_400


def make_file(path, age_days, content="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    t = time.time() - age_days * DAY
    os.utime(path, (t, t))
    return path


def test_finds_only_old_files(tmp_path):
    old = make_file(tmp_path / "old.log", 40)
    make_file(tmp_path / "new.log", 5)
    found = find_old_files(tmp_path, days=30)
    assert [c.path for c in found] == [old]


def test_recursive_and_non_recursive(tmp_path):
    top = make_file(tmp_path / "a.log", 40)
    nested = make_file(tmp_path / "sub" / "b.log", 40)
    assert {c.path for c in find_old_files(tmp_path, 30)} == {top, nested}
    assert {c.path for c in find_old_files(tmp_path, 30, recursive=False)} == {top}


def test_pattern_filter(tmp_path):
    log_file = make_file(tmp_path / "a.log", 40)
    make_file(tmp_path / "keep.txt", 40)
    assert [c.path for c in find_old_files(tmp_path, 30, "*.log")] == [log_file]


def test_symlinks_are_skipped(tmp_path):
    target = make_file(tmp_path / "outside" / "t.log", 40)
    root = tmp_path / "root"
    root.mkdir()
    try:
        (root / "link.log").symlink_to(target)
    except OSError:
        pytest.skip("symlinks not supported")
    assert find_old_files(root, 30) == []


def test_delete_files_counts_and_frees(tmp_path):
    make_file(tmp_path / "a.log", 40, "hello")
    make_file(tmp_path / "b.log", 40, "world!")
    result = delete_files(find_old_files(tmp_path, 30))
    assert result.deleted == 2
    assert result.freed_bytes == 11
    assert not result.failures
    assert list(tmp_path.iterdir()) == []


def test_delete_failure_does_not_stop_run(tmp_path):
    a = make_file(tmp_path / "a.log", 40)
    b = make_file(tmp_path / "b.log", 40)
    candidates = find_old_files(tmp_path, 30)
    a.unlink()  # vanishes before deletion -> FileNotFoundError
    result = delete_files(candidates)
    assert result.deleted == 1 and len(result.failures) == 1
    assert not b.exists()


def test_invalid_inputs(tmp_path):
    with pytest.raises(ValueError):
        find_old_files(tmp_path, -1)
    with pytest.raises(NotADirectoryError):
        find_old_files(tmp_path / "missing", 1)


def test_exclude_filter(tmp_path):
    log_file = make_file(tmp_path / "app.log", 40)
    keep_file = make_file(tmp_path / "app.keep", 40)
    bak_file = make_file(tmp_path / "app.bak", 40)

    # single string exclude
    assert [c.path for c in find_old_files(tmp_path, 30, exclude="*.keep")] == [bak_file, log_file]

    # list exclude
    assert [c.path for c in find_old_files(tmp_path, 30, exclude=["*.keep", "*.bak"])] == [log_file]

    # recursive exclude
    nested_keep = make_file(tmp_path / "sub" / "nested.keep", 40)
    assert keep_file not in [c.path for c in find_old_files(tmp_path, 30, exclude="*.keep")]
    assert nested_keep not in [c.path for c in find_old_files(tmp_path, 30, exclude="*.keep")]

