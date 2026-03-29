import pytest

from meeting_summary.folders import FolderDefinition
from meeting_summary.prompt import build_user_message, get_system_prompt


SAMPLE_FOLDERS = [
    FolderDefinition(name="Sprint Reviews", description="Sprint review meetings"),
    FolderDefinition(name="Planejamento", description="Planning sessions"),
]


# --- get_system_prompt ---

def test_system_prompt_without_folders_is_unchanged():
    original = get_system_prompt("pt-br")
    with_none = get_system_prompt("pt-br", folders=None)
    with_empty = get_system_prompt("pt-br", folders=[])
    assert original == with_none
    assert original == with_empty


def test_system_prompt_without_folders_has_no_meeting_folder():
    prompt = get_system_prompt("pt-br")
    assert "MEETING_FOLDER" not in prompt


def test_system_prompt_with_folders_includes_meeting_folder_pt_br():
    prompt = get_system_prompt("pt-br", folders=SAMPLE_FOLDERS)
    assert "MEETING_FOLDER:" in prompt


def test_system_prompt_with_folders_includes_meeting_folder_en():
    prompt = get_system_prompt("en", folders=SAMPLE_FOLDERS)
    assert "MEETING_FOLDER:" in prompt


def test_system_prompt_with_folders_meeting_folder_after_slug():
    prompt = get_system_prompt("pt-br", folders=SAMPLE_FOLDERS)
    slug_pos = prompt.index("MEETING_SLUG:")
    folder_pos = prompt.index("MEETING_FOLDER:")
    assert folder_pos > slug_pos


def test_system_prompt_with_folders_includes_unclassified_rule_pt_br():
    prompt = get_system_prompt("pt-br", folders=SAMPLE_FOLDERS)
    assert "UNCLASSIFIED" in prompt


def test_system_prompt_with_folders_includes_unclassified_rule_en():
    prompt = get_system_prompt("en", folders=SAMPLE_FOLDERS)
    assert "UNCLASSIFIED" in prompt


def test_system_prompt_with_folders_includes_no_contamination_rule_pt_br():
    prompt = get_system_prompt("pt-br", folders=SAMPLE_FOLDERS)
    assert "não incluir" in prompt.lower() or "não inclua" in prompt.lower()


# --- build_user_message ---

def test_build_user_message_without_folders_backward_compat():
    original_result = (
        "Aqui está a transcrição da reunião para resumir:\n\n---\ntranscrição\n---"
    )
    assert build_user_message("transcrição") == original_result
    assert build_user_message("transcrição", folders=None) == original_result
    assert build_user_message("transcrição", folders=[]) == original_result


def test_build_user_message_with_folders_includes_folder_names():
    msg = build_user_message("transcrição", folders=SAMPLE_FOLDERS)
    assert "Sprint Reviews" in msg
    assert "Planejamento" in msg


def test_build_user_message_with_folders_includes_descriptions():
    msg = build_user_message("transcrição", folders=SAMPLE_FOLDERS)
    assert "Sprint review meetings" in msg
    assert "Planning sessions" in msg


def test_build_user_message_folders_outside_transcription_markers():
    transcription = "this is the transcript"
    msg = build_user_message(transcription, folders=SAMPLE_FOLDERS)
    closing_marker_pos = msg.index("---", msg.index("---") + 3)  # second ---
    folders_pos = msg.index("Sprint Reviews")
    assert folders_pos > closing_marker_pos


def test_build_user_message_transcription_unchanged_with_folders():
    transcription = "Speaker A: hello\nSpeaker B: world"
    msg = build_user_message(transcription, folders=SAMPLE_FOLDERS)
    assert transcription in msg
