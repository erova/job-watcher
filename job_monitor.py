import requests
import json
from datetime import datetime

def fetch_greenhouse_jobs(company_slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return data.get("jobs", [])
    except Exception as e:
        print(f"[ERROR] Greenhouse fetch failed for {company_slug}: {e}")
        return []

def fetch_lever_jobs(company_slug):
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[ERROR] Lever fetch failed for {company_slug}: {e}")
        return []

def log_event(file, new_data):
    try:
        with open(file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(new_data)
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def log_click(details):
    log_event("clicks.json", {
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    })

def log_run(query):
    log_event("runs.json", {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query
    })

def run_monitor(companies, keywords, locations):
    matches = []
    for company in companies:
        source = company.get("source")
        slug = company.get("slug")
        jobs = []
        if source == "greenhouse":
            jobs = fetch_greenhouse_jobs(slug)
        elif source == "lever":
            jobs = fetch_lever_jobs(slug)
        else:
            continue

        for job in jobs:
            title = job.get("title", "").lower()
            location = job.get("location", "").lower() if "location" in job else job.get("categories", {}).get("location", "").lower()
            if any(k.lower() in title for k in keywords) and any(l.lower() in location for l in locations):
                matches.append({
                    "title": job["title"],
                    "location": location.title(),
                    "url": job.get("absolute_url") or job.get("applyUrl"),
                    "company": company.get("name")
                })
    return matches