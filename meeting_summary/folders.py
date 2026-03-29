from dataclasses import dataclass
from pathlib import Path

UNCLASSIFIED_PT_BR = "Não classificado"
UNCLASSIFIED_EN = "Unclassified"
FOLDER_DESCRIPTION_FILE = "_folder.md"


@dataclass(frozen=True)
class FolderDefinition:
    name: str
    description: str


def discover_folders(output_dir: Path) -> list:
    """Scan output_dir subdirectories for _folder.md files.

    Returns a list of FolderDefinitions for each subfolder that contains
    a _folder.md. Subfolders without _folder.md are silently ignored.
    Reserved names ("Não classificado", "Unclassified") are also skipped.
    """
    folders = []
    reserved = {UNCLASSIFIED_PT_BR.lower(), UNCLASSIFIED_EN.lower()}
    for subdir in sorted(output_dir.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name.lower() in reserved:
            continue
        desc_file = subdir / FOLDER_DESCRIPTION_FILE
        if not desc_file.exists():
            continue
        description = desc_file.read_text(encoding="utf-8").strip()
        if description:
            folders.append(FolderDefinition(name=subdir.name, description=description))
    return folders
