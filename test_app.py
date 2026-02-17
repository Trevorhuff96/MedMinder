import pytest
from auth import is_valid_email
import os
import glob

#test valid email formats
def test_valid_email():
    assert is_valid_email("test@example.com")

def test_invalid_email_missing_at():
    assert not is_valid_email("testexample.com")

def test_invalid_email_missing_domain():
    assert not is_valid_email("test@")

def test_invalid_email_missing_dot():
    assert not is_valid_email("test@example")

#test docs folder and required documents
REQUIRED_DOCS = [
    "Design Decisions.docx",
    "Prompts.docx",
    "Requirements with Trust Gates.docx",
    "System Proposal - MedMinder.pdf",
]

def test_docs_folder_exists():
    assert os.path.isdir("docs"), "❌ docs folder is missing!"

def test_required_docs_exist_in_docs():
    for doc in REQUIRED_DOCS:
        path = os.path.join("docs", doc)
        assert os.path.exists(path), f"❌ {doc} is missing from docs folder!"

def test_no_docs_outside_docs_folder():
    all_docx = glob.glob("**/*.docx", recursive=True)
    all_pdf = glob.glob("**/*.pdf", recursive=True)

    for file in all_docx + all_pdf:
        normalized = file.replace("\\", "/")
        assert normalized.startswith("docs/"), f"❌ {file} is outside the docs folder!"



