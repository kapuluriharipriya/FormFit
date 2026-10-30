"""
FORMFIT - TINYFISH INTERNSHIP RADAR

Stage 1: One agent, one careers page
Stage 2: Multiple agents running in parallel
Stage 3: Search discovers pages, agents scrape them

Commands:
python radar.py 1
python radar.py 2
python radar.py 3
"""

import asyncio
import json
import os
import sys
from datetime import datetime

from tinyfish import TinyFish, AsyncTinyFish, RunStatus


# =====================================================
# CONFIGURATION
# =====================================================

if not os.getenv("TINYFISH_API_KEY"):
    sys.exit(
        "ERROR: TINYFISH_API_KEY is missing. "
        "Configure it in your terminal first."
    )

GOAL = """
Find internship opportunities suitable for college students.

Prefer these fields:
- Software Development
- Python Development
- Artificial Intelligence
- Machine Learning
- Data Science
- Web Development

For every opportunity extract:
1. Internship title
2. Company name
3. Location
4. Remote or on-site status
5. Required skills
6. Eligibility criteria
7. Stipend
8. Application deadline
9. Duration
10. Official application link

Only return opportunities that appear to be genuine internship listings.
Do not invent missing information. Use "Not specified" when unavailable.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "internships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "remote": {"type": "boolean"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "eligibility": {"type": "string"},
                    "stipend": {"type": "string"},
                    "deadline": {"type": "string"},
                    "duration": {"type": "string"},
                    "apply_link": {"type": "string"}
                },
                "required": [
                    "title",
                    "company",
                    "location",
                    "remote",
                    "skills",
                    "eligibility",
                    "stipend",
                    "deadline",
                    "duration",
                    "apply_link"
                ]
            }
        }
    },
    "required": ["internships"]
}


# =====================================================
# CAREER WEBSITES
# =====================================================

PAGES = {
    "Jane Street":
        "https://www.janestreet.com/join-jane-street/open-roles/",

    "Google":
        "https://www.google.com/about/careers/applications/jobs/results/?q=intern",

    "Microsoft":
        "https://jobs.careers.microsoft.com/global/en/search?q=intern",

    "Razorpay":
        "https://razorpay.com/jobs/"
}


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def print_header(title):
    print("\n" + "=" * 55)
    print(f"       FORMFIT - {title}")
    print("=" * 55 + "\n")


def extract_items(result):
    if isinstance(result, dict):
        return result.get("internships", [])

    return []


def save_results(rows):

    # Remove duplicate listings based on company and title.
    unique = {}

    for row in rows:
        title = row.get("title", "").strip().lower()
        company = row.get("company", "").strip().lower()

        if title and title != "not specified":
            unique[(title, company)] = row

    rows = list(unique.values())

    rows.sort(
        key=lambda item: not item.get("remote", False)
    )

    with open("internships.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "project": "FormFit",
                "last_updated": datetime.now().isoformat(),
                "total_opportunities": len(rows),
                "internships": rows
            },
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nINTERNSHIP RESULTS\n")

    for index, item in enumerate(rows, start=1):
        remote = "REMOTE" if item.get("remote") else "ON-SITE"

        print(
            f"{index}. {item.get('title', 'Unknown')}\n"
            f"   Company: {item.get('company', 'Unknown')}\n"
            f"   Location: {item.get('location', 'Unknown')}\n"
            f"   Mode: {remote}\n"
            f"   Deadline: {item.get('deadline', 'Unknown')}\n"
            f"   Apply: {item.get('apply_link', 'Unknown')}\n"
        )

    print("-" * 55)
    print(f"Total opportunities: {len(rows)}")
    print("Saved successfully to internships.json")


# =====================================================
# STAGE 1 - SINGLE AGENT
# =====================================================

def stage1():

    print_header("STAGE 1 - SINGLE AGENT")

    client = TinyFish()

    url = PAGES["Jane Street"]

    print("Website:", url)
    print("\nStarting TinyFish agent...\n")

    try:
        run = client.agent.run(
            url=url,
            goal=GOAL,
            output_schema=SCHEMA
        )

        print("Agent Status:", run.status)

        if run.status == RunStatus.COMPLETED:

            print("\nEXTRACTED DATA:\n")

            print(
                json.dumps(
                    run.result,
                    indent=4,
                    ensure_ascii=False
                )
            )

            rows = extract_items(run.result)

            for row in rows:
                row["source"] = "Jane Street"

            save_results(rows)

        else:
            print("Agent did not complete successfully.")

    except Exception as error:
        print("Stage 1 Error:", str(error))


# =====================================================
# STAGE 2 - PARALLEL AGENTS
# =====================================================

async def scrape_pages(pages):

    agents = AsyncTinyFish()

    tasks = [
        agents.agent.run(
            url=url,
            goal=GOAL,
            output_schema=SCHEMA
        )
        for url in pages.values()
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    rows = []

    for (company, url), run in zip(pages.items(), results):

        if isinstance(run, Exception):
            print(f"ERROR - {company}: {run}")
            continue

        print(f"{company}: {run.status}")

        if run.status != RunStatus.COMPLETED:
            continue

        items = extract_items(run.result)

        for item in items:
            item["source"] = company
            rows.append(item)

    return rows


def stage2():

    print_header("STAGE 2 - PARALLEL AGENTS")

    print("Starting agents on multiple career websites...\n")

    try:
        rows = asyncio.run(scrape_pages(PAGES))
        save_results(rows)

    except Exception as error:
        print("Stage 2 Error:", str(error))


# =====================================================
# STAGE 3 - SEARCH + AGENTS
# =====================================================

def stage3():

    print_header("STAGE 3 - SEARCH AND DISCOVERY")

    client = TinyFish()

    print("Searching for internship opportunities...\n")

    try:

        hits = client.search.query(
            query="software engineering AI machine learning data science internship 2026 apply"
        )

        pages = {}

        for result in hits.results[:5]:

            url = getattr(result, "url", None)

            if url:
                pages[url] = url

        if not pages:
            print("No career pages discovered.")
            return

        print("Discovered pages:")

        for url in pages:
            print("-", url)

        print("\nStarting agents on discovered pages...\n")

        rows = asyncio.run(scrape_pages(pages))

        for row in rows:
            row["source"] = row.get("source", "Search Discovery")

        save_results(rows)

    except Exception as error:
        print("Stage 3 Error:", str(error))


# =====================================================
# MAIN PROGRAM
# =====================================================

if __name__ == "__main__":

    stages = {
        "1": stage1,
        "2": stage2,
        "3": stage3
    }

    if len(sys.argv) < 2:

        print_header("INTERNSHIP RADAR")

        print("Choose a stage:")
        print("1 - Single agent")
        print("2 - Parallel agents")
        print("3 - Search + agents")

        sys.exit(0)

    choice = sys.argv[1]

    if choice not in stages:
        print("Invalid stage. Choose 1, 2 or 3.")
        sys.exit(1)

    stages[choice]()