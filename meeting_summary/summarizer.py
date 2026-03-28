import re

import anthropic

from .prompt import build_user_message, get_system_prompt


def summarize(
    transcription: str,
    model: str = "claude-sonnet-4-20250514",
    language: str = "pt-br",
    max_tokens: int = 4096,
) -> dict:
    """Envia a transcrição para o Claude e retorna o sumário estruturado.

    Returns:
        dict com "title_slug" (str) e "markdown" (str)
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        system=get_system_prompt(language),
        messages=[
            {"role": "user", "content": build_user_message(transcription)},
        ],
    )

    response_text = message.content[0].text
    return _parse_response(response_text)


def _parse_response(response_text: str) -> dict:
    """Extrai o slug e o markdown da resposta do Claude."""
    lines = response_text.strip().split("\n")

    title_slug = None
    markdown_start = 0

    for i, line in enumerate(lines):
        match = re.match(r"^MEETING_SLUG:\s*(.+)$", line.strip())
        if match:
            title_slug = match.group(1).strip()
            markdown_start = i + 1
            break

    # Remove linhas vazias entre o slug e o início do markdown
    while markdown_start < len(lines) and not lines[markdown_start].strip():
        markdown_start += 1

    markdown = "\n".join(lines[markdown_start:]).strip()

    return {
        "title_slug": title_slug,
        "markdown": markdown,
    }
