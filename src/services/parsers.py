from fastapi import status, HTTPException
from io import BytesIO
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import re


def validate_empty_input(
    text: str
) -> None:
    pattern = r"^\s*$"

    if re.match(pattern=pattern, string=text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is empty"
        )


def extract_pdf(content: bytes) -> str:
    pdf = PdfReader(BytesIO(content))

    text = []

    for page in pdf.pages:
        extracted = page.extract_text()

        if extracted:
            text.append(extracted)

    return "\n".join(text)


def extract_docx(content: bytes) -> str:
    doc = Document(BytesIO(content))

    return "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )


def extract_html(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")

    return soup.get_text(separator="\n")


def extract_txt(content: bytes) -> str:
    return content.decode("utf-8")


def extract_text(filename: str, content: bytes) -> str:
    ext = filename.split(".")[-1].lower()

    text = ""

    if ext == "pdf":
        text = extract_pdf(content)
    if ext == "docx":
        text = extract_docx(content)
    if ext in ["html", "htm"]:
        text = extract_html(content)
    if ext == "txt":
        text = extract_txt(content)

    validate_empty_input(text=text)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=f"{ext} is unaprocessable"
    )
