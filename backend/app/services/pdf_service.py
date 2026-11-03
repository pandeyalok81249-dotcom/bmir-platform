import io
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class PDFGeneratorService:
    @staticmethod
    def generate_resume_pdf(resume_content: Dict[str, Any], template_name: str = "professional") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        accent_color = colors.HexColor("#0969DA") if template_name == "professional" else (
            colors.HexColor("#1A7F37") if template_name == "technical" else colors.HexColor("#1F2328")
        )

        title_style = ParagraphStyle(
            "ResumeTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=accent_color,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ResumeSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#656D76"),
            spaceAfter=12,
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=accent_color,
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "ResumeBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1F2328"),
            spaceAfter=6,
        )

        story = []

        # Name / Header
        full_name = resume_content.get("full_name") or resume_content.get("name") or "Candidate Resume"
        story.append(Paragraph(full_name, title_style))

        # Contact / Subtitle
        contact_parts = []
        if resume_content.get("email"):
            contact_parts.append(str(resume_content["email"]))
        if resume_content.get("phone"):
            contact_parts.append(str(resume_content["phone"]))
        if resume_content.get("location"):
            contact_parts.append(str(resume_content["location"]))
        if contact_parts:
            story.append(Paragraph(" • ".join(contact_parts), subtitle_style))

        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E1E4E8"), spaceAfter=10))

        # Summary
        summary = resume_content.get("summary")
        if summary:
            story.append(Paragraph("Professional Summary", section_heading))
            story.append(Paragraph(str(summary), body_style))
            story.append(Spacer(1, 8))

        # Experience
        experience = resume_content.get("experience")
        if experience:
            story.append(Paragraph("Work Experience", section_heading))
            if isinstance(experience, str):
                for p in experience.splitlines():
                    if p.strip():
                        story.append(Paragraph(p.strip(), body_style))
            elif isinstance(experience, list):
                for exp in experience:
                    if isinstance(exp, dict):
                        role = exp.get("role") or exp.get("title", "")
                        comp = exp.get("company", "")
                        dur = exp.get("duration") or exp.get("dates", "")
                        story.append(Paragraph(f"<b>{role}</b> - {comp} ({dur})", body_style))
                        desc = exp.get("description") or exp.get("bullets", [])
                        if isinstance(desc, list):
                            for b in desc:
                                story.append(Paragraph(f"• {b}", body_style))
                        elif isinstance(desc, str):
                            story.append(Paragraph(desc, body_style))
                    elif isinstance(exp, str):
                        story.append(Paragraph(f"• {exp}", body_style))
            story.append(Spacer(1, 8))

        # Skills
        skills = resume_content.get("skills")
        if skills:
            story.append(Paragraph("Skills & Competencies", section_heading))
            if isinstance(skills, list):
                story.append(Paragraph(", ".join([str(s) for s in skills]), body_style))
            else:
                story.append(Paragraph(str(skills), body_style))
            story.append(Spacer(1, 8))

        # Education
        education = resume_content.get("education")
        if education:
            story.append(Paragraph("Education", section_heading))
            if isinstance(education, list):
                for ed in education:
                    if isinstance(ed, dict):
                        inst = ed.get("institution", "")
                        deg = ed.get("degree", "")
                        story.append(Paragraph(f"<b>{deg}</b>, {inst}", body_style))
                    else:
                        story.append(Paragraph(str(ed), body_style))
            else:
                story.append(Paragraph(str(education), body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

