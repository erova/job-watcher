import json
import os
from datetime import datetime

def run_monitor(companies, keywords, locations):
    # Simulated results
    new_jobs = []
    seen_jobs = []

    for company in companies:
        for kw in keywords:
            job = {
                "company": company,
                "title": f"{kw.title()} Designer",
                "location": "Remote",
                "url": f"https://example.com/{company}/{kw}"
            }
            if kw.lower() in ["design", "product"]:
                new_jobs.append(job)
            else:
                seen_jobs.append(job)

    log_event("run", {"companies": companies, "keywords": keywords, "locations": locations})
    return new_jobs, seen_jobs

def log_click(job):
    log_event("click", {"company": job["company"], "title": job["title"], "url": job["url"]})

def log_event(event_type, details):
    log = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
    log_file = "logs.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            logs = json.load(f)
    logs.append(log)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)