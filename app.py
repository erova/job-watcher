import streamlit as st
from group_loader import load_all_groups, load_company_group
from job_monitor import run_monitor, log_click
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from collections import Counter

load_dotenv()
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>Job Watcher Agent</h1>", unsafe_allow_html=True)

all_groups = load_all_groups()
group_names = list(all_groups.keys())

st.sidebar.subheader("Step 1: Choose Company Groups")
selected_groups = st.sidebar.multiselect("Select groups to monitor", group_names, default=group_names)

companies = []
for group in selected_groups:
    companies.extend(load_company_group(group))

st.sidebar.subheader("Step 2: Filters")
keywords = st.sidebar.text_input("Filter by keywords (comma-separated)", "design, product").split(",")
keywords = [k.strip() for k in keywords if k.strip()]
locations = st.sidebar.text_input("Filter by locations (comma-separated)", "remote, new york").split(",")
locations = [l.strip() for l in locations if l.strip()]

st.sidebar.subheader("Step 3: Subscribe to Email Alerts")
email = st.sidebar.text_input("Your email address")
if email and st.sidebar.button("Subscribe"):
    sub = {
        "email": email,
        "groups": selected_groups,
        "keywords": keywords,
        "locations": locations,
        "subscribed_at": datetime.utcnow().isoformat()
    }
    if os.path.exists("subscribers.json"):
        with open("subscribers.json", "r") as f:
            subs = json.load(f)
    else:
        subs = []

    if email not in [s["email"] for s in subs]:
        subs.append(sub)
        with open("subscribers.json", "w") as f:
            json.dump(subs, f, indent=2)
        st.sidebar.success("Subscribed successfully!")
    else:
        st.sidebar.info("You're already subscribed.")

if st.button("▶️ Run Agent"):
    if not companies:
        st.warning("Please select at least one company group.")
    else:
        with st.spinner("Scanning job boards..."):
            new_jobs, seen_jobs = run_monitor(companies, keywords, locations)

        st.subheader(f"🆕 New Matches ({len(new_jobs)})")
        if new_jobs:
            for job in new_jobs:
                st.markdown(f"- **{job['company']}** — [{job['title']}]({job['url']}) ({job['location']})", unsafe_allow_html=True)
        else:
            st.info("No new matches found.")

        st.subheader(f"📁 Previously Seen Jobs ({len(seen_jobs)})")
        for job in seen_jobs:
            st.markdown(f"- **{job['company']}** — [{job['title']}]({job['url']}) ({job['location']})", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 Admin Dashboard")

if os.path.exists("logs.json"):
    with open("logs.json") as f:
        logs = json.load(f)

    runs = [l for l in logs if l["type"] == "run"]
    clicks = [l for l in logs if l["type"] == "click"]

    st.markdown(f"**Total Searches Run:** {len(runs)}  \n**Total Job Link Clicks:** {len(clicks)}")

**Total Job Link Clicks:** {len(clicks)}")

    top_companies = Counter(c["details"].get("company") for c in clicks if "company" in c["details"])
    if top_companies:
        st.markdown("**Top Clicked Companies:**")
        for name, count in top_companies.most_common(5):
            st.markdown(f"- {name}: {count} clicks")

    st.markdown("**Full Activity Log:**")
    st.json(logs[-20:])
else:
    st.info("No logs yet.")