from pathlib import Path

from fastapi import HTTPException, UploadFile, status

MAX_FILE_SIZE = 10485760  # 10 MB

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".html", ".htm", ".txt"}

ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain", "text/markdown"}


async def validate_upload_file(file: UploadFile) -> bytes:
    validate_filename(file.filename)
    validate_extension(file.filename)
    validate_content_type(file.content_type)

    content = await read_with_size_limit(file)

    return content


async def read_with_size_limit(file: UploadFile) -> bytes:
    size = 0
    chunks = []

    while chunk := await file.read(1024 * 1024):
        size += len(chunk)

        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File too large"
            )

        chunks.append(chunk)

    await file.seek(0)

    return b"".join(chunks)


def validate_content_type(content_type: str | None) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type"
        )


def validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension '{ext}' is not allowed",
        )


async def validate_filename(filename: str | None) -> None:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
        )

    path = Path(filename)

    if not path.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename"
        )

    if not path.suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension is required",
        )
