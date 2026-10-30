import html
import json
from urllib.parse import quote_plus

import streamlit as st

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="FormFit | Internship Radar",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. SESSION STATE
# =====================================================

if "profile" not in st.session_state:
    st.session_state.profile = {}

if "saved" not in st.session_state:
    st.session_state.saved = []

if "applied" not in st.session_state:
    st.session_state.applied = []

if "selected_job" not in st.session_state:
    st.session_state.selected_job = 0

if "documents" not in st.session_state:
    st.session_state.documents = {
        "Updated Resume": True,
        "Cover Letter": True,
        "Academic Transcripts": False,
        "ID Proof": True,
        "Portfolio / GitHub": False,
        "Certifications": False
    }

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Home"

# Apply navigation requested by a button BEFORE creating the radio widget.
if "pending_page" in st.session_state:
    st.session_state.nav_choice = st.session_state.pending_page
    del st.session_state.pending_page


def navigate(page):
    st.session_state.pending_page = page
    st.rerun()


def esc(value):
    """Escape scraped text before putting it inside HTML."""
    return html.escape(str(value))


def merge_unique(selected, extra_text):
    """Combine chosen options with comma-separated custom ones."""
    result = list(selected)
    seen = {s.lower() for s in result}
    for part in extra_text.split(","):
        part = part.strip()
        if part and part.lower() not in seen:
            result.append(part)
            seen.add(part.lower())
    return result


# =====================================================
# 3. LOAD INTERNSHIP + JOB DATA (TinyFish JSON files)
# =====================================================

def load_listings(path, default_type):
    """Read a TinyFish JSON file. Returns None if the file is missing."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        items = data
    else:
        items = data.get("internships", data.get("jobs", []))

    listings = []
    for item in items:
        listings.append({
            "type": item.get("type", default_type),
            "title": item.get("title", "Internship"),
            "company": item.get("company", "Company"),
            "source": item.get("source", ""),
            "skills": item.get("skills", []),
            "location": item.get("location", "Not specified"),
            "work_mode": (
                "Remote" if item.get("remote", False)
                else "On-site"
            ),
            "stipend": item.get("stipend", "Not specified"),
            "deadline": item.get("deadline", "Not specified"),
            "duration": item.get("duration", "Not specified"),
            "description": item.get(
                "eligibility", "See official listing."
            ),
            "requirements": ", ".join(str(s) for s in item.get("skills", [])),
            "apply_link": item.get("apply_link", "")
        })
    return listings


jobs = []

_internships = load_listings("internships.json", "Internship")
if _internships is None:
    st.error("Internship data not found. Run radar.py first.")
else:
    jobs.extend(_internships)

# Optional: jobs.json (same format, add "type": "Job" or leave it out)
_jobs_file = load_listings("jobs.json", "Job")
if _jobs_file:
    jobs.extend(_jobs_file)

# =====================================================
# 4. CSS DESIGN
# =====================================================

st.markdown("""
<style>

/* MAIN PAGE */
.stApp {
    background-color: #F4F7F5 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #F4F7F5 !important;
}

[data-testid="stMain"] {
    background-color: #F4F7F5 !important;
}

[data-testid="stMainBlockContainer"] {
    background-color: #F4F7F5 !important;
    padding-top: 2rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #002B24 !important;
    min-width: 245px;
}

[data-testid="stSidebar"] > div {
    background-color: #002B24 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #FFFFFF !important;
}

/* HEADINGS */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #123D32;
}

/* HOME HERO */
.hero {
    background: linear-gradient(120deg, #003D34, #006354);
    padding: 42px;
    border-radius: 18px;
    min-height: 280px;
    margin-bottom: 22px;
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 43px;
    line-height: 1.2;
}

.hero p {
    color: #D8EEE5 !important;
    font-size: 16px;
}

.pink-text {
    color: #FFA398 !important;
}

/* WHITE CARDS */
.panel,
.job,
.metric {
    background: #FFFFFF;
    border: 1px solid #DFE9E3;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
}

.panel h2,
.panel h3,
.panel p,
.job h2,
.job h3,
.job p,
.metric h2,
.metric p {
    color: #173D32 !important;
}

/* METRICS */
.metric {
    text-align: center;
    min-height: 120px;
}

.metric h2 {
    color: #009B75 !important;
    margin: 8px 0;
}

/* SKILL TAGS */
.tag {
    display: inline-block;
    background: #DDF5EA;
    color: #00664F;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
    margin: 3px;
}

/* MATCH SCORE */
.score {
    color: #009B75 !important;
    font-size: 27px;
    font-weight: bold;
}

/* BUTTONS */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #F49B91 !important;
    color: #18372D !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    min-height: 40px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #FFB5AA !important;
    color: #18372D !important;
}

/* FORM INPUTS */
.stTextInput input,
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #173D32 !important;
    border: 1px solid #C9D9D0 !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #173D32 !important;
}

/* PROGRESS */
.stProgress > div > div > div {
    background-color: #009B75 !important;
}

/* DIVIDERS */
hr {
    border-color: #DCE8E1 !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def metric_card(icon, value, label):
    st.markdown(f"""
    <div class="metric">
        <div style="font-size:25px">{icon}</div>
        <h2>{value}</h2>
        <p>{label}</p>
    </div>
    """, unsafe_allow_html=True)


def skill_hits(job):
    """Profile skills that appear anywhere in the job's skill text."""
    profile_skills = st.session_state.profile.get("skills", [])
    job_text = " ".join(str(s) for s in job["skills"]).lower()
    return [s for s in profile_skills if s.lower() in job_text]


def calculate_match(job):
    profile_skills = st.session_state.profile.get("skills", [])
    if not profile_skills or not job["skills"]:
        return 0
    return round(len(skill_hits(job)) / len(profile_skills) * 100)


def linkedin_url(kind):
    """Personalised LinkedIn search link (opens LinkedIn itself)."""
    profile = st.session_state.profile
    terms = profile.get("interests", []) or profile.get("skills", [])[:2]
    keywords = " ".join(terms) if terms else kind
    if kind == "Internship":
        keywords = f"{keywords} intern"
    location = profile.get("location", "India")
    url = (
        "https://www.linkedin.com/jobs/search/?keywords="
        + quote_plus(keywords)
        + "&location=" + quote_plus(location)
    )
    if kind == "Internship":
        url += "&f_E=1"  # LinkedIn's "Internship" experience filter
    return url


def show_job_card(job, index):
    tags = "".join(
        f'<span class="tag">{esc(skill)}</span>'
        for skill in job["skills"]
    )

    match = calculate_match(job)

    st.markdown(f"""
    <div class="job">
        <h3>💼 {esc(job['title'])}</h3>
        <b>{esc(job['company'])}</b>
        <br><br>
        {tags}
        <br><br>
        📍 {esc(job['location'])} | {esc(job['work_mode'])}
        <br><br>
        💰 {esc(job['stipend'])}
        <br>
        📅 Deadline: {esc(job['deadline'])}
        <br><br>
        <span class="score">{match}%</span>
        <b> Skills Match</b>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "View Details",
            key=f"view_{index}",
            use_container_width=True
        ):
            st.session_state.selected_job = index
            navigate("Opportunity Details")

    with col2:
        if st.button(
            "☆ Save",
            key=f"save_{index}",
            use_container_width=True
        ):
            if job["title"] not in st.session_state.saved:
                st.session_state.saved.append(job["title"])

            st.toast("Saved successfully!")


def render_listing_page(kind):
    """Shared page for 'Internship' and 'Job' listings."""
    plural = "Internships" if kind == "Internship" else "Jobs"
    items = [(i, j) for i, j in enumerate(jobs) if j["type"] == kind]

    st.title(
        "Top Matching Opportunities" if kind == "Internship"
        else "Job Opportunities"
    )
    st.caption(f"{plural} matched with your student profile.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("💼", len(items), f"{plural} Found")

    with c2:
        metric_card("⭐", len([
            j for _, j in items if calculate_match(j) >= 70
        ]), "Highly Relevant")

    with c3:
        metric_card("➤", len(st.session_state.applied), "Applied")

    with c4:
        metric_card("🏠", len([
            j for _, j in items if j["work_mode"] == "Remote"
        ]), "Remote Friendly")

    if not st.session_state.profile:
        st.warning("Please create your profile first.")
        if st.button("Create Profile", key=f"cp_{kind}"):
            navigate("My Profile")
        return

    st.link_button(
        f"🔗 Search {plural} on LinkedIn ↗",
        linkedin_url(kind),
        use_container_width=True
    )

    if not items:
        st.info(
            f"No {plural.lower()} loaded yet from our TinyFish sources. "
            f"Use the LinkedIn button above, or add a "
            f"{'jobs.json' if kind == 'Job' else 'internships.json'} "
            "file to show them here."
        )
        return

    search = st.text_input(
        f"🔍 Search {plural.lower()}...",
        key=f"search_{kind}"
    )

    sort_option = st.selectbox(
        "Sort By",
        ["Highest Match", "Company Name"],
        key=f"sort_{kind}"
    )

    filtered = [
        (i, job) for i, job in items
        if search.lower() in (
            job["title"] + " " + job["company"]
        ).lower()
    ]

    if sort_option == "Highest Match":
        filtered.sort(key=lambda x: calculate_match(x[1]), reverse=True)
    else:
        filtered.sort(key=lambda x: x[1]["company"])

    if filtered:
        for index, job in filtered:
            show_job_card(job, index)
    else:
        st.info(f"No matching {plural.lower()} found.")


# =====================================================
# 6. SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:

    st.markdown("""
    <h1 style="color:white !important;">🎯 FormFit</h1>
    <p style="color:#A7DDC8 !important;">
        YOUR INTERNSHIP RADAR
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Home",
            "My Profile",
            "Find Internships",
            "Job Opportunities",
            "Opportunity Details",
            "Readiness Check",
            "Saved",
            "Dashboard",
            "About"
        ],
        key="nav_choice"
    )

    st.divider()

    st.markdown("""
    <p style="color:#A7DDC8 !important;">
        AI-POWERED STUDENT OPPORTUNITIES
    </p>
    <p style="color:white !important;">
        Discover • Verify • Prepare • Apply
    </p>
    """, unsafe_allow_html=True)

# One-time message carried over from the previous page (e.g. profile saved)
if "flash" in st.session_state:
    flash_kind, flash_msg = st.session_state.pop("flash")
    if flash_kind == "success":
        st.success(flash_msg)
    else:
        st.error(flash_msg)


# =====================================================
# 7. HOME PAGE
# =====================================================

if page == "Home":

    st.markdown("""
    <div class="hero">
        <p>AI AGENT • STUDENT OPPORTUNITIES</p>
        <h1>
            Find Opportunities.<br>
            <span class="pink-text">Verify Your Fit.</span><br>
            Apply with Confidence.
        </h1>
        <p>
            An AI-powered platform that finds internships,
            checks your eligibility and helps you prepare
            before you apply.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Get Started →", use_container_width=True):
        navigate("My Profile")

    st.subheader("Your Internship Journey")

    cols = st.columns(4)

    features = [
        ("🔎", "Discover", "Find internships across multiple sites."),
        ("🛡️", "Verify", "Check eligibility and skill fit."),
        ("📄", "Prepare", "Check required application documents."),
        ("➤", "Apply", "Apply with confidence.")
    ]

    for col, item in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="panel">
                <h2>{item[0]}</h2>
                <h3>{item[1]}</h3>
                <p>{item[2]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.info("Create your student profile to discover matching internships.")


# =====================================================
# 8. STUDENT PROFILE
# =====================================================

elif page == "My Profile":

    st.title("Create Your Profile")
    st.write("Tell us about yourself to find the best opportunities.")

    profile = st.session_state.profile

    looking_options = ["Internship", "Job"]
    year_options = ["1st Year", "2nd Year", "3rd Year",
                    "4th Year", "Graduate"]
    branch_options = [
        "Computer Science and Engineering",
        "AI & ML",
        "Information Technology",
        "ECE",
        "Other"
    ]
    experience_options = [
        "Beginner (0 - 1 year)",
        "Intermediate (1 - 2 years)",
        "Experienced (2+ years)"
    ]
    base_skills = [
        "Python", "Java", "C", "C++", "SQL",
        "Machine Learning", "AI", "Deep Learning",
        "HTML", "CSS", "JavaScript", "React",
        "Data Analysis", "Statistics", "Django", "Cloud",
        "Git", "Excel"
    ]
    base_roles = [
        "AI/ML",
        "Data Science",
        "Software Development",
        "Web Development",
        "Research",
        "Quantitative Finance",
        "Cybersecurity",
        "Product / Design"
    ]

    # Keep any custom values the student typed earlier selectable.
    skill_options = base_skills + [
        s for s in profile.get("skills", []) if s not in base_skills
    ]
    role_options = base_roles + [
        r for r in profile.get("interests", []) if r not in base_roles
    ]

    with st.form("profile_form"):

        name = st.text_input(
            "Full Name",
            value=profile.get("name", "")
        )

        looking_for = st.radio(
            "I am looking for",
            looking_options,
            index=looking_options.index(
                profile.get("looking_for", "Internship")
            ),
            horizontal=True
        )

        col1, col2 = st.columns(2)

        with col1:
            year = st.selectbox(
                "Year of Study",
                year_options,
                index=year_options.index(profile.get("year", "3rd Year"))
            )

            branch = st.selectbox(
                "Field of Study",
                branch_options,
                index=branch_options.index(profile.get(
                    "branch", "Computer Science and Engineering"
                ))
                if profile.get("branch", "Computer Science and Engineering")
                in branch_options else branch_options.index("Other")
            )

            branch_other = st.text_input(
                "If 'Other', type your field of study",
                value=profile.get("branch_other", "")
            )

        with col2:
            location = st.text_input(
                "Current Location",
                value=profile.get("location", "Bengaluru, Karnataka")
            )

            experience = st.selectbox(
                "Experience Level",
                experience_options,
                index=experience_options.index(
                    profile.get("experience", experience_options[0])
                )
            )

        skills = st.multiselect(
            "Your Skills",
            skill_options,
            default=profile.get("skills", [])
        )

        other_skills = st.text_input(
            "Other skills not listed (separate with commas)",
            placeholder="e.g. Tableau, Rust, Figma"
        )

        interests = st.multiselect(
            "Preferred Roles",
            role_options,
            default=profile.get("interests", [])
        )

        other_roles = st.text_input(
            "Other roles not listed (separate with commas)",
            placeholder="e.g. Game Development, DevOps"
        )

        submitted = st.form_submit_button(
            "Save Profile →",
            use_container_width=True
        )

    if submitted:

        if not name.strip():
            st.error(
                "❌ Profile NOT saved. Please enter your full name."
            )

        elif not merge_unique(skills, other_skills):
            st.error(
                "❌ Profile NOT saved. Please choose or type at "
                "least one skill."
            )

        else:
            st.session_state.profile = {
                "name": name.strip(),
                "looking_for": looking_for,
                "year": year,
                "branch": branch,
                "branch_other": branch_other,
                "location": location,
                "experience": experience,
                "skills": merge_unique(skills, other_skills),
                "interests": merge_unique(interests, other_roles)
            }

            if looking_for == "Job":
                target = "Job Opportunities"
            else:
                target = "Find Internships"

            st.session_state.flash = (
                "success",
                f"✅ Profile saved successfully! Showing {looking_for.lower()} "
                "opportunities for you."
            )
            navigate(target)


# =====================================================
# 9. FIND INTERNSHIPS
# =====================================================

elif page == "Find Internships":

    render_listing_page("Internship")


# =====================================================
# 9b. JOB OPPORTUNITIES
# =====================================================

elif page == "Job Opportunities":

    render_listing_page("Job")


# =====================================================
# 10. OPPORTUNITY DETAILS
# =====================================================

elif page == "Opportunity Details":

    st.title("Opportunity Details")

    if not jobs:
        st.info("No listings loaded yet. Run radar.py first.")

    else:
        if st.session_state.selected_job >= len(jobs):
            st.session_state.selected_job = 0

        job = jobs[st.session_state.selected_job]

        st.markdown(f"""
        <div class="panel">
            <h2>{esc(job['title'])}</h2>
            <h3>{esc(job['company'])}</h3>
            <span class="score">{calculate_match(job)}% Match</span>
            <br><br>
            📍 {esc(job['location'])} | {esc(job['work_mode'])}
            <br><br>
            💰 {esc(job['stipend'])}
            <br>
            📅 Deadline: {esc(job['deadline'])}
            <br>
            Duration: {esc(job['duration'])}
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs([
            "Overview",
            "Eligibility",
            "Why You Match"
        ])

        with tab1:
            st.subheader("About the Role")
            st.write(job["description"])

        with tab2:
            st.subheader("Required Skills")
            st.write(job["requirements"])
            st.info(
                "Confirm exact eligibility on the employer's official listing."
            )

        with tab3:
            matching_skills = skill_hits(job)

            st.subheader("Your Matching Skills")

            if matching_skills:
                st.success(", ".join(matching_skills))
            else:
                st.warning("Add relevant skills to your profile.")

            st.metric("Skill Match", f"{calculate_match(job)}%")

        if job.get("apply_link"):
            st.link_button(
                "Apply on Official Website ↗",
                job["apply_link"],
                use_container_width=True
            )

            if st.button(
                "Mark as Applied",
                key="mark_applied",
                use_container_width=True
            ):
                if job["title"] not in st.session_state.applied:
                    st.session_state.applied.append(job["title"])
                st.toast("Marked as applied!")
        else:
            st.warning("Application link is not available.")


# =====================================================
# 11. READINESS CHECK
# =====================================================

elif page == "Readiness Check":

    st.title("Application Readiness")
    st.write("Check whether your application documents are ready.")

    st.subheader("Document Checklist")

    for document in list(st.session_state.documents):

        checked = st.checkbox(
            document,
            value=st.session_state.documents[document],
            key=f"document_{document}"
        )

        st.session_state.documents[document] = checked

    completed = sum(st.session_state.documents.values())
    total = len(st.session_state.documents)
    score = int(completed / total * 100)

    st.divider()

    st.subheader(f"Your Readiness Score: {score}%")

    st.progress(score / 100)

    if score == 100:
        st.success("🎉 All checklist items are complete!")
    else:
        st.warning("Complete the pending documents before applying.")


# =====================================================
# 12. SAVED INTERNSHIPS
# =====================================================

elif page == "Saved":

    st.title("Saved Opportunities")

    if not st.session_state.saved:

        st.info("You haven't saved anything yet.")

        if st.button("Find Internships"):
            navigate("Find Internships")

    else:

        for title in st.session_state.saved:

            st.markdown(f"""
            <div class="panel">
                ⭐ <b>{esc(title)}</b>
            </div>
            """, unsafe_allow_html=True)


# =====================================================
# 13. DASHBOARD
# =====================================================

elif page == "Dashboard":

    profile = st.session_state.profile

    st.title("Welcome to FormFit!")
    st.write("Track your progress and discover new opportunities.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("💼", len(jobs), "Opportunities Found")

    with c2:
        metric_card("⭐", len(st.session_state.saved), "Saved")

    with c3:
        metric_card("➤", len(st.session_state.applied), "Applied")

    with c4:
        metric_card(
            "📊",
            "100%" if profile else "0%",
            "Profile Status"
        )

    left, right = st.columns(2)

    with left:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Your Top Skills")

        if profile:

            for skill in profile.get("skills", []):

                st.markdown(
                    f'<span class="tag">{esc(skill)}</span>',
                    unsafe_allow_html=True
                )

        else:
            st.info("Complete your profile first.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Recommended For You")

        recommended = profile.get("interests", []) if profile else []
        if recommended:
            for role in recommended:
                st.write(f"➤ {role}")
        else:
            st.write("➤ AI/ML Internships")
            st.write("➤ Data Science Internships")
            st.write("➤ Software Development")
            st.write("➤ Research Opportunities")

        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Recent Opportunities")

    for job in jobs:

        st.markdown(f"""
        <div class="panel">
            <b>{esc(job['title'])}</b> | {esc(job['company'])}
            <br><br>
            Match: <span style="color:#009B75">
            {calculate_match(job)}%</span>
            | Deadline: {esc(job['deadline'])}
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# 14. ABOUT
# =====================================================

elif page == "About":

    st.title("About FormFit")

    st.markdown("""
    <div class="hero">
        <h1>FormFit 🎯</h1>
        <p>Find opportunities. Verify your fit. Apply with confidence.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("""
    FormFit is an AI-powered internship discovery platform
    designed to help students identify suitable opportunities.

    **Main Features**

    - Discover internships and jobs across multiple career websites.
    - Extract internship information.
    - Match opportunities with student skills.
    - Check application readiness.
    - Track saved and applied internships.

    TinyFish integration will provide live internship discovery.
    """)

    st.success("Helping students apply smarter, not harder!")