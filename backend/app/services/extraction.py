from __future__ import annotations

import hashlib
import io
from pathlib import Path

from fastapi import UploadFile, status
from pypdf import PdfReader

from app.core.config import settings
from app.core.exceptions import AthenaError

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".md",
    ".markdown",
    ".txt",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sql",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".go",
    ".rs",
    ".cpp",
    ".hpp",
    ".java",
}


class ExtractedFile:
    def __init__(self, content: str, checksum: str, size_bytes: int) -> None:
        self.content = content
        self.checksum = checksum
        self.size_bytes = size_bytes


async def extract_upload(file: UploadFile) -> ExtractedFile:
    filename = file.filename or "upload"
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise AthenaError(
            f"Unsupported file type: {extension}", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
    data = await file.read()
    if not data:
        raise AthenaError("Uploaded file is empty")
    if len(data) > settings.max_upload_bytes:
        raise AthenaError(
            "File exceeds maximum upload size", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
    checksum = hashlib.sha256(data).hexdigest()
    if extension == ".pdf":
        content = _extract_pdf(data)
    else:
        content = _decode_text(data)
    if not content.strip():
        raise AthenaError("No searchable text could be extracted from file")
    return ExtractedFile(content=content, checksum=checksum, size_bytes=len(data))


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page.strip() for page in pages if page.strip())


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise AthenaError("Could not decode text file")
