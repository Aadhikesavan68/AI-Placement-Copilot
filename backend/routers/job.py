from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, Body
from typing import List, Optional
from routers.auth import get_current_user
from schemas.user_schema import User
from schemas.job_schema import (
    JobDescriptionResponse,
    JobUploadTextRequest,
    DeleteJobResponse
)
from services.jd_service import (
    process_jd_file_upload,
    process_jd_text_upload,
    get_latest_jd,
    get_jd_history,
    delete_jd
)

router = APIRouter()

@router.post("/upload", response_model=JobDescriptionResponse)
async def upload_job_description(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse a Job Description.
    Supports:
    - File upload (PDF, DOCX, TXT) via multipart/form-data
    - Form fields (text, title) via multipart/form-data or application/x-www-form-urlencoded
    - JSON payload ({ "text": "...", "title": "..." }) via application/json
    """
    try:
        content_type = request.headers.get("content-type", "")

        # 1. If JSON payload
        if "application/json" in content_type:
            try:
                body = await request.json()
                jd_text = body.get("text") or body.get("job_description") or body.get("jd_text")
                jd_title = body.get("title") or body.get("jd_name") or body.get("job_title")
                if not jd_text or not jd_text.strip():
                    raise HTTPException(status_code=400, detail="Job description text is required")
                jd_doc = await process_jd_text_upload(jd_text, jd_title, current_user.id)
                return jd_doc
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        # 2. If File provided in multipart
        if file and file.filename:
            jd_doc = await process_jd_file_upload(file, current_user.id)
            return jd_doc

        # 3. If Text provided in form-data
        if text and text.strip():
            jd_doc = await process_jd_text_upload(text, title, current_user.id)
            return jd_doc

        raise HTTPException(
            status_code=400,
            detail="Must provide either a file (PDF, DOCX, TXT) or raw job description text."
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Failed to process job description", "error": str(e)}
        )


@router.get("/latest", response_model=Optional[JobDescriptionResponse])
async def get_latest_job(current_user: User = Depends(get_current_user)):
    """Fetches the latest job description for the current user."""
    try:
        jd = await get_latest_jd(current_user.id)
        return jd
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Failed to fetch latest job description", "error": str(e)}
        )


@router.get("/history", response_model=List[JobDescriptionResponse])
async def get_history(current_user: User = Depends(get_current_user)):
    """Fetches full job description upload history for the current user."""
    try:
        return await get_jd_history(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Failed to fetch job description history", "error": str(e)}
        )


@router.delete("/{id}", response_model=DeleteJobResponse)
async def delete_job_description(id: str, current_user: User = Depends(get_current_user)):
    """Deletes a job description by ID."""
    try:
        deleted = await delete_jd(id, current_user.id)
        if deleted:
            return {"success": True, "message": "Job description deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete job description from database")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Failed to delete job description", "error": str(e)}
        )
