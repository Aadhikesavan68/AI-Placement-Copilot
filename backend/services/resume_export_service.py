import re
import math
import textwrap
from pathlib import Path

import fitz
from docx import Document
from utils.resume_parser import parse_resume


EDITABLE_FIELDS = [
    "summary", "skills", "languages_prog", "frameworks", "databases", "cloud",
    "tools", "soft_skills", "education", "projects", "experience", "internships",
    "certifications", "achievements", "languages", "technologies",
]

STRUCTURED_SECTIONS = [
    ("summary", "OBJECTIVE", False),
    ("education", "EDUCATION", True),
    ("skills", "TECHNICAL SKILLS", True),
    ("experience", "INTERNSHIP EXPERIENCE", True),
    ("projects", "PROJECTS", True),
    ("certifications", "CERTIFICATIONS", True),
    ("achievements", "ACHIEVEMENTS", True),
]


def _safe_stem(resume: dict) -> str:
    name = resume.get("name") or resume.get("resume_name") or "candidate_resume"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("._") or "candidate_resume"


def _replacement_pairs(resume: dict) -> list[tuple[str, str]]:
    explicit = resume.get("_text_replacements")
    if explicit:
        return sorted(set((str(before), str(after)) for before, after in explicit if before and before != after), key=lambda pair: len(pair[0]), reverse=True)
    original = resume.get("_original_resume_data")
    if not original and resume.get("original_file"):
        original = parse_resume(str(resume["original_file"]))
    original = original or resume
    pairs = []
    for field in EDITABLE_FIELDS:
        before = original.get(field)
        after = resume.get(field)
        if isinstance(before, list) and isinstance(after, list):
            for old, new in zip(before, after):
                if isinstance(old, str) and isinstance(new, str) and old != new and old.strip():
                    pairs.append((old, new))
        elif isinstance(before, str) and isinstance(after, str) and before != after and before.strip():
            pairs.append((before, after))
    return sorted(set(pairs), key=lambda pair: len(pair[0]), reverse=True)


def _replace_text(text: str, pairs: list[tuple[str, str]]) -> str:
    for before, after in pairs:
        text = text.replace(before, after)
    return text


def _replace_docx_runs(container, pairs: list[tuple[str, str]]) -> None:
    for paragraph in container.paragraphs:
        for run in paragraph.runs:
            run.text = _replace_text(run.text, pairs)
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                _replace_docx_runs(cell, pairs)


def _build_docx(source_path: str, output_path: Path, pairs: list[tuple[str, str]]) -> None:
    document = Document(source_path)
    _replace_docx_runs(document, pairs)
    document.save(output_path)


def _field_values(resume: dict, field: str) -> list[str]:
    value = resume.get(field)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip() and str(item) != "Not Found"]
    if isinstance(value, str) and value.strip() and value != "Not Found":
        return [value.strip()]
    return []


def _with_source_text(resume: dict, source_path: Path) -> dict:
    if resume.get("_raw_resume_text"):
        return resume
    if source_path.suffix.lower() == ".pdf":
        document = fitz.open(source_path)
        text = "\n".join(page.get_text("text") for page in document)
        document.close()
    elif source_path.suffix.lower() == ".docx":
        document = Document(source_path)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        text = ""
    if text.strip():
        resume = dict(resume)
        resume["_raw_resume_text"] = _replace_text(text, _replacement_pairs(resume))
    return resume


def _build_structured_pdf(resume: dict, output_path: Path) -> None:
    document = fitz.open()
    page = document.new_page()
    margin = 40
    y = margin
    usable_width = page.rect.width - (margin * 2)

    def write(text: str, size: float = 8.5, bold: bool = False, gap: float = 1.5, align: int = 0) -> None:
        nonlocal page, y
        characters_per_line = max(1, int(usable_width / max(size * 0.48, 1)))
        font = "hebo" if bold else "helv"
        lines = []
        for line in text.splitlines() or [""]:
            lines.extend(textwrap.wrap(line, width=characters_per_line, break_long_words=False) or [""])
        line_height = size * 1.08
        for line in lines:
            if y + line_height > page.rect.height - margin:
                page = document.new_page()
                y = margin
            width = fitz.get_text_length(line, fontname=font, fontsize=size)
            if align == 1:
                x = margin + max(0, (usable_width - width) / 2)
            elif align == 2:
                x = margin + max(0, usable_width - width)
            else:
                x = margin
            page.insert_text((x, y + size), line, fontsize=size, fontname=font)
            y += line_height
        if not lines:
            page = document.new_page()
            y = margin
        y += gap

    def header(title: str) -> None:
        nonlocal y
        write(title, 9.5, True, 1)
        page.draw_line((margin, y), (margin + usable_width, y), color=(0, 0, 0), width=0.55)
        y += 3

    def item(value: str, bold: bool = False) -> None:
        write(value, 8.2, bold, 0.8)

    def bullet(value: str) -> None:
        write("• " + value, 8.1, False, 0.7)

    raw_text = resume.get("_raw_resume_text")
    if isinstance(raw_text, str) and raw_text.strip():
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        section_names = {"OBJECTIVE", "SUMMARY", "EDUCATION", "TECHNICAL SKILLS", "SKILLS", "INTERNSHIP", "INTERNSHIP EXPERIENCE", "EXPERIENCE", "PROJECTS", "CERTIFICATIONS", "ACHIEVEMENTS", "AWARDS"}
        name_line = lines.pop(0) if lines else "Candidate Resume"
        write(name_line.upper(), 16, True, 1, 1)
        if lines:
            contact_line = lines.pop(0)
            write(contact_line, 7, False, 5, 1)
        for line in lines:
            normalized = re.sub(r"[:\s]+$", "", line).upper()
            if normalized in section_names:
                header(normalized)
            elif line.startswith(("•", "-", "*")):
                bullet(re.sub(r"^[•*\-]\s*", "", line))
            elif re.match(r"^(Project|Tech Stack|Programming|Core Subjects|Web Development|Databases|Machine Learning|Tools and Technologies):", line, re.IGNORECASE):
                item(line, line.lower().startswith("project:"))
            else:
                item(line)
        document.save(output_path)
        document.close()
        return

    name = str(resume.get("name") or "Candidate Resume")
    if name in {"Candidate Name", "Tamil Nadu", "Not Found"}:
        filename_name = Path(str(resume.get("resume_name", ""))).stem
        filename_name = re.sub(r"^[^_]+_", "", filename_name)
        name = re.sub(r"\s+(Resume|CV|Final.*)$", "", filename_name, flags=re.IGNORECASE).strip() or name
    write(name.upper(), 16, True, 1, 1)
    contact = " | ".join(str(resume.get(field)) for field in ("location", "email", "phone", "github", "linkedin") if resume.get(field) and resume.get(field) != "Not Found")
    if contact:
        write(contact, 7, False, 5, 1)

    summary = _field_values(resume, "summary")
    if summary:
        header("OBJECTIVE")
        item(" ".join(summary))

    education = _field_values(resume, "education")
    if education:
        header("EDUCATION")
        for index, value in enumerate(education):
            if re.search(r"\b20\d{2}\b", value) or value.strip().startswith(("-", "–")):
                write(value, 8, False, 0.5, 2)
            elif index == 0 or re.search(r"degree|school|college|higher|secondary|b\.tech", value, re.IGNORECASE):
                item(value, True)
            else:
                item(value)

    skills = _field_values(resume, "skills")
    skill_groups = [
        ("Programming Language", _field_values(resume, "languages_prog")),
        ("Core Subjects", _field_values(resume, "soft_skills")),
        ("Web Development", _field_values(resume, "frameworks")),
        ("Databases", _field_values(resume, "databases")),
        ("Machine Learning", _field_values(resume, "technologies")),
        ("Tools and Technologies", _field_values(resume, "tools")),
    ]
    if skills or any(values for _, values in skill_groups):
        header("TECHNICAL SKILLS")
        rendered = False
        for label, values in skill_groups:
            if values:
                item(f"{label}: " + ", ".join(dict.fromkeys(values)))
                rendered = True
        if not rendered:
            item("Technical Skills: " + ", ".join(dict.fromkeys(skills)))

    for field, title in (("experience", "INTERNSHIP EXPERIENCE"), ("projects", "PROJECTS")):
        values = _field_values(resume, field)
        if not values:
            continue
        header(title)
        for index, value in enumerate(values):
            if index == 0 or (index > 0 and not value.endswith(".") and not value.lower().startswith(("project:", "tech stack:"))):
                item(value, True)
            elif value.lower().startswith("tech stack:"):
                item(value, False)
            else:
                bullet(value)

    for field, title in (("certifications", "CERTIFICATIONS"), ("achievements", "ACHIEVEMENTS")):
        values = _field_values(resume, field)
        if values:
            header(title)
            for value in values:
                bullet(value)
    document.save(output_path)
    document.close()


def _build_pdf(source_path: str, output_path: Path, pairs: list[tuple[str, str]]) -> int:
    document = fitz.open(source_path)
    if not any(page.get_text().strip() for page in document):
        document.close()
        return 0
    replacements_count = 0
    for page in document:
        replacements = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    old_text = span.get("text", "")
                    new_text = _replace_text(old_text, pairs)
                    if new_text != old_text:
                        replacements.append((span, new_text))

        for span, _ in replacements:
            page.add_redact_annot(fitz.Rect(span["bbox"]), fill=(1, 1, 1))
        page.apply_redactions()
        replacements_count += len(replacements)
        for span, new_text in replacements:
            rect = fitz.Rect(span["bbox"])
            color = span.get("color", 0)
            rgb = (((color >> 16) & 255) / 255, ((color >> 8) & 255) / 255, (color & 255) / 255)
            page.insert_text((rect.x0, rect.y1), new_text, fontsize=span.get("size", 10), fontname="helv", color=rgb)
    document.save(output_path)
    document.close()
    return replacements_count


def export_resume(resume: dict, output_dir: str) -> tuple[str, str, str]:
    source_path = Path(str(resume.get("original_file", "")))
    if not source_path.exists():
        raise FileNotFoundError("The uploaded resume file is no longer available")
    extension = source_path.suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise ValueError("Only PDF and DOCX resumes can be exported")
    resume = _with_source_text(resume, source_path)

    output_path = Path(output_dir) / f"{_safe_stem(resume)}_corrected{extension}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pairs = _replacement_pairs(resume)
    if extension == ".pdf":
        replacements_count = _build_pdf(str(source_path), output_path, pairs) if pairs else 0
        if not replacements_count:
            _build_structured_pdf(resume, output_path)
        media_type = "application/pdf"
    else:
        _build_docx(str(source_path), output_path, pairs)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return str(output_path), output_path.name, media_type


def export_corrected_pdf(resume: dict, output_dir: str) -> tuple[str, str, str]:
    source_path = Path(str(resume.get("original_file", "")))
    if not source_path.exists():
        raise FileNotFoundError("The uploaded resume file is no longer available")
    resume = _with_source_text(resume, source_path)
    output_path = Path(output_dir) / f"{_safe_stem(resume)}_Corrected_Resume.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pairs = _replacement_pairs(resume)
    replacements = _build_pdf(str(source_path), output_path, pairs) if source_path.suffix.lower() == ".pdf" and pairs else 0
    if not replacements:
        _build_structured_pdf(resume, output_path)
    return str(output_path), output_path.name, "application/pdf"
