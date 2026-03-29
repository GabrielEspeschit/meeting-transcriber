"""Integration tests for the CLI. These mock the Claude API call."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _make_summarize_mock(slug="test-meeting", folder=None, markdown="# Title\nContent"):
    """Return a mock for meeting_summary.summarizer.summarize."""
    def mock_summarize(**kwargs):
        return {"title_slug": slug, "meeting_folder": folder, "markdown": markdown}
    return mock_summarize


def _run_cli(args, env=None):
    """Run main() with the given sys.argv args, return (exit_code, stdout, stderr)."""
    import io
    from unittest.mock import patch as _patch

    base_env = {"ANTHROPIC_API_KEY": "test-key"}
    if env:
        base_env.update(env)

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    exit_code = 0
    with _patch("sys.argv", ["meeting-summary"] + args), \
         _patch.dict("os.environ", base_env, clear=False), \
         _patch("sys.stdout", stdout_capture), \
         _patch("sys.stderr", stderr_capture):
        try:
            from meeting_summary.cli import main
            main()
        except SystemExit as e:
            exit_code = e.code or 0

    return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()


# --- Single file, no folders (backward compat) ---

def test_single_file_no_folders(tmp_path):
    txt = tmp_path / "meeting.txt"
    txt.write_text("Speaker: Hello world", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    mock = _make_summarize_mock(slug="hello-world", markdown="# Title\nContent")

    with patch("meeting_summary.cli.summarize", side_effect=mock):
        code, out, err = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0
    files = list(output_dir.glob("*.md"))
    assert len(files) == 1
    assert files[0].name.endswith("hello-world.md")


def test_single_file_output_is_flat_without_folders(tmp_path):
    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("meeting_summary.cli.summarize", side_effect=_make_summarize_mock()):
        code, _, _ = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0
    # No subfolders should be created
    subdirs = [p for p in output_dir.iterdir() if p.is_dir()]
    assert subdirs == []


# --- Multiple files, no folders ---

def test_multiple_files_no_folders(tmp_path):
    txts = []
    for i in range(3):
        f = tmp_path / f"meeting{i}.txt"
        f.write_text(f"content {i}", encoding="utf-8")
        txts.append(f)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    call_count = 0
    def mock_summarize(**kwargs):
        nonlocal call_count
        call_count += 1
        return {"title_slug": f"meeting-{call_count}", "meeting_folder": None, "markdown": "# T\nC"}

    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        code, _, _ = _run_cli(
            [str(t) for t in txts] + ["--output-dir", str(output_dir)]
        )

    assert code == 0
    assert call_count == 3
    files = list(output_dir.glob("*.md"))
    assert len(files) == 3


# --- Multiple files with folders ---

def test_multiple_files_classified_into_subfolders(tmp_path):
    planning_dir = tmp_path / "output" / "Planejamento"
    planning_dir.mkdir(parents=True)
    (planning_dir / "_folder.md").write_text("Planning sessions", encoding="utf-8")

    sprint_dir = tmp_path / "output" / "Sprint Reviews"
    sprint_dir.mkdir()
    (sprint_dir / "_folder.md").write_text("Sprint review meetings", encoding="utf-8")

    txt1 = tmp_path / "planning.txt"
    txt1.write_text("planning content", encoding="utf-8")
    txt2 = tmp_path / "sprint.txt"
    txt2.write_text("sprint content", encoding="utf-8")

    responses = [
        {"title_slug": "q2-planning", "meeting_folder": "Planejamento", "markdown": "# Q2\nContent"},
        {"title_slug": "sprint-review", "meeting_folder": "Sprint Reviews", "markdown": "# Sprint\nContent"},
    ]
    call_idx = 0
    def mock_summarize(**kwargs):
        nonlocal call_idx
        r = responses[call_idx]
        call_idx += 1
        return r

    output_dir = tmp_path / "output"
    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        code, _, _ = _run_cli(
            [str(txt1), str(txt2), "--output-dir", str(output_dir)]
        )

    assert code == 0
    planning_summaries = [f for f in planning_dir.glob("*.md") if f.name != "_folder.md"]
    sprint_summaries = [f for f in sprint_dir.glob("*.md") if f.name != "_folder.md"]
    assert len(planning_summaries) == 1
    assert len(sprint_summaries) == 1


def test_unclassified_fallback_for_unknown_folder(tmp_path):
    known_dir = tmp_path / "output" / "Planejamento"
    known_dir.mkdir(parents=True)
    (known_dir / "_folder.md").write_text("Planning", encoding="utf-8")

    txt = tmp_path / "meeting.txt"
    txt.write_text("brainstorm content", encoding="utf-8")

    def mock_summarize(**kwargs):
        return {"title_slug": "brainstorm", "meeting_folder": "UNCLASSIFIED", "markdown": "# B\nC"}

    output_dir = tmp_path / "output"
    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        code, _, _ = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0
    unclassified_dir = output_dir / "Não classificado"
    assert unclassified_dir.exists()
    assert len(list(unclassified_dir.glob("*.md"))) == 1


def test_unclassified_fallback_for_none_folder(tmp_path):
    known_dir = tmp_path / "output" / "Planejamento"
    known_dir.mkdir(parents=True)
    (known_dir / "_folder.md").write_text("Planning", encoding="utf-8")

    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")

    def mock_summarize(**kwargs):
        return {"title_slug": "test", "meeting_folder": None, "markdown": "# T\nC"}

    output_dir = tmp_path / "output"
    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        code, _, _ = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0
    unclassified_dir = output_dir / "Não classificado"
    assert unclassified_dir.exists()


def test_creates_subfolders_automatically(tmp_path):
    # _folder.md exists but the subfolder for the classified result does NOT
    # The CLI should create it via mkdir(parents=True, exist_ok=True)
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    sprint_dir = output_dir / "Sprint Reviews"
    sprint_dir.mkdir()
    (sprint_dir / "_folder.md").write_text("Sprint meetings", encoding="utf-8")

    # The meeting is classified into a folder that doesn't exist yet
    # (only "Sprint Reviews" exists, but meeting returns "Planejamento")
    # So it should fall back to "Não classificado" (which also doesn't exist yet)
    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")

    def mock_summarize(**kwargs):
        return {"title_slug": "test", "meeting_folder": "UNCLASSIFIED", "markdown": "# T\nC"}

    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        code, _, _ = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0
    assert (output_dir / "Não classificado").exists()


# --- Error handling ---

def test_one_bad_file_does_not_abort_others(tmp_path):
    good = tmp_path / "good.txt"
    good.write_text("good content", encoding="utf-8")
    bad = tmp_path / "bad.txt"  # will not exist

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("meeting_summary.cli.summarize", side_effect=_make_summarize_mock()):
        code, out, err = _run_cli(
            [str(bad), str(good), "--output-dir", str(output_dir)]
        )

    assert code == 1
    assert "bad.txt" in err
    files = list(output_dir.glob("*.md"))
    assert len(files) == 1  # good.txt was processed


def test_exit_code_zero_when_all_succeed(tmp_path):
    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("meeting_summary.cli.summarize", side_effect=_make_summarize_mock()):
        code, _, _ = _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert code == 0


def test_exit_code_one_when_some_fail(tmp_path):
    good = tmp_path / "good.txt"
    good.write_text("content", encoding="utf-8")
    missing = tmp_path / "missing.txt"
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("meeting_summary.cli.summarize", side_effect=_make_summarize_mock()):
        code, _, err = _run_cli(
            [str(good), str(missing), "--output-dir", str(output_dir)]
        )

    assert code == 1


def test_non_txt_file_skipped_with_error(tmp_path):
    pdf = tmp_path / "meeting.pdf"
    pdf.write_text("not a text file", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    code, _, err = _run_cli([str(pdf), "--output-dir", str(output_dir)])
    assert code == 1
    assert "meeting.pdf" in err


def test_empty_txt_file_skipped_with_error(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("   \n", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    code, _, err = _run_cli([str(empty), "--output-dir", str(output_dir)])
    assert code == 1
    assert "empty.txt" in err


def test_missing_output_dir_aborts_early(tmp_path):
    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")
    missing_dir = tmp_path / "nonexistent"

    code, _, err = _run_cli([str(txt), "--output-dir", str(missing_dir)])
    assert code == 1
    assert "saída" in err or "output" in err.lower() or "nonexistent" in err


def test_summarize_called_with_folders_when_present(tmp_path):
    sprint_dir = tmp_path / "output" / "Sprint Reviews"
    sprint_dir.mkdir(parents=True)
    (sprint_dir / "_folder.md").write_text("Sprint meetings", encoding="utf-8")

    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")

    captured_kwargs = {}
    def mock_summarize(**kwargs):
        captured_kwargs.update(kwargs)
        return {"title_slug": "test", "meeting_folder": "Sprint Reviews", "markdown": "# T\nC"}

    output_dir = tmp_path / "output"
    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert captured_kwargs.get("folders") is not None
    assert len(captured_kwargs["folders"]) == 1
    assert captured_kwargs["folders"][0].name == "Sprint Reviews"


def test_summarize_called_without_folders_when_none_present(tmp_path):
    txt = tmp_path / "meeting.txt"
    txt.write_text("content", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    captured_kwargs = {}
    def mock_summarize(**kwargs):
        captured_kwargs.update(kwargs)
        return {"title_slug": "test", "meeting_folder": None, "markdown": "# T\nC"}

    with patch("meeting_summary.cli.summarize", side_effect=mock_summarize):
        _run_cli([str(txt), "--output-dir", str(output_dir)])

    assert captured_kwargs.get("folders") is None
