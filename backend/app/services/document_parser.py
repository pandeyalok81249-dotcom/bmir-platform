import io
import re
from typing import Dict, List, Tuple
import docx
import pypdf

# Common standard section title triggers
SECTION_PATTERNS = {
    "summary": r"^(professional\s+summary|summary|profile|about\s+me|objective)",
    "experience": r"^(work\s+experience|professional\s+experience|experience|employment\s+history)",
    "education": r"^(education|academic\s+background|qualifications)",
    "skills": r"^(skills|technical\s+skills|core\s+competencies|technologies)",
    "projects": r"^(projects|personal\s+projects|selected\s+work)",
    "certifications": r"^(certifications|licenses|accreditations)",
}


class DocumentParser:
    @staticmethod
    def validate_document_content(content: bytes, file_ext: str) -> Tuple[bool, str]:
        """
        Validates document magic numbers and structure to prevent extension spoofing.
        """
        ext = file_ext.lower().strip(".")
        if ext == "pdf":
            # PDF magic number %PDF- within first 1024 bytes
            if not (b"%PDF-" in content[:1024]):
                return False, "File does not appear to be a valid PDF document (missing %PDF- header)."
        elif ext in ["docx", "doc"]:
            # DOCX is a zip archive with magic bytes PK\x03\x04
            if not content.startswith(b"PK\x03\x04"):
                return False, "File does not appear to be a valid DOCX document (invalid zip container signature)."
        elif ext in ["txt", "text"]:
            # Check for binary/null bytes
            if b"\x00" in content[:1024]:
                return False, "Text file appears to contain raw binary data or unprintable characters."
        else:
            return False, f"Unsupported file extension: .{ext}. Only PDF, DOCX, and TXT are supported."

        return True, "Valid document format."

    @staticmethod
    def extract_text(file_bytes: bytes, file_type: str) -> str:
        clean_ext = file_type.lower().strip(".").strip()

        # Validate magic numbers first
        valid, msg = DocumentParser.validate_document_content(file_bytes, clean_ext)
        if not valid:
            raise ValueError(msg)

        if clean_ext == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                extracted_pages = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        extracted_pages.append(text)
                return "\n".join(extracted_pages).strip()
            except Exception as e:
                raise ValueError(f"Could not parse PDF document: {str(e)}")

        elif clean_ext in ["docx", "doc"]:
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return "\n".join(paragraphs).strip()
            except Exception as e:
                raise ValueError(f"Could not parse DOCX document: {str(e)}")

        elif clean_ext in ["txt", "text"]:
            try:
                return file_bytes.decode("utf-8", errors="replace").strip()
            except Exception as e:
                raise ValueError(f"Could not decode text file: {str(e)}")

        else:
            raise ValueError(f"Unsupported document format: {clean_ext}. Use PDF, DOCX, or TXT.")

    @staticmethod
    def assess_extraction_quality(extracted_text: str) -> Tuple[bool, str]:
        if not extracted_text or len(extracted_text.strip()) < 50:
            return False, "Document contains insufficient or empty text. If this is a scanned PDF, please provide an OCR-rendered document."

        word_count = len(extracted_text.split())
        if word_count < 20:
            return False, f"Document only contains {word_count} words, which is below the minimum required for resume intelligence."

        return True, "Valid text extraction."

    @staticmethod
    def segment_sections(text: str) -> Dict[str, str]:
        lines = text.splitlines()
        sections: Dict[str, List[str]] = {"header": []}
        current_section = "header"

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if this line is a section header (short line matching header pattern)
            matched_section = None
            if len(line_stripped.split()) <= 4:
                lower_line = line_stripped.lower()
                for sec_key, pattern in SECTION_PATTERNS.items():
                    if re.match(pattern, lower_line):
                        matched_section = sec_key
                        break

            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line_stripped)

        return {k: "\n".join(v) for k, v in sections.items() if v}
