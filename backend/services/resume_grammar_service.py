import copy
import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from database.mongo import get_database
from utils.resume_parser import extract_text_from_docx, extract_text_from_pdf, parse_resume

try:
    import language_tool_python
except ImportError:
    language_tool_python = None


MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
FALLBACK_REPLACEMENTS = {
    r"\brecieve\b": "receive",
    r"\bdevelopement\b": "development",
    r"\bprograming\b": "programming",
    r"\bexperiance\b": "experience",
    r"\bmanagment\b": "management",
    r"\bresponsibilites\b": "responsibilities",
    r"\bacheivements\b": "achievements",
    r"\bteh\b": "the",
}


def _clean_filename(filename: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._") or "resume"


def _extract_text(path: str, extension: str) -> str:
    if extension == ".pdf":
        return extract_text_from_pdf(path)
    return extract_text_from_docx(path)


def _fallback_corrections(text: str) -> list[dict]:
    corrections = []
    for pattern, replacement in FALLBACK_REPLACEMENTS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            before = match.group(0)
            after = replacement if before.islower() else replacement.capitalize()
            corrections.append({
                "id": str(uuid.uuid4()),
                "before": before,
                "after": after,
                "category": "spelling",
                "message": f"Replace '{before}' with '{after}'.",
                "accepted": True,
            })
    return corrections


def _languagetool_corrections(text: str) -> list[dict]:
    if not language_tool_python or not text.strip():
        return []
    tool = None
    try:
        tool = language_tool_python.LanguageTool(os.getenv("LANGUAGE_TOOL_LANGUAGE", "en-US"))
        corrections = []
        for match in tool.check(text):
            replacement = match.replacements[0] if match.replacements else None
            if not replacement or not match.context:
                continue
            before = text[match.offset:match.offset + match.error_length]
            if not before.strip() or before == replacement:
                continue
            category = "spelling" if "SPELL" in str(match.rule_id).upper() else "grammar"
            corrections.append({
                "id": str(uuid.uuid4()),
                "before": before,
                "after": replacement,
                "category": category,
                "message": match.message,
                "accepted": True,
            })
        return corrections
    except Exception:
        return []
    finally:
        if tool:
            try:
                tool.close()
            except Exception:
                pass


def _apply_corrections(text: str, corrections: list[dict]) -> str:
    corrected = text
    for correction in corrections:
        if correction.get("accepted", True):
            corrected = corrected.replace(correction["before"], correction["after"], 1)
    return corrected


async def analyze_resume_upload(file: UploadFile, user_id: str) -> dict:
    filename = _clean_filename(file.filename or "resume")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded resume is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Resume must be smaller than 10 MB.")

    correction_id = str(uuid.uuid4())
    upload_dir = Path("uploads") / "grammar" / user_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    source_path = upload_dir / f"{correction_id}_{filename}"
    source_path.write_bytes(content)

    text = _extract_text(str(source_path), extension)
    if not text.strip():
        source_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="No readable text was found. Upload a text-based PDF or DOCX file.")

    corrections = _languagetool_corrections(text)
    known = {(item["before"], item["after"]) for item in corrections}
    corrections.extend(item for item in _fallback_corrections(text) if (item["before"], item["after"]) not in known)
    analyzed = len(re.findall(r"[^.!?]+[.!?]", text)) or len([line for line in text.splitlines() if line.strip()])
    corrected_text = _apply_corrections(text, corrections)
    parsed = parse_resume(str(source_path))

    record = {
        "id": correction_id,
        "user_id": user_id,
        "original_filename": filename,
        "file_type": extension[1:],
        "source_path": str(source_path),
        "original_text": text,
        "corrected_text": corrected_text,
        "total_sentences": analyzed,
        "parsed_resume": parsed,
        "corrections": corrections,
        "created_at": __import__("datetime").datetime.utcnow(),
        "status": "review",
    }
    await get_database()["resume_corrections"].insert_one(copy.deepcopy(record))
    record.pop("_id", None)
    return _public_record(record, analyzed)


def _public_record(record: dict, analyzed: int | None = None) -> dict:
    corrections = record.get("corrections", [])
    return {
        "id": record["id"],
        "original_filename": record["original_filename"],
        "total_sentences": analyzed if analyzed is not None else record.get("total_sentences", 0),
        "grammar_issue_count": sum(item.get("category") == "grammar" for item in corrections),
        "spelling_issue_count": sum(item.get("category") == "spelling" for item in corrections),
        "corrected_sentence_count": sum(item.get("accepted", True) for item in corrections),
        "correction_summary": f"Found {len(corrections)} suggested correction(s). Review and accept the changes before downloading.",
        "original_text": record.get("original_text", ""),
        "corrected_text": record.get("corrected_text", ""),
        "corrections": corrections,
        "status": record.get("status", "review"),
    }


async def get_correction(correction_id: str, user_id: str) -> dict:
    record = await get_database()["resume_corrections"].find_one({"id": correction_id, "user_id": user_id})
    if not record:
        raise HTTPException(status_code=404, detail="Correction record not found.")
    return record


async def update_corrections(correction_id: str, user_id: str, corrections: list[dict]) -> dict:
    record = await get_correction(correction_id, user_id)
    allowed = {(item["id"], item["before"], item["after"]) for item in record.get("corrections", [])}
    clean = []
    for item in corrections:
        key = (item.get("id"), item.get("before"), item.get("after"))
        if key in allowed:
            clean.append({**item, "accepted": bool(item.get("accepted", False))})
    corrected_text = _apply_corrections(record["original_text"], clean)
    await get_database()["resume_corrections"].update_one(
        {"id": correction_id, "user_id": user_id},
        {"$set": {"corrections": clean, "corrected_text": corrected_text, "status": "review"}},
    )
    record["corrections"] = clean
    record["corrected_text"] = corrected_text
    return record


def correction_to_resume(record: dict) -> dict:
    resume = copy.deepcopy(record.get("parsed_resume", {}))
    resume["original_file"] = record["source_path"]
    resume["resume_name"] = record["original_filename"]
    resume["name"] = resume.get("name") or Path(record["original_filename"]).stem
    replacements = [
        (item["before"], item["after"])
        for item in record.get("corrections", [])
        if item.get("accepted", False)
    ]
    for field, value in list(resume.items()):
        if isinstance(value, str):
            for before, after in replacements:
                resume[field] = resume[field].replace(before, after)
        elif isinstance(value, list):
            resume[field] = [
                next((item.replace(before, after) for before, after in replacements if isinstance(item, str) and before in item), item)
                for item in value
            ]
    resume["_text_replacements"] = replacements
    resume["_raw_resume_text"] = record.get("corrected_text", "")
    return resume
