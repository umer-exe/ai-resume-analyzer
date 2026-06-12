"""Deterministic rule-based resume/profile analysis for Phase 6."""

import re
from functools import lru_cache

from services import analyzer_rules as rules
from services.ml_classifier import predict_category


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
    if score >= rules.CATEGORY_GOOD_SCORE:
        return "Good"
    if score >= rules.CATEGORY_WARNING_SCORE:
        return "Warning"
    return "Needs Work"


def _overall_status(score):
    if score >= rules.OVERALL_STRONG_SCORE:
        return "Strong"
    if score >= rules.OVERALL_MODERATE_SCORE:
        return "Moderate"
    return "Needs Work"


def _category_sort_key(category):
    return (
        category["score"],
        rules.CATEGORY_ORDER.index(category["category"]),
    )


def extract_skills(profile_text):
    """Return unique canonical skills in deterministic catalog order."""
    return [
        skill
        for skill, aliases in rules.SKILL_CATALOG
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
        action = rules.ACTION_BY_CATEGORY["Skills"]

    return score, feedback, action


def _projects_analysis(profile_text, detected_skill_count):
    has_project = _contains_any(profile_text, rules.PROJECT_TERMS)
    has_action = _contains_any(profile_text, rules.ACTION_VERBS)
    has_measurement = bool(rules.MEASURABLE_PATTERN.search(profile_text))
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
        action = rules.ACTION_BY_CATEGORY["Projects"]
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
    has_experience = _contains_any(profile_text, rules.EXPERIENCE_TERMS)
    has_duration = bool(rules.DURATION_PATTERN.search(profile_text))
    has_measurement = bool(rules.MEASURABLE_PATTERN.search(profile_text))
    has_action = _contains_any(profile_text, rules.ACTION_VERBS)

    score = _round_score(
        (40 if has_experience else 0)
        + (20 if has_action else 0)
        + (20 if has_duration else 0)
        + (20 if has_measurement else 0)
    )

    if not has_experience:
        feedback = "No clear practical experience was detected."
        action = rules.ACTION_BY_CATEGORY["Experience"]
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
    has_education = _contains_any(profile_text, rules.EDUCATION_TERMS)
    has_field = _contains_any(profile_text, rules.FIELD_TERMS)
    has_degree = _contains_any(profile_text, rules.DEGREE_TERMS)
    has_year = bool(rules.YEAR_PATTERN.search(profile_text))

    score = _round_score(
        (40 if has_education else 0)
        + (25 if has_field else 0)
        + (20 if has_degree else 0)
        + (15 if has_year else 0)
    )

    if not has_education:
        feedback = "Education details were not clearly detected."
        action = rules.ACTION_BY_CATEGORY["Education"]
    elif not has_degree:
        feedback = "Education is present; add the qualification and study dates."
        action = "Add the qualification name and expected or completed study dates."
    else:
        feedback = "Education and qualification details are clearly represented."
        action = "Keep education details concise and consistently formatted."

    return score, feedback, action


def _ats_keywords_analysis(profile_text, detected_skill_count):
    action_count = _count_phrases(profile_text, rules.ACTION_VERBS)
    has_measurement = bool(rules.MEASURABLE_PATTERN.search(profile_text))

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
        action = rules.ACTION_BY_CATEGORY["ATS Keywords"]

    return score, feedback, action


def _formatting_analysis(profile_text):
    words = re.findall(r"\b[\w+#.]+\b", profile_text)
    word_count = len(words)
    sentence_count = len(
        [sentence for sentence in re.split(r"[.!?]+", profile_text) if sentence.strip()]
    )
    has_headings = bool(rules.HEADING_PATTERN.search(profile_text))
    has_bullets = bool(rules.BULLET_PATTERN.search(profile_text))
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
        action = rules.ACTION_BY_CATEGORY["Formatting"]
    else:
        feedback = "Improve spacing, sentence length, and section consistency."
        action = "Shorten dense sentences and make section formatting consistent."

    return score, feedback, action


def _build_action_plan(category_analysis):
    ranked_categories = sorted(category_analysis, key=_category_sort_key)
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


def _build_checks(category_analysis):
    return {
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


def _build_summary(category_analysis, status):
    weakest_categories = sorted(
        category_analysis,
        key=_category_sort_key,
    )[:2]
    strongest_categories = sorted(
        category_analysis,
        key=lambda category: (
            -category["score"],
            rules.CATEGORY_ORDER.index(category["category"]),
        ),
    )[:2]

    weak_area_text = " and ".join(
        category["category"].lower() for category in weakest_categories
    )
    strong_area_text = " and ".join(
        category["category"].lower() for category in strongest_categories
    )
    return (
        f"Your profile is rated {status.lower()}. Its strongest areas are "
        f"{strong_area_text}; focus next on improving {weak_area_text}."
    )


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
            category["score"] * rules.CATEGORY_WEIGHTS[category["category"]]
            for category in category_analysis
        )
    )
    status = _overall_status(overall_score)

    return {
        "score": overall_score,
        "status": status,
        "summary": _build_summary(category_analysis, status),
        "checks": _build_checks(category_analysis),
        "category_analysis": category_analysis,
        "skills": detected_skills,
        "action_plan": _build_action_plan(category_analysis),
        "ml_prediction": predict_category(profile_text),
    }
