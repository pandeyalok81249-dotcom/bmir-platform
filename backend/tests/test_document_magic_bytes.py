import pytest
from httpx import AsyncClient
from app.services.document_parser import DocumentParser


def test_magic_byte_validation_direct():
    # Valid PDF magic bytes
    valid_pdf_bytes = b"%PDF-1.4\n%some binary data\n"
    ok, msg = DocumentParser.validate_document_content(valid_pdf_bytes, "pdf")
    assert ok is True

    # Spoofed PDF (plain text content with .pdf extension)
    spoofed_pdf_bytes = b"This is just plain text masquerading as a PDF file."
    ok, msg = DocumentParser.validate_document_content(spoofed_pdf_bytes, "pdf")
    assert ok is False
    assert "missing %PDF- header" in msg

    # Spoofed DOCX (plain text with .docx extension)
    spoofed_docx_bytes = b"Fake docx file without zip header."
    ok, msg = DocumentParser.validate_document_content(spoofed_docx_bytes, "docx")
    assert ok is False
    assert "invalid zip container signature" in msg

    # Binary text file with null bytes
    binary_txt = b"Hello\x00\x00World binary content"
    ok, msg = DocumentParser.validate_document_content(binary_txt, "txt")
    assert ok is False
    assert "raw binary data" in msg


@pytest.mark.asyncio
async def test_spoofed_pdf_upload_rejection(client: AsyncClient, auth_headers: dict):
    # Upload a fake PDF that lacks the %PDF- magic bytes
    fake_pdf = b"Hello, I am pretending to be a PDF file."
    files = {"file": ("malicious_resume.pdf", fake_pdf, "application/pdf")}
    resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert resp.status_code == 422
    assert "missing %PDF- header" in resp.json()["error"]["message"]

