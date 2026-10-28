from app.tools import (
    search_policies,
    validate_application,
    create_application_draft,
)


def test_search_finds_synthetic_policy():
    result = search_policies("food truck requirements")

    assert result["ok"] is True
    assert len(result["results"]) >= 1
    assert result["results"][0]["synthetic"] is True


def test_empty_search_query_is_rejected():
    result = search_policies("   ")

    assert result["ok"] is False
    assert result["results"] == []


def test_complete_application_is_valid():
    application = {
        "applicant_name": "Ahmed Demo",
        "location": "Jeddah Demo Zone",
        "activity": "Food truck",
        "contact": "demo@example.com",
    }

    result = validate_application(application)

    assert result["valid"] is True
    assert result["missing_fields"] == []


def test_missing_location_is_detected():
    application = {
        "applicant_name": "Ahmed Demo",
        "location": "",
        "activity": "Food truck",
        "contact": "demo@example.com",
    }

    result = validate_application(application)

    assert result["valid"] is False
    assert "location" in result["missing_fields"]


def test_incomplete_application_cannot_create_draft():
    application = {
        "applicant_name": "Ahmed Demo",
        "location": "",
        "activity": "Food truck",
        "contact": "demo@example.com",
    }

    result = create_application_draft(application)

    assert result["status"] == "incomplete"


def test_complete_application_waits_for_approval():
    application = {
        "applicant_name": "Ahmed Demo",
        "location": "Jeddah Demo Zone",
        "activity": "Food truck",
        "contact": "demo@example.com",
    }

    result = create_application_draft(application)

    assert result["status"] == "awaiting_approval"
    assert result["submitted"] is False
