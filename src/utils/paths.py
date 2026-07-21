"""Safe filesystem path helpers.

Prevent path traversal when resolving user-supplied filenames or paths
under application-controlled directories (e.g. OUTPUT_DIR).
"""

from pathlib import Path
from typing import Iterable, Union

PathLike = Union[str, Path]


def safe_filename(filename: str) -> str:
    """Return a basename-only filename, rejecting traversal attempts.

    Args:
        filename: Client-supplied file name (must not contain path separators)

    Returns:
        The sanitized basename

    Raises:
        ValueError: If the name is empty, absolute, or escapes the basename
    """
    if not filename or not filename.strip():
        raise ValueError("Filename is required")

    name = filename.strip()
    if name in (".", ".."):
        raise ValueError("Invalid filename")

    path = Path(name)
    if path.is_absolute() or path.name != name or ".." in path.parts:
        raise ValueError("Invalid filename: path separators or traversal not allowed")

    return path.name


def safe_join_under(base_dir: PathLike, filename: str) -> Path:
    """Join a basename under base_dir and ensure the result stays inside it.

    Args:
        base_dir: Allowed root directory
        filename: Basename only (no directories)

    Returns:
        Resolved Path under base_dir

    Raises:
        ValueError: If the resolved path escapes base_dir
    """
    base = Path(base_dir).resolve()
    safe_name = safe_filename(filename)
    candidate = (base / safe_name).resolve()

    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("Path escapes allowed directory") from exc

    return candidate


def resolve_under_roots(user_path: PathLike, allowed_roots: Iterable[PathLike]) -> Path:
    """Resolve a user path and require it to sit under at least one allowed root.

    Absolute paths are accepted only if they resolve under an allowed root.
    Relative paths are resolved against each root in order until one matches.

    Args:
        user_path: Client-supplied path (absolute or relative)
        allowed_roots: Directories that may contain the file

    Returns:
        Resolved Path under an allowed root

    Raises:
        ValueError: If the path is empty or outside all allowed roots
    """
    raw = str(user_path).strip() if user_path is not None else ""
    if not raw:
        raise ValueError("Path is required")

    roots = [Path(root).resolve() for root in allowed_roots]
    if not roots:
        raise ValueError("No allowed directories configured")

    given = Path(raw).expanduser()

    candidates = []
    if given.is_absolute():
        candidates.append(given.resolve())
    else:
        for root in roots:
            candidates.append((root / given).resolve())

    for candidate in candidates:
        for root in roots:
            try:
                candidate.relative_to(root)
                return candidate
            except ValueError:
                continue

    raise ValueError("Path escapes allowed directories")
