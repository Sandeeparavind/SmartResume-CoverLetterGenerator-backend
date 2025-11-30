import io
from fastapi.testclient import TestClient

from app.main import app
from app.services import career_service

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_smart_resume_upload_returns_suggestions(monkeypatch):
    # Arrange: fake implementation so we don't call Hugging Face
    def fake_improve_resume_from_file(file_bytes, content_type, job_description):
        assert content_type == "text/plain"
        assert "backend" in job_description.lower()  # check JD flowed through
        # Return suggestions as if AI produced them
        return [
            "Add measurable impact to your backend projects.",
            "Highlight your experience with REST APIs more prominently.",
        ]

    monkeypatch.setattr(
        career_service,
        "improve_resume_from_file",
        fake_improve_resume_from_file,
    )

    resume_content = b"My resume content with backend and APIs."
    files = {
        "file": ("resume.txt", resume_content, "text/plain"),
    }
    data = {
        "job_description": "We are looking for a backend engineer experienced with APIs.",
    }

    # Act
    resp = client.post(
        "/api/career/smart-resume-upload",
        files=files,
        data=data,
    )

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert "suggestions" in body
    assert isinstance(body["suggestions"], list)
    assert len(body["suggestions"]) == 2
    assert "backend" in body["suggestions"][0].lower()


def test_rewrite_summary_upload_returns_summary(monkeypatch):
    def fake_rewrite_summary_from_file(file_bytes, content_type, job_description):
        assert content_type == "text/plain"
        assert "intern" in job_description.lower()
        return "Backend-focused Software Engineering student with experience in APIs and cloud."

    monkeypatch.setattr(
        career_service,
        "rewrite_summary_from_file",
        fake_rewrite_summary_from_file,
    )

    resume_content = b"My resume content with some summary."
    files = {
        "file": ("resume.txt", resume_content, "text/plain"),
    }
    data = {
        "job_description": "Software Engineer Intern working on backend services.",
    }

    resp = client.post(
        "/api/career/rewrite-summary-upload",
        files=files,
        data=data,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "rewritten_summary" in body
    assert "backend" in body["rewritten_summary"].lower()


def test_cover_letter_upload_returns_cover_letter(monkeypatch):
    def fake_generate_cover_letter_from_file(
        job_title,
        company_name,
        job_description,
        tone,
        resume_bytes,
        resume_content_type,
    ):
        assert job_title == "Software Engineer Intern"
        assert company_name == "CoolTech Inc"
        assert "python" in job_description.lower()
        assert resume_content_type == "text/plain"
        # Simulate AI-generated cover letter
        return (
            "Dear Hiring Manager,\n\n"
            "I am excited to apply for the Software Engineer Intern position at CoolTech Inc..."
        )

    monkeypatch.setattr(
        career_service,
        "generate_cover_letter_from_file",
        fake_generate_cover_letter_from_file,
    )

    resume_content = b"My resume content mentioning Python and backend."
    files = {
        "resume": ("resume.txt", resume_content, "text/plain"),
    }
    data = {
        "job_title": "Software Engineer Intern",
        "company_name": "CoolTech Inc",
        "job_description": "We use Python for backend services.",
        "tone": "professional",
    }

    resp = client.post(
        "/api/career/cover-letter",
        files=files,
        data=data,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "cover_letter" in body
    assert body["cover_letter"].startswith("Dear Hiring Manager")
