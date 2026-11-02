import os
import shutil
from fastapi import UploadFile, HTTPException
from utils.resume_parser import parse_resume
from repositories.resume_repository import create_resume
from schemas.resume_schema import ResumeCreate

UPLOAD_DIR = "uploads"

async def process_resume_upload(file: UploadFile, user_id: str):
    # Validate Extension
    allowed_extensions = {".pdf", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")

    # Save File
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    # Check File Size (<10MB)
    if os.path.getsize(file_path) > 10 * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    # Parse Resume
    try:
        parsed_data = parse_resume(file_path)
    except Exception as e:
        # In a real scenario, we might still save the raw file, but for now we fail
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {e}")
        
    # Store in Database
    resume_create = ResumeCreate(
        resume_name=file.filename,
        user_id=user_id,
        original_file=file_path,
        **parsed_data
    )
    
    saved_resume = await create_resume(resume_create.model_dump())
    from repositories.skill_assessment_repository import upsert_candidate_skills
    from services.skill_assessment_service import extract_candidate_skills
    await upsert_candidate_skills(user_id, extract_candidate_skills(saved_resume))
    
    # Calculate completion score
    score = calculate_completion_score(saved_resume)
    saved_resume["completion_score"] = score
    
    return saved_resume

def calculate_completion_score(resume_data: dict) -> int:
    fields_to_check = [
        "name", "email", "phone", "college", "degree", "skills",
        "projects", "education", "experience", "certifications",
        "linkedin", "github", "portfolio", "achievements", "languages"
    ]
    filled = 0
    for field in fields_to_check:
        val = resume_data.get(field)
        if val and val != "Not Found":
            if isinstance(val, list) and len(val) > 0:
                filled += 1
            elif isinstance(val, str) and len(val.strip()) > 0:
                filled += 1
    total = len(fields_to_check)
    return max(10, int((filled / total) * 100))

async def process_jd_upload(file: UploadFile, user_id: str):
    from utils.resume_parser import extract_text_from_pdf, extract_text_from_docx
    from services.ats_service import parse_job_description_text
    from database.mongo import get_database
    import uuid
    from datetime import datetime

    allowed_extensions = {".pdf", ".docx", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX and TXT are supported.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_jd_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save job description file: {e}")
        
    if file_ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read TXT: {e}")

    try:
        parsed_data = parse_job_description_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job description: {e}")
        
    db = get_database()
    jd_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "jd_name": file.filename,
        "jd_text": text,
        "extracted_data": parsed_data,
        "upload_date": datetime.utcnow()
    }
    await db["job_descriptions"].insert_one(jd_doc)
    if "_id" in jd_doc:
        del jd_doc["_id"]
        
    return jd_doc
