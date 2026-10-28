from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = ROOT_DIR / "policies"


def search_policies(query: str) -> dict[str, Any]:
    """Search local synthetic policy documents by keyword."""

    if not query or not query.strip():
        return {
            "ok": False,
            "error": "Search query cannot be empty.",
            "results": [],
        }

    if not POLICIES_DIR.exists():
        return {
            "ok": False,
            "error": "Policy directory was not found.",
            "results": [],
        }

    query_terms = set(query.lower().split())
    results = []

    for path in sorted(POLICIES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        text_lower = text.lower()

        # Simple baseline retrieval: count query terms in each document.
        score = sum(text_lower.count(term) for term in query_terms)

        if score > 0:
            results.append({
                "source": path.name,
                "score": score,
                "content": text,
                "synthetic": True,
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    return {
        "ok": True,
        "query": query,
        "results": results,
    }


def validate_application(
    application: dict[str, Any],
) -> dict[str, Any]:
    """Validate the required fields in a demo application."""

    required_fields = [
        "applicant_name",
        "location",
        "activity",
        "contact",
    ]

    missing_fields = [
        field
        for field in required_fields
        if not str(application.get(field, "")).strip()
    ]

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def create_application_draft(
    application: dict[str, Any],
) -> dict[str, Any]:
    """Create a local draft and stop for human approval."""

    validation = validate_application(application)

    if not validation["valid"]:
        return {
            "status": "incomplete",
            "missing_fields": validation["missing_fields"],
        }

    # This function does not submit anything to an external service.
    return {
        "status": "awaiting_approval",
        "message": (
            "Draft prepared. Human approval is required "
            "before any further action."
        ),
        "draft": dict(application),
        "submitted": False,
        "synthetic": True,
    }
