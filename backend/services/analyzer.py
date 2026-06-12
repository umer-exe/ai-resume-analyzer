"""Deterministic rule-based resume/profile analysis for Phase 6."""

import re
from functools import lru_cache

from services.ml_classifier import predict_role


SKILL_CATALOG = {
    "Programming": [
        ("Python", ("python",)),
        ("JavaScript", ("javascript", "java script", "js")),
        ("Java", ("java",)),
        ("C++", ("c++", "cpp")),
        ("C#", ("c#", "c sharp")),
        ("SQL", ("sql", "mysql", "postgresql", "postgres", "sqlite")),
    ],
    "Web Development": [
        ("HTML", ("html", "html5")),
        ("CSS", ("css", "css3")),
        ("Flask", ("flask",)),
        ("Django", ("django",)),
        ("React", ("react", "react.js", "reactjs")),
        ("Node.js", ("node.js", "nodejs", "node js")),
        ("REST APIs", ("rest api", "rest apis", "restful api", "api", "apis")),
    ],
    "AI and Data": [
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
    ],
    "Cybersecurity and Networking": [
        ("Cybersecurity", ("cybersecurity", "cyber security")),
        ("Networking", ("networking", "computer networks", "network security")),
        ("Linux", ("linux",)),
        ("Wireshark", ("wireshark",)),
    ],
    "Cloud and Tools": [
        ("GitHub", ("github",)),
        ("Git", ("git",)),
        ("Docker", ("docker",)),
        ("AWS", ("aws", "amazon web services")),
        ("Azure", ("azure", "microsoft azure")),
        ("Google Cloud", ("google cloud", "gcp")),
    ],
}

ROLE_CATALOG = [
    {
        "role": "Python Developer Intern",
        "required": ("Python", "Flask", "SQL"),
        "optional": ("Django", "REST APIs", "GitHub"),
    },
    {
        "role": "Junior Web Developer",
        "required": ("HTML", "CSS", "JavaScript"),
        "optional": ("React", "Flask", "GitHub"),
    },
    {
        "role": "Data Analyst Intern",
        "required": ("SQL", "Excel", "Data Visualization"),
        "optional": ("Python", "Pandas", "Power BI"),
    },
    {
        "role": "AI/ML Intern",
        "required": ("Python", "Artificial Intelligence", "Machine Learning"),
        "optional": ("Pandas", "NumPy", "GitHub"),
    },
    {
        "role": "Cybersecurity/Networking Intern",
        "required": ("Cybersecurity", "Networking", "Linux"),
        "optional": ("Wireshark", "Python", "GitHub"),
    },
]

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

PROJECT_DETAIL_TERMS = (
    "architecture",
    "backend",
    "database",
    "dataset",
    "frontend",
    "model",
    "outcome",
    "technology",
    "tool",
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

ROLE_KEYWORDS = (
    "analyst",
    "data analysis",
    "developer",
    "development",
    "engineer",
    "machine learning",
    "software",
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

RECOMMENDATION_BY_CATEGORY = {
    "Skills": "Add more role-relevant technical skills and tools.",
    "Projects": (
        "Expand project descriptions with the tools used and measurable outcomes."
    ),
    "Experience": (
        "Add practical experience, responsibilities, or transferable achievements."
    ),
    "Education": "State your education, field of study, and qualification clearly.",
    "ATS Keywords": (
        "Use stronger action verbs and role-specific keywords from target roles."
    ),
    "Formatting": (
        "Improve structure with clear sections, concise sentences, and bullet points."
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
    if score >= 70:
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
    """Return grouped canonical skills in deterministic catalog order."""
    detected_skills = {}

    for category, skill_definitions in SKILL_CATALOG.items():
        category_skills = []

        for skill, aliases in skill_definitions:
            if any(_contains_phrase(profile_text, alias) for alias in aliases):
                category_skills.append(skill)

        detected_skills[category] = category_skills

    return detected_skills


def _flatten_skills(grouped_skills):
    return [
        skill
        for category_skills in grouped_skills.values()
        for skill in category_skills
    ]


def _skills_analysis(grouped_skills):
    skill_count = sum(len(skills) for skills in grouped_skills.values())
    category_count = sum(bool(skills) for skills in grouped_skills.values())
    score = _round_score(
        (skill_count * 8)
        + (category_count * 7)
        + (10 if skill_count >= 5 else 0)
    )

    if score >= 70:
        feedback = (
            f"{skill_count} relevant skills were detected across "
            f"{category_count} categories."
        )
    elif score >= 50:
        feedback = (
            "Some relevant skills are present, but the profile needs broader "
            "role-specific coverage."
        )
    else:
        feedback = (
            "Add a clearer technical skills section with tools relevant to "
            "your target role."
        )

    return score, feedback


def _projects_analysis(profile_text, detected_skill_count):
    has_project = _contains_any(profile_text, PROJECT_TERMS)
    has_action = _contains_any(profile_text, ACTION_VERBS)
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))
    has_repository = _contains_any(profile_text, ("github", "portfolio"))
    has_detail = detected_skill_count > 0 and _contains_any(
        profile_text, PROJECT_DETAIL_TERMS
    )

    score = _round_score(
        10
        + (30 if has_project else 0)
        + (15 if has_action else 0)
        + (25 if has_measurement else 0)
        + (10 if has_repository else 0)
        + (10 if has_detail else 0)
    )

    if not has_project:
        feedback = "No clear project evidence was detected."
    elif not has_measurement:
        feedback = "Projects are present, but they need measurable outcomes."
    else:
        feedback = "Projects include useful technical detail and measurable evidence."

    return score, feedback


def _experience_analysis(profile_text):
    has_experience = _contains_any(profile_text, EXPERIENCE_TERMS)
    has_role = _contains_any(profile_text, ROLE_KEYWORDS)
    has_duration = bool(DURATION_PATTERN.search(profile_text))
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))
    action_count = _count_phrases(profile_text, ACTION_VERBS)

    score = _round_score(
        10
        + (30 if has_experience else 0)
        + (20 if has_role else 0)
        + (15 if has_duration else 0)
        + (15 if has_measurement else 0)
        + (10 if action_count >= 2 else 0)
    )

    if not has_experience:
        feedback = (
            "Add internships, volunteer work, freelance work, or transferable "
            "experience."
        )
    elif not has_measurement:
        feedback = "Experience is present but needs measurable achievements."
    else:
        feedback = "Experience includes role context and measurable evidence."

    return score, feedback


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
    elif not has_degree:
        feedback = "Education is present; add the qualification and study dates."
    else:
        feedback = "Education and qualification details are clearly represented."

    return score, feedback


def _ats_keywords_analysis(profile_text, detected_skill_count):
    action_count = _count_phrases(profile_text, ACTION_VERBS)
    has_role_keywords = _contains_any(profile_text, ROLE_KEYWORDS)
    has_measurement = bool(MEASURABLE_PATTERN.search(profile_text))

    score = _round_score(
        min(35, detected_skill_count * 5)
        + min(25, action_count * 5)
        + (20 if has_role_keywords else 0)
        + (20 if has_measurement else 0)
    )

    if score >= 70:
        feedback = "The profile contains useful skills, action verbs, and keywords."
    elif not has_measurement:
        feedback = (
            "Add measurable achievements and more keywords from target role "
            "descriptions."
        )
    else:
        feedback = "Add more role-specific skills and action verbs."

    return score, feedback


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

    length_score = 30 if word_count >= 80 else 25 if word_count >= 40 else 15
    sentence_score = 20 if sentence_count >= 3 else 15 if sentence_count >= 2 else 5

    score = _round_score(
        length_score
        + sentence_score
        + (20 if has_headings else 0)
        + (15 if has_bullets else 0)
        + (10 if is_readable_case else 0)
        + (5 if average_sentence_length <= 35 else 0)
    )

    if score >= 70:
        feedback = "The profile uses readable structure and concise formatting."
    elif not has_headings and not has_bullets:
        feedback = "Add clear section headings and concise bullet points."
    else:
        feedback = "Improve spacing, sentence length, and section consistency."

    return score, feedback


def match_roles(grouped_skills):
    """Return the top three skill-alignment suggestions with stable tie-breaking."""
    detected_skills = set(_flatten_skills(grouped_skills))
    matches = []

    for catalog_index, role in enumerate(ROLE_CATALOG):
        matched_required = [
            skill for skill in role["required"] if skill in detected_skills
        ]
        matched_optional = [
            skill for skill in role["optional"] if skill in detected_skills
        ]
        missing_required = [
            skill for skill in role["required"] if skill not in detected_skills
        ]
        missing_optional = [
            skill for skill in role["optional"] if skill not in detected_skills
        ]

        required_score = len(matched_required) / len(role["required"]) * 80
        optional_score = len(matched_optional) / len(role["optional"]) * 20
        match_percentage = _round_score(required_score + optional_score)

        matches.append(
            {
                "role": role["role"],
                "match_percentage": match_percentage,
                "matched_skills": matched_required + matched_optional,
                "missing_skills": missing_required + missing_optional,
                "_matched_required_count": len(matched_required),
                "_missing_required_count": len(missing_required),
                "_catalog_index": catalog_index,
            }
        )

    matches.sort(
        key=lambda match: (
            -match["match_percentage"],
            -match["_matched_required_count"],
            match["_missing_required_count"],
            match["_catalog_index"],
        )
    )

    return [
        {
            "role": match["role"],
            "match_percentage": match["match_percentage"],
            "matched_skills": match["matched_skills"],
            "missing_skills": match["missing_skills"],
        }
        for match in matches[:3]
    ]


def _build_recommendations(category_analysis):
    ranked_categories = sorted(
        category_analysis,
        key=lambda category: (
            category["score"],
            list(CATEGORY_WEIGHTS).index(category["category"]),
        ),
    )

    needs_work = [
        category for category in ranked_categories if category["status"] == "Needs Work"
    ]
    warnings = [
        category for category in ranked_categories if category["status"] == "Warning"
    ]

    high_categories = needs_work[:2] or ranked_categories[:1]
    medium_categories = [
        category
        for category in warnings
        if category["category"]
        not in {high_category["category"] for high_category in high_categories}
    ][:2]

    if not medium_categories:
        medium_categories = [
            category
            for category in ranked_categories
            if category["category"]
            not in {high_category["category"] for high_category in high_categories}
        ][:2]

    return {
        "high_priority": [
            RECOMMENDATION_BY_CATEGORY[category["category"]]
            for category in high_categories
        ],
        "medium_priority": [
            RECOMMENDATION_BY_CATEGORY[category["category"]]
            for category in medium_categories
        ],
        "low_priority": [
            "Add or refine a concise professional summary.",
            "Review formatting consistency before applying.",
        ],
    }


def _build_next_steps(category_analysis, top_role):
    weakest_category = min(
        category_analysis,
        key=lambda category: (
            category["score"],
            list(CATEGORY_WEIGHTS).index(category["category"]),
        ),
    )
    missing_skills = top_role["missing_skills"][:3]

    if missing_skills:
        skill_step = (
            f"Build missing skills for {top_role['role']}: "
            f"{', '.join(missing_skills)}."
        )
    else:
        skill_step = f"Continue strengthening skills for {top_role['role']}."

    return [
        RECOMMENDATION_BY_CATEGORY[weakest_category["category"]],
        "Add 2 to 3 projects with tools, responsibilities, and measurable outcomes.",
        skill_step,
        "Publish relevant projects and documentation on GitHub.",
        (
            "Tailor the profile for internships or entry-level roles and review "
            "each role description before applying."
        ),
    ]


def analyze_profile(profile_text):
    """Analyze profile text and return the Phase 5.5-compatible response data."""
    grouped_skills = extract_skills(profile_text)
    detected_skill_count = len(_flatten_skills(grouped_skills))

    category_results = [
        ("Skills", *_skills_analysis(grouped_skills)),
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
        }
        for category, score, feedback in category_results
    ]

    overall_score = _round_score(
        sum(
            category["score"] * CATEGORY_WEIGHTS[category["category"]]
            for category in category_analysis
        )
    )
    status = _overall_status(overall_score)
    role_matches = match_roles(grouped_skills)
    top_role = role_matches[0]

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
    summary = (
        f"Your profile is rated {status.lower()} with strongest skill-based "
        f"alignment to {top_role['role']}. Focus next on {weak_area_text}. "
        "Role suggestions are based on profile skills and are not live job matching."
    )
    ml_prediction = predict_role(profile_text)

    return {
        "score": overall_score,
        "status": status,
        "summary": summary,
        "top_role": top_role["role"],
        "checks": checks,
        "category_analysis": category_analysis,
        "skills": grouped_skills,
        "recommended_roles": role_matches,
        "recommendations": _build_recommendations(category_analysis),
        "next_steps": _build_next_steps(category_analysis, top_role),
        "ml_prediction": ml_prediction,
    }
