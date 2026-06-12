"""Static rules used by the deterministic profile analyzer."""

import re


SKILL_CATALOG = (
    ("Python", ("python",)),
    ("JavaScript", ("javascript", "java script", "js")),
    ("Java", ("java",)),
    ("C++", ("c++", "cpp")),
    ("C#", ("c#", "c sharp")),
    ("SQL", ("sql", "mysql", "postgresql", "postgres", "sqlite")),
    ("HTML", ("html", "html5")),
    ("CSS", ("css", "css3")),
    ("Flask", ("flask",)),
    ("Django", ("django",)),
    ("React", ("react", "react.js", "reactjs")),
    ("Node.js", ("node.js", "nodejs", "node js")),
    ("REST APIs", ("rest api", "rest apis", "restful api", "api", "apis")),
    (
        "Artificial Intelligence",
        ("artificial intelligence", "basic ai concepts", "ai concepts", "ai"),
    ),
    ("Machine Learning", ("machine learning", "machine-learning", "ml")),
    ("Pandas", ("pandas",)),
    ("NumPy", ("numpy",)),
    (
        "Data Visualization",
        ("data visualization", "data visualisation", "visualization"),
    ),
    ("Excel", ("excel", "microsoft excel")),
    ("Power BI", ("power bi", "powerbi")),
    ("Cybersecurity", ("cybersecurity", "cyber security")),
    ("Networking", ("networking", "computer networks", "network security")),
    ("Linux", ("linux",)),
    ("Wireshark", ("wireshark",)),
    ("GitHub", ("github",)),
    ("Git", ("git",)),
    ("Docker", ("docker",)),
    ("AWS", ("aws", "amazon web services")),
    ("Azure", ("azure", "microsoft azure")),
    ("Google Cloud", ("google cloud", "gcp")),
)

CATEGORY_WEIGHTS = {
    "Skills": 0.25,
    "Projects": 0.20,
    "Experience": 0.15,
    "Education": 0.15,
    "ATS Keywords": 0.15,
    "Formatting": 0.10,
}
CATEGORY_ORDER = tuple(CATEGORY_WEIGHTS)

CATEGORY_GOOD_SCORE = 75
CATEGORY_WARNING_SCORE = 50
OVERALL_STRONG_SCORE = 80
OVERALL_MODERATE_SCORE = 60

ACTION_VERBS = (
    "achieved",
    "analyzed",
    "automated",
    "built",
    "created",
    "designed",
    "developed",
    "implemented",
    "improved",
    "led",
    "managed",
    "optimized",
    "reduced",
    "tested",
)

PROJECT_TERMS = (
    "academic project",
    "capstone",
    "project",
    "projects",
    "portfolio",
)

EXPERIENCE_TERMS = (
    "employment",
    "experience",
    "freelance",
    "intern",
    "internship",
    "volunteer",
    "worked",
)

EDUCATION_TERMS = (
    "college",
    "education",
    "school",
    "student",
    "university",
)

DEGREE_TERMS = (
    "associate",
    "bachelor",
    "bs",
    "bsc",
    "degree",
    "master",
    "msc",
)

FIELD_TERMS = (
    "artificial intelligence",
    "computer science",
    "data science",
    "information technology",
    "software engineering",
)

MEASURABLE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:\.\d+)?\s*"
    r"(?:%|percent|users?|clients?|projects?|hours?|days?|weeks?|months?|"
    r"years?|records?|requests?|seconds?|ms|x)(?![A-Za-z0-9])",
    re.IGNORECASE,
)

DURATION_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:\d+\+?\s*(?:months?|years?)|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)

YEAR_PATTERN = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
HEADING_PATTERN = re.compile(
    r"(?im)^\s*(?:education|experience|projects?|skills|summary)\s*:?\s*$"
)
BULLET_PATTERN = re.compile(r"(?m)^\s*(?:[-*]|\d+[.)])\s+")

ACTION_BY_CATEGORY = {
    "Skills": (
        "Add a concise skills section with the technical tools you can demonstrate."
    ),
    "Projects": (
        "Describe projects with the tools used, your contribution, and a "
        "measurable result."
    ),
    "Experience": (
        "Add an internship, freelance, volunteer, or academic responsibility "
        "with clear outcomes."
    ),
    "Education": (
        "State your qualification, field of study, institution, and dates clearly."
    ),
    "ATS Keywords": (
        "Use clear technical skills, action verbs, and measurable achievements "
        "throughout the profile."
    ),
    "Formatting": (
        "Organize the profile with clear headings, concise bullet points, and "
        "consistent spacing."
    ),
}
