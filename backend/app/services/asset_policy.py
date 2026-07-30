import re
from typing import Dict, List, Tuple


DESCRIPTIVE_KEYWORDS = {
    "introduction",
    "history",
    "overview",
    "definition",
    "applications",
    "advantages",
    "disadvantages",
    "future work",
    "literature review",
    "conclusion",
    "summary",
    "company overview",
    "marketing",
    "background",
    "motivation",
    "problem statement",
}

ANIMATION_KEYWORDS = {
    "algebra",
    "geometry",
    "trigonometry",
    "calculus",
    "linear algebra",
    "coordinate geometry",
    "function",
    "functions",
    "graph",
    "graphs",
    "statistics",
    "probability",
    "equation",
    "equations",
    "projectile motion",
    "electric field",
    "electric fields",
    "magnetic field",
    "magnetic fields",
    "wave",
    "waves",
    "binary tree",
    "binary trees",
    "graph algorithm",
    "graph algorithms",
    "bfs",
    "dfs",
    "sorting algorithm",
    "sorting algorithms",
    "neural network",
    "neural networks",
    "proof",
    "proofs",
    "vector",
    "matrix",
    "matrices",
    "derivative",
    "integral",
    "limit",
    "kinematics",
}

DIAGRAM_KEYWORDS = {
    "architecture",
    "system architecture",
    "software architecture",
    "process flow",
    "workflow",
    "data flow",
    "entity relationship",
    "erd",
    "class diagram",
    "sequence diagram",
    "pipeline",
    "network architecture",
    "decision tree",
    "component",
    "components",
    "relationship",
    "relationships",
    "algorithm",
    "algorithms",
    "framework architecture",
    "api flow",
    "lifecycle",
    "stages",
}

PROCESS_HINTS = {
    "step",
    "steps",
    "flow",
    "workflow",
    "pipeline",
    "process",
    "lifecycle",
    "architecture",
    "module",
    "component",
    "algorithm",
    "tree",
    "graph",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _contains_any(text: str, keywords: set[str]) -> bool:
    normalized = _normalize(text)
    return any(keyword in normalized for keyword in keywords)


def _slide_text(slide: Dict) -> str:
    parts = [
        slide.get("title", ""),
        slide.get("content", ""),
        " ".join(slide.get("bullet_points", [])),
    ]
    return " ".join(part for part in parts if part).strip()


def _is_descriptive_title(title: str) -> bool:
    return _contains_any(title, DESCRIPTIVE_KEYWORDS)


def should_generate_animation(topic: str, slides: List[Dict]) -> Tuple[bool, str]:
    corpus = " ".join([topic] + [_slide_text(slide) for slide in slides[:8]])
    titles = [slide.get("title", "") for slide in slides[:8] if slide.get("title")]

    if _contains_any(corpus, DESCRIPTIVE_KEYWORDS) and not _contains_any(corpus, ANIMATION_KEYWORDS):
        return False, "Topic is primarily descriptive and does not need visual animation."

    if not _contains_any(corpus, ANIMATION_KEYWORDS):
        return False, "Topic does not match Vynetra's supported visual concept categories."

    meaningful_titles = [title for title in titles if not _is_descriptive_title(title)]
    if not meaningful_titles:
        return False, "Slides do not contain a concept that benefits from animation."

    return True, "Topic contains visually explainable mathematical or algorithmic concepts."


def select_animation_focus(topic: str, slides: List[Dict]) -> str:
    candidates = []
    for slide in slides[:8]:
        title = slide.get("title", "").strip()
        content = slide.get("content", "").strip()
        if _contains_any(f"{title} {content}", ANIMATION_KEYWORDS) and not _is_descriptive_title(title):
            candidates.append(title or content)

    if candidates:
        return candidates[0]

    return topic


def select_diagram_candidate_slides(topic: str, slides: List[Dict], limit: int = 2) -> List[Dict]:
    candidates: List[Dict] = []
    topic_supports_diagram = _contains_any(topic, DIAGRAM_KEYWORDS)

    for slide in slides[:8]:
        title = slide.get("title", "")
        content = slide.get("content", "")
        bullets = slide.get("bullet_points", [])
        combined = f"{title} {content} {' '.join(bullets)}"

        if _is_descriptive_title(title):
            continue

        bullet_count = len([bullet for bullet in bullets if bullet.strip()])
        has_structure = bullet_count >= 3 or _contains_any(combined, PROCESS_HINTS)
        is_diagram_worthy = _contains_any(combined, DIAGRAM_KEYWORDS) or (topic_supports_diagram and has_structure)

        if is_diagram_worthy:
            candidates.append(slide)

        if len(candidates) >= limit:
            break

    return candidates
