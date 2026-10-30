# 🎯 FormFit – AI-Powered Internship Radar

### Find Opportunities. Verify Your Fit. Apply with Confidence.

## 📌 About the Project

FormFit is an AI-powered internship discovery platform designed to help college students find suitable internships and evaluate their application readiness before applying.

Students can enter their skills, interests, academic year, experience level, and preferred location. FormFit helps identify relevant opportunities, compare skill requirements, and prepare students for applications.

## 🎯 Problem Statement

Students often struggle to find internships that match their skills and eligibility. They spend valuable time browsing multiple websites and checking requirements manually.

FormFit aims to simplify this process through opportunity discovery, skill matching, and application readiness checks.

## ✨ Key Features

- **Student Profile:** Enter academic details, skills, interests, and location.
- **Internship Discovery:** Explore internship opportunities.
- **Skill Matching:** Calculate compatibility scores based on student skills.
- **Opportunity Details:** View eligibility, stipend, location, duration, and deadlines when available.
- **Readiness Check:** Track required application documents.
- **Save Opportunities:** Save interesting internships.
- **Dashboard:** Track saved opportunities and application progress.

## 🛠️ Technology Stack

- Python
- Streamlit
- TinyFish
- JSON
- SQLite (planned for persistent data storage)

## 📂 Project Structure

```text
FormFit/
│
├── app.py
├── radar.py
├── internships.json
├── config.toml
├── settings.json
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/kapuluriharipriya/FormFit.git
```

### 2. Open the project folder

```bash
cd FormFit
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

## 🚀 Future Enhancements

- Live internship discovery using TinyFish web agents.
- Integration with multiple trusted opportunity websites.
- Explainable opportunity matching scores.
- Verified eligibility and deadline extraction.
- SQLite database integration.
- Personalized internship recommendations.

## 🌟 Project Vision

Our vision is to help students discover the right opportunities, understand their eligibility, identify missing requirements, and apply with confidence.

**FormFit – Helping Students Apply Smarter, Not Harder!**

## 👥 Team

Developed as a team project for the TinyFish Hackathon.
