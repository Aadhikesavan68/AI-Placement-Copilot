from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import copy
from typing import List
from routers.auth import get_current_user
from schemas.user_schema import User
from schemas.resume_schema import ResumeResponse, DeleteResponse
from schemas.job_schema import JobDescriptionResponse
from services.resume_service import process_resume_upload, calculate_completion_score, process_jd_upload
from repositories.resume_repository import get_resumes_by_user, get_resume_by_id, delete_resume_by_id, update_resume_by_id
from services.resume_improvement_service import improve_resume
from services.resume_export_service import export_resume
import os

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        resume = await process_resume_upload(file, current_user.id)
        return resume
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to upload resume", "error": str(e)})

@router.get("/history", response_model=List[ResumeResponse])
async def get_history(current_user: User = Depends(get_current_user)):
    try:
        resumes = await get_resumes_by_user(current_user.id)
        for resume in resumes:
            resume["completion_score"] = calculate_completion_score(resume)
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to fetch history", "error": str(e)})

@router.get("/{id}", response_model=ResumeResponse)
async def get_resume(id: str, current_user: User = Depends(get_current_user)):
    try:
        resume = await get_resume_by_id(id, current_user.id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        resume["completion_score"] = calculate_completion_score(resume)
        return resume
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to fetch resume", "error": str(e)})

@router.post("/{id}/improve")
async def improve_uploaded_resume(id: str, current_user: User = Depends(get_current_user)):
    try:
        resume = await get_resume_by_id(id, current_user.id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        result = await improve_resume(resume)
        if not resume.get("_original_resume_data"):
            original_data = {
                field: copy.deepcopy(resume.get(field))
                for field in result["resume"]
                if field not in {"id", "user_id", "upload_date", "original_file", "resume_name"}
            }
        else:
            original_data = resume["_original_resume_data"]
        updates = {field: result["resume"].get(field) for field in result["resume"] if field not in {"id", "user_id", "upload_date", "original_file", "resume_name"}}
        updates["_original_resume_data"] = original_data
        updated_resume = await update_resume_by_id(id, current_user.id, updates)
        if not updated_resume:
            raise HTTPException(status_code=500, detail="Failed to save improved resume")
        result["resume"] = updated_resume
        result["resume"]["completion_score"] = result["completion_score"]
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to improve resume", "error": str(e)})

@router.get("/{id}/download")
async def download_resume(id: str, current_user: User = Depends(get_current_user)):
    try:
        resume = await get_resume_by_id(id, current_user.id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        output_path, filename, media_type = export_resume(resume, os.path.join("uploads", "corrected"))
        return FileResponse(output_path, media_type=media_type, filename=filename)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to generate resume download", "error": str(e)})

@router.delete("/{id}", response_model=DeleteResponse)
async def delete_resume(id: str, current_user: User = Depends(get_current_user)):
    try:
        # Get resume to find the file path
        resume = await get_resume_by_id(id, current_user.id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Delete from DB
        deleted = await delete_resume_by_id(id, current_user.id)
        if deleted:
            # Delete file
            if os.path.exists(resume["original_file"]):
                os.remove(resume["original_file"])
            return {"success": True, "message": "Resume deleted successfully"}
        else:
             raise HTTPException(status_code=500, detail="Failed to delete from database")
    except HTTPException as e:
         raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to delete resume", "error": str(e)})

@router.post("/job/upload", response_model=JobDescriptionResponse)
async def upload_job_description(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        jd = await process_jd_upload(file, current_user.id)
        return jd
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Failed to upload job description", "error": str(e)})
