import sys
import os
import asyncio
from datetime import datetime
import uuid

# Add the backend directory to sys.path so we can import from core, database, etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo import connect_to_mongo, close_mongo_connection, get_database
from utils.dataset_parser import parse_company_csv

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "leetcode-repo")

# Basic logo mapping for popular companies
LOGO_MAPPING = {
    "amazon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "google": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
    "microsoft": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
    "adobe": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Adobe_Systems_logo_and_wordmark.svg",
    "apple": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
    "meta": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg",
    "netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "uber": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Uber_logo_2018.png",
    "salesforce": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg",
    "oracle": "https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg",
    "cisco": "https://upload.wikimedia.org/wikipedia/commons/0/08/Cisco_logo_blue_2016.svg",
    "tcs": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg",
    "infosys": "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg",
    "wipro": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Wipro_Primary_Logo_Color_RGB.svg",
    "accenture": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture_2017.svg",
    "cognizant": "https://upload.wikimedia.org/wikipedia/commons/4/43/Cognizant_logo_2022.svg",
    "zoho": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Zoho_Logo.svg"
}

async def clear_collections():
    db = get_database()
    await db["companies"].delete_many({})
    await db["technical_questions"].delete_many({})
    await db["topics"].delete_many({})
    print("Cleared existing collections.")

async def import_dataset():
    await connect_to_mongo()
    await clear_collections()
    db = get_database()
    
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset path {DATASET_PATH} does not exist. Please run 'git clone' first.")
        await close_mongo_connection()
        return

    company_dirs = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d)) and not d.startswith('.')]
    
    total_companies = len(company_dirs)
    print(f"Found {total_companies} company folders.")
    
    all_questions_to_insert = []
    
    for i, company_dir in enumerate(company_dirs):
        company_name = company_dir.replace("-", " ").title()
        
        # Read all.csv if it exists
        csv_path = os.path.join(DATASET_PATH, company_dir, "all.csv")
        if not os.path.exists(csv_path):
            continue
            
        questions = parse_company_csv(csv_path, company_name)
        
        if not questions:
            continue
            
        # Extract unique topics
        topics = list(set([q["topic"] for q in questions]))
        
        # Determine logo
        logo_url = LOGO_MAPPING.get(company_dir.lower(), None)
        if not logo_url:
            # Fallback placeholder logo
            logo_url = f"https://ui-avatars.com/api/?name={company_name}&background=random"
            
        # Create company document
        company_doc = {
            "company_name": company_name,
            "company_logo": logo_url,
            "description": f"Interview questions asked at {company_name}.",
            "total_questions": len(questions),
            "topics": topics,
            "created_at": datetime.utcnow()
        }
        
        await db["companies"].insert_one(company_doc)
        
        # Add to total questions list
        all_questions_to_insert.extend(questions)
        
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{total_companies} companies...")
            
    # Insert all questions
    if all_questions_to_insert:
        print(f"Inserting {len(all_questions_to_insert)} questions...")
        
        # Batched insert for questions
        batch_size = 5000
        for i in range(0, len(all_questions_to_insert), batch_size):
            batch = all_questions_to_insert[i:i+batch_size]
            await db["technical_questions"].insert_many(batch)
            
    print("Import complete!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(import_dataset())
