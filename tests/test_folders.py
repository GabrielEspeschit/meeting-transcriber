import pytest

from meeting_summary.folders import (
    UNCLASSIFIED_EN,
    UNCLASSIFIED_PT_BR,
    FolderDefinition,
    discover_folders,
)


def test_discover_empty_dir(tmp_path):
    assert discover_folders(tmp_path) == []


def test_discover_skips_no_description_file(tmp_path):
    (tmp_path / "Sprint Reviews").mkdir()
    assert discover_folders(tmp_path) == []


def test_discover_skips_empty_description(tmp_path):
    subdir = tmp_path / "Sprint Reviews"
    subdir.mkdir()
    (subdir / "_folder.md").write_text("   \n", encoding="utf-8")
    assert discover_folders(tmp_path) == []


def test_discover_skips_whitespace_only_description(tmp_path):
    subdir = tmp_path / "Planejamento"
    subdir.mkdir()
    (subdir / "_folder.md").write_text("\n\n\n", encoding="utf-8")
    assert discover_folders(tmp_path) == []


def test_discover_reserved_name_pt_br(tmp_path):
    subdir = tmp_path / UNCLASSIFIED_PT_BR
    subdir.mkdir()
    (subdir / "_folder.md").write_text("Reuniões sem classificação", encoding="utf-8")
    assert discover_folders(tmp_path) == []


def test_discover_reserved_name_en(tmp_path):
    subdir = tmp_path / UNCLASSIFIED_EN
    subdir.mkdir()
    (subdir / "_folder.md").write_text("Unclassified meetings", encoding="utf-8")
    assert discover_folders(tmp_path) == []


def test_discover_reserved_name_case_insensitive(tmp_path):
    subdir = tmp_path / "NÃO CLASSIFICADO"
    subdir.mkdir()
    (subdir / "_folder.md").write_text("desc", encoding="utf-8")
    # "NÃO CLASSIFICADO".lower() == "não classificado", so it's reserved and skipped
    result = discover_folders(tmp_path)
    assert len(result) == 0


def test_discover_single_valid_folder(tmp_path):
    subdir = tmp_path / "Sprint Reviews"
    subdir.mkdir()
    (subdir / "_folder.md").write_text("Sprint review meetings", encoding="utf-8")
    result = discover_folders(tmp_path)
    assert result == [FolderDefinition(name="Sprint Reviews", description="Sprint review meetings")]


def test_discover_multiple_folders(tmp_path):
    for name, desc in [
        ("Planejamento", "Planning sessions"),
        ("Sprint Reviews", "Sprint reviews"),
        ("1:1s", "One on one meetings"),
    ]:
        subdir = tmp_path / name
        subdir.mkdir()
        (subdir / "_folder.md").write_text(desc, encoding="utf-8")

    result = discover_folders(tmp_path)
    assert len(result) == 3
    names = [f.name for f in result]
    assert "Planejamento" in names
    assert "Sprint Reviews" in names
    assert "1:1s" in names


def test_discover_sort_order(tmp_path):
    for name in ["Zebra", "Alpha", "Mango"]:
        subdir = tmp_path / name
        subdir.mkdir()
        (subdir / "_folder.md").write_text(f"Description for {name}", encoding="utf-8")

    result = discover_folders(tmp_path)
    assert [f.name for f in result] == ["Alpha", "Mango", "Zebra"]


def test_discover_ignores_files_not_dirs(tmp_path):
    (tmp_path / "some_file.txt").write_text("not a folder", encoding="utf-8")
    assert discover_folders(tmp_path) == []


def test_discover_description_stripped(tmp_path):
    subdir = tmp_path / "Sprint Reviews"
    subdir.mkdir()
    (subdir / "_folder.md").write_text("  Sprint reviews  \n", encoding="utf-8")
    result = discover_folders(tmp_path)
    assert result[0].description == "Sprint reviews"


def test_discover_ignores_subfolder_without_folder_md_alongside_valid(tmp_path):
    valid = tmp_path / "Planejamento"
    valid.mkdir()
    (valid / "_folder.md").write_text("Planning", encoding="utf-8")

    invalid = tmp_path / "SemDescricao"
    invalid.mkdir()

    result = discover_folders(tmp_path)
    assert len(result) == 1
    assert result[0].name == "Planejamento"
