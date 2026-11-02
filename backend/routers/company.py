from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from routers.auth import get_current_user
from schemas.user_schema import User
from schemas.company_schema import CompanyResponse, CompanyStatsResponse, CompanyTopicResponse, BookmarkResponse
from schemas.question_schema import CompanyQuestionsResponse
from services.company_service import (
    list_companies, search_company, get_company_details,
    get_questions_for_company, get_topics_for_company, get_stats_for_company,
    toggle_bookmark
)

router = APIRouter()

@router.get("/all", response_model=List[CompanyResponse])
async def get_all_companies(current_user: User = Depends(get_current_user)):
    return await list_companies()

@router.get("/search", response_model=List[CompanyResponse])
async def search_companies(q: str = "", current_user: User = Depends(get_current_user)):
    return await search_company(q)

@router.get("/{company}", response_model=CompanyResponse)
async def get_company(company: str, current_user: User = Depends(get_current_user)):
    comp = await get_company_details(company)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp

@router.get("/{company}/stats", response_model=CompanyStatsResponse)
async def get_company_stats(company: str, current_user: User = Depends(get_current_user)):
    return await get_stats_for_company(company)

@router.get("/{company}/topics", response_model=List[CompanyTopicResponse])
async def get_company_topics(company: str, current_user: User = Depends(get_current_user)):
    return await get_topics_for_company(company)

@router.get("/{company}/questions", response_model=CompanyQuestionsResponse)
async def get_company_questions(
    company: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    return await get_questions_for_company(company, skip, limit, difficulty, topic, current_user.id)

@router.post("/questions/{id}/bookmark", response_model=BookmarkResponse)
async def bookmark_question(id: str, current_user: User = Depends(get_current_user)):
    bookmarked = await toggle_bookmark(id, current_user.id)
    return {"success": True, "bookmarked": bookmarked}
