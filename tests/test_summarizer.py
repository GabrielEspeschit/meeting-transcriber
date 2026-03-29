import pytest

from meeting_summary.summarizer import _parse_response


def test_parse_response_basic():
    response = "MEETING_SLUG: sprint-review\n\n# Meeting Title\nContent here"
    result = _parse_response(response)
    assert result["title_slug"] == "sprint-review"
    assert result["meeting_folder"] is None
    assert "# Meeting Title" in result["markdown"]


def test_parse_response_with_folder():
    response = (
        "MEETING_SLUG: sprint-review\n"
        "MEETING_FOLDER: Sprint Reviews\n"
        "\n"
        "# Meeting Title\nContent here"
    )
    result = _parse_response(response)
    assert result["title_slug"] == "sprint-review"
    assert result["meeting_folder"] == "Sprint Reviews"
    assert result["markdown"].startswith("# Meeting Title")


def test_parse_response_without_folder():
    response = "MEETING_SLUG: planning-q2\n\n# Q2 Planning\nSome content"
    result = _parse_response(response)
    assert result["meeting_folder"] is None


def test_parse_response_folder_unclassified():
    response = (
        "MEETING_SLUG: random-meeting\n"
        "MEETING_FOLDER: UNCLASSIFIED\n"
        "\n"
        "# Random Meeting\nContent"
    )
    result = _parse_response(response)
    assert result["meeting_folder"] == "UNCLASSIFIED"


def test_parse_response_folder_whitespace():
    response = (
        "MEETING_SLUG: some-slug\n"
        "MEETING_FOLDER:   Sprint Reviews   \n"
        "\n"
        "# Title\nContent"
    )
    result = _parse_response(response)
    assert result["meeting_folder"] == "Sprint Reviews"


def test_parse_response_markdown_not_contaminated_by_folder():
    response = (
        "MEETING_SLUG: test-slug\n"
        "MEETING_FOLDER: Planejamento\n"
        "\n"
        "# Title\n**Participants:** Ana, Bruno"
    )
    result = _parse_response(response)
    assert "MEETING_FOLDER" not in result["markdown"]
    assert "MEETING_SLUG" not in result["markdown"]


def test_parse_response_no_slug():
    response = "# Just a meeting title\nSome content"
    result = _parse_response(response)
    assert result["title_slug"] is None
    assert result["meeting_folder"] is None
    assert "# Just a meeting title" in result["markdown"]


def test_parse_response_folder_stops_at_non_folder_line():
    # If the line after MEETING_SLUG is not MEETING_FOLDER (and not empty),
    # meeting_folder should remain None
    response = "MEETING_SLUG: test-slug\n# Title directly\nContent"
    result = _parse_response(response)
    assert result["meeting_folder"] is None
    assert result["markdown"].startswith("# Title directly")


def test_parse_response_multiple_blank_lines_between_metadata_and_markdown():
    response = (
        "MEETING_SLUG: test-slug\n"
        "MEETING_FOLDER: Sprint Reviews\n"
        "\n"
        "\n"
        "# Title\nContent"
    )
    result = _parse_response(response)
    assert result["markdown"].startswith("# Title")
