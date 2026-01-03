from apify_client import ApifyClient
import pandas as pd
import os


APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "60CQman1uPJZgcyd2"
OUTPUT_FILE = "glassdoor_reviews_apify.xlsx"

client = ApifyClient(APIFY_API_TOKEN)

run_input = {
    "company_name": "Blackcoffer",
    "item_limit": 5,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
    },
}

print("Running Glassdoor scraper ")
run = client.actor(ACTOR_ID).call(run_input=run_input)

dataset_id = run["defaultDatasetId"]
print(f"Dataset ID: {dataset_id}") 

raw_items = list(client.dataset(dataset_id).iterate_items())

if not raw_items:
    raise Exception("No data scraped. Exiting.")

rows = []

for item in raw_items:
    ratings = item.get("ratings", {}) or {}

    row = {
        "Overall rating": item.get("rating_overall"),
        "Feedback": item.get("summary"),
        "Position": item.get("job_title"),
        "Location": item.get("location"),
        "service Time": item.get("length_of_employement"),
        "Diversity and Inclusion": item.get("rating_driversity_and_inclusion"),
        "Career Opportunities": item.get("rating_career_opportunities"),
        "Culture and Values": item.get("rating_culture_and_values"),
        "Work/Life Balance": item.get("rating.work_life_balance"),
        "Senior Management": item.get("rating_senior_leadership"),
        "Compensation and Benifit": item.get("rating_compensation_and_benefits"),
        "Pros": item.get("pros"),
        "Cons": item.get("cons"),
        "Recommend": item.get("rating_recommend_to_friend"),
        "CEO Approval": item.get("rating_ceo"),
        "Bussiness Outlook": item.get("rating_business_outlook"),
        "Date": item.get("review_date_time"),
        "URL": item.get("employer_logo_url"),
    }

    rows.append(row)

df = pd.DataFrame(rows)

column_order = [
    "Overall rating", "Feedback", "Position", "service Time", "Diversity and Inclusion",
    "Career Opportunities", "Culture and Values", "Work/Life Balance", "Senior Management",
    "Compensation and Benifit", "Pros", "Cons", "Recommend", "CEO Approval", "Bussiness Outlook",
    "Date", "URL"
]

df = df[column_order]

df.to_excel(OUTPUT_FILE, index=False)
print(f"Data saved to {OUTPUT_FILE}")