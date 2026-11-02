import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from repositories.resume_repository import get_resume_by_id
from routers.auth import get_current_user
from schemas.user_schema import User
from services.resume_export_service import export_corrected_pdf
from services.resume_grammar_service import (
    analyze_resume_upload,
    correction_to_resume,
    get_correction,
    update_corrections,
    _public_record,
)

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    return await analyze_resume_upload(file, current_user.id)


@router.post("/{correction_id}/review")
async def review_corrections(correction_id: str, payload: dict, current_user: User = Depends(get_current_user)):
    corrections = payload.get("corrections")
    if not isinstance(corrections, list):
        raise HTTPException(status_code=400, detail="corrections must be a list")
    record = await update_corrections(correction_id, current_user.id, corrections)
    return _public_record(record)


@router.post("/{correction_id}/generate-pdf")
async def generate_corrected_pdf(correction_id: str, current_user: User = Depends(get_current_user)):
    record = await get_correction(correction_id, current_user.id)
    resume = correction_to_resume(record)
    output_path, filename, media_type = export_corrected_pdf(resume, os.path.join("uploads", "grammar", "corrected"))
    return FileResponse(output_path, media_type=media_type, filename=filename)


@router.get("/history")
async def correction_history(current_user: User = Depends(get_current_user)):
    from database.mongo import get_database
    records = await get_database()["resume_corrections"].find({"user_id": current_user.id}).sort("created_at", -1).to_list(50)
    return [_public_record(record) for record in records]