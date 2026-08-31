import pytest


ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "webp"}
ALLOWED_MIMES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}


def validate_upload_security(filename: str, content_type: str) -> tuple[bool, str]:
    ext = (filename or "").rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extension de fichier non autorisée. Extensions acceptées : {', '.join(ALLOWED_EXTENSIONS)}"
    if content_type.lower() not in ALLOWED_MIMES:
        return False, "Format de fichier non supporté."
    return True, "OK"


@pytest.mark.unit
def test_maintenance_receipt_upload_rejects_dangerous_extensions():
    dangerous_files = [
        ("payload.html", "text/html"),
        ("exploit.svg", "image/svg+xml"),
        ("shell.php", "application/x-httpd-php"),
        ("script.js", "application/javascript"),
        ("binary.exe", "application/x-msdownload"),
        ("danger.sh", "application/x-sh"),
    ]
    for fname, ctype in dangerous_files:
        is_valid, err = validate_upload_security(fname, ctype)
        assert is_valid is False, f"Dangerous file {fname} should be rejected"


@pytest.mark.unit
def test_maintenance_receipt_upload_accepts_valid_documents():
    valid_files = [
        ("facture_revision.pdf", "application/pdf"),
        ("recu_vidange.jpg", "image/jpeg"),
        ("ticket_garage.png", "image/png"),
        ("facture_freins.webp", "image/webp"),
    ]
    for fname, ctype in valid_files:
        is_valid, err = validate_upload_security(fname, ctype)
        assert is_valid is True, f"Valid file {fname} should be accepted"
        assert err == "OK"
