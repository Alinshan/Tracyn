import hashlib
from pathlib import Path


CHUNK_SIZE = 1024 * 1024  # 1 MB


def calculate_sha256(path: str) -> str:
    """Calculate SHA-256 hash of a file using chunked reading to avoid loading large files into memory."""
    sha256 = hashlib.sha256()
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)

    return sha256.hexdigest()


def calculate_sha256_string(content: str) -> str:
    """Calculate SHA-256 of a string (used for tamper-protecting the baseline JSON)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
