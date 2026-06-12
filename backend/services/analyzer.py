"""Deterministic rule-based resume/profile analysis for Phase 6."""

import re
from functools import lru_cache

from services.ml_classifier import predict_role


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
    "Skills": "Add a concise skills section with the technical tools you can demonstrate.",
    "Projects": "Describe projects with the tools used, your contribution, and a measurable result.",
    "Experience": (
        "Add an internship, freelance, volunteer, or academic responsibility with clear outcomes."
    ),
    "Education": "State your qualification, field of study, institution, and dates clearly.",
    "ATS Keywords": (
        "Use clear technical skills, action verbs, and measurable achievements throughout the profile."
    ),
    "Formatting": (
        "Organize the profile with clear headings, concise bullet points, and consistent spacing."
    ),
}


@lru_cache(maxsize=None)
def _phrase_pattern(phrase):
    escaped_phrase = re.escape(phrase).replace(r"\ ", r"\s+")
    return re.compile(
        rf"(?<![A-Za-z0-9]){escaped_phrase}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


def _contains_phrase(text, phrase):
    return bool(_phrase_pattern(phrase).search(text))


def _contains_any(text, phrases):
    return any(_contains_phrase(text, phrase) for phrase in phrases)


def _count_phrases(text, phrases):
    return sum(1 for phrase in phrases if _contains_phrase(text, phrase))


def _round_score(value):
    return max(0, min(100, int(value + 0.5)))


def _category_status(score):
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Warning"
    return "Needs Work"


def _overall_status(score):
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Moderate"
    return "Needs Work"


def extract_skills(profile_text):
    """Return unique canonical skills in deterministic catalog order."""
    return [
        skill
        for skill, aliases in SKILL_CATALOG
        if any(_contains_phrase(profile_text, alias) for alias in aliases)
    ]


def _skills_analysis(detected_skills):
    skill_count = len(detected_skills)
    if skill_count >= 8:
        score = 100
    elif skill_count >= 5:
        score = 80
    elif skill_count >= 3:
        score = 60
    elif skill_count >= 1:
        score = 40
    else:
        score = 0

    if score >= 70:
        feedback = f"{skill_count} technical skills were clearly detected."
        action = (
            "Support the listed skills with clear project or experience evidence."
        )
    elif score >= 50:
        feedback = "Several technical skills are present, but the skills section could be clearer."
        action = "Group the detected skills in one concise technical skills section."
    else:
        feedback = "Few clearly named technical skills were detected."
        action = ACTION_BY_CATEGORY["Skills"]

    return score, feedback, action


def _projects_analysis(profile_text, detected_skill_count):
    has_project = _contains_any(profile_text, PROJECT_TERMS)
    has_action = _contains_any(profile_text, ACTION_VERBS)
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))
    has_detail = detected_skill_count > 0 and has_project

    score = (
        _round_score(
            20
            + (25 if has_detail else 0)
            + (20 if has_action else 0)
            + (35 if has_measurement else 0)
        )
        if has_project
        else 0
    )

    if not has_project:
        feedback = "No clear project evidence was detected."
        action = ACTION_BY_CATEGORY["Projects"]
    elif not has_detail:
        feedback = "Projects are mentioned, but the tools and contribution are unclear."
        action = "Name the tools used and explain your contribution to each project."
    elif not has_measurement:
        feedback = "Projects are present, but they need measurable outcomes."
        action = "Add one concrete result, user count, percentage, or performance outcome."
    else:
        feedback = "Projects include technical detail and measurable evidence."
        action = "Keep project descriptions concise and lead with the strongest outcome."

    return score, feedback, action


def _experience_analysis(profile_text):
    has_experience = _contains_any(profile_text, EXPERIENCE_TERMS)
    has_duration = bool(DURATION_PATTERN.search(profile_text))
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))
    has_action = _contains_any(profile_text, ACTION_VERBS)

    score = _round_score(
        (40 if has_experience else 0)
        + (20 if has_action else 0)
        + (20 if has_duration else 0)
        + (20 if has_measurement else 0)
    )

    if not has_experience:
        feedback = "No clear practical experience was detected."
        action = ACTION_BY_CATEGORY["Experience"]
    elif not has_action:
        feedback = "Experience is present, but responsibilities are not described clearly."
        action = "Rewrite experience points with direct action verbs and clear responsibilities."
    elif not has_measurement:
        feedback = "Experience is present but needs measurable achievements."
        action = "Add a measurable result to at least one experience entry."
    else:
        feedback = "Experience includes clear responsibilities and measurable evidence."
        action = "Keep the strongest achievement first in each experience entry."

    return score, feedback, action


def _education_analysis(profile_text):
    has_education = _contains_any(profile_text, EDUCATION_TERMS)
    has_field = _contains_any(profile_text, FIELD_TERMS)
    has_degree = _contains_any(profile_text, DEGREE_TERMS)
    has_year = bool(YEAR_PATTERN.search(profile_text))

    score = _round_score(
        (40 if has_education else 0)
        + (25 if has_field else 0)
        + (20 if has_degree else 0)
        + (15 if has_year else 0)
    )

    if not has_education:
        feedback = "Education details were not clearly detected."
        action = ACTION_BY_CATEGORY["Education"]
    elif not has_degree:
        feedback = "Education is present; add the qualification and study dates."
        action = "Add the qualification name and expected or completed study dates."
    else:
        feedback = "Education and qualification details are clearly represented."
        action = "Keep education details concise and consistently formatted."

    return score, feedback, action


def _ats_keywords_analysis(profile_text, detected_skill_count):
    action_count = _count_phrases(profile_text, ACTION_VERBS)
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))

    score = _round_score(
        (40 if detected_skill_count >= 3 else 20 if detected_skill_count else 0)
        + (30 if action_count >= 2 else 15 if action_count else 0)
        + (30 if has_measurement else 0)
    )

    if score >= 75:
        feedback = "The profile uses clear skills, action verbs, and measurable evidence."
        action = "Keep technical terms specific and connect them to demonstrated results."
    elif action_count == 0:
        feedback = "Add direct action verbs to describe contributions and achievements."
        action = "Start contribution statements with direct verbs such as built, improved, or tested."
    elif not has_measurement:
        feedback = "Add measurable results to strengthen the profile evidence."
        action = "Add numbers, percentages, scale, or time saved to key achievements."
    else:
        feedback = "Name more technical skills clearly in the profile."
        action = ACTION_BY_CATEGORY["ATS Keywords"]

    return score, feedback, action


def _formatting_analysis(profile_text):
    words = re.findall(r"\b[\w+#.]+\b", profile_text)
    word_count = len(words)
    sentence_count = len(
        [sentence for sentence in re.split(r"[.!?]+", profile_text) if sentence.strip()]
    )
    has_headings = bool(HEADING_PATTERN.search(profile_text))
    has_bullets = bool(BULLET_PATTERN.search(profile_text))
    is_readable_case = profile_text != profile_text.upper()
    average_sentence_length = word_count / max(sentence_count, 1)

    length_score = 30 if word_count >= 80 else 20 if word_count >= 40 else 10
    readable_sentences = sentence_count >= 2 and average_sentence_length <= 35

    score = _round_score(
        length_score
        + (25 if has_headings else 0)
        + (25 if has_bullets else 0)
        + (20 if readable_sentences and is_readable_case else 0)
    )

    if score >= 75:
        feedback = "The profile uses readable structure and concise formatting."
        action = "Keep headings, bullets, spacing, and sentence style consistent."
    elif not has_headings and not has_bullets:
        feedback = "Add clear section headings and concise bullet points."
        action = ACTION_BY_CATEGORY["Formatting"]
    else:
        feedback = "Improve spacing, sentence length, and section consistency."
        action = "Shorten dense sentences and make section formatting consistent."

    return score, feedback, action


def _build_action_plan(category_analysis):
    ranked_categories = sorted(
        category_analysis,
        key=lambda category: (
            category["score"],
            list(CATEGORY_WEIGHTS).index(category["category"]),
        ),
    )

    categories_to_improve = [
        category
        for category in ranked_categories
        if category["status"] != "Good"
    ]
    selected_categories = categories_to_improve[:3] or ranked_categories[:1]

    return [
        {
            "category": category["category"],
            "priority": (
                "High"
                if category["status"] == "Needs Work"
                else "Medium"
                if category["status"] == "Warning"
                else "Low"
            ),
            "action": category["action"],
        }
        for category in selected_categories
    ]


def analyze_profile(profile_text):
    """Return deterministic profile-quality analysis plus the ML prediction."""
    detected_skills = extract_skills(profile_text)
    detected_skill_count = len(detected_skills)

    category_results = [
        ("Skills", *_skills_analysis(detected_skills)),
        ("Projects", *_projects_analysis(profile_text, detected_skill_count)),
        ("Experience", *_experience_analysis(profile_text)),
        ("Education", *_education_analysis(profile_text)),
        (
            "ATS Keywords",
            *_ats_keywords_analysis(profile_text, detected_skill_count),
        ),
        ("Formatting", *_formatting_analysis(profile_text)),
    ]

    category_analysis = [
        {
            "category": category,
            "score": score,
            "status": _category_status(score),
            "feedback": feedback,
            "action": action,
        }
        for category, score, feedback, action in category_results
    ]

    overall_score = _round_score(
        sum(
            category["score"] * CATEGORY_WEIGHTS[category["category"]]
            for category in category_analysis
        )
    )
    status = _overall_status(overall_score)

    checks = {
        "passed": sum(
            category["status"] == "Good" for category in category_analysis
        ),
        "warnings": sum(
            category["status"] == "Warning" for category in category_analysis
        ),
        "issues": sum(
            category["status"] == "Needs Work" for category in category_analysis
        ),
    }

    weakest_categories = sorted(
        category_analysis,
        key=lambda category: (
            category["score"],
            list(CATEGORY_WEIGHTS).index(category["category"]),
        ),
    )[:2]
    weak_area_text = " and ".join(
        category["category"].lower() for category in weakest_categories
    )
    strongest_categories = sorted(
        category_analysis,
        key=lambda category: (
            -category["score"],
            list(CATEGORY_WEIGHTS).index(category["category"]),
        ),
    )[:2]
    strong_area_text = " and ".join(
        category["category"].lower() for category in strongest_categories
    )
    summary = (
        f"Your profile is rated {status.lower()}. Its strongest areas are "
        f"{strong_area_text}; focus next on improving {weak_area_text}."
    )
    ml_prediction = predict_role(profile_text)

    return {
        "score": overall_score,
        "status": status,
        "summary": summary,
        "checks": checks,
        "category_analysis": category_analysis,
        "skills": detected_skills,
        "action_plan": _build_action_plan(category_analysis),
        "ml_prediction": ml_prediction,
    }
