from repositories.company_repository import (
    get_all_companies, search_companies, get_company_by_name, 
    get_company_questions, get_company_topics, get_company_stats,
    toggle_question_bookmark, get_user_bookmarked_questions
)

async def list_companies():
    return await get_all_companies()

async def search_company(query: str):
    if not query:
        return await get_all_companies()
    return await search_companies(query)

async def get_company_details(name: str):
    return await get_company_by_name(name)

async def get_questions_for_company(name: str, skip: int = 0, limit: int = 20, difficulty: str = None, topic: str = None, user_id: str = None):
    result = await get_company_questions(name, skip, limit, difficulty, topic)
    
    # Optional: Attach bookmark status if user is logged in
    if user_id:
        bookmarks = await get_user_bookmarked_questions(user_id)
        for q in result["questions"]:
            q["bookmarked"] = q["id"] in bookmarks
            
    return result

async def get_topics_for_company(name: str):
    return await get_company_topics(name)

async def get_stats_for_company(name: str):
    return await get_company_stats(name)

async def toggle_bookmark(question_id: str, user_id: str):
    return await toggle_question_bookmark(question_id, user_id)
