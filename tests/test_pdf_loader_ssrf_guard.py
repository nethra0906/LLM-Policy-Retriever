import pytest

from policy_intel.ingestion.pdf_loader import UnsafePdfUrlError, _assert_public_url


def test_rejects_non_http_scheme():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("file:///etc/passwd")


def test_rejects_localhost():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("http://localhost/secret.pdf")


def test_rejects_loopback_ip():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("http://127.0.0.1/secret.pdf")


def test_rejects_cloud_metadata_ip():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("http://169.254.169.254/latest/meta-data/")


def test_rejects_private_ip_range():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("http://10.0.0.5/internal.pdf")


def test_rejects_missing_host():
    with pytest.raises(UnsafePdfUrlError):
        _assert_public_url("https:///no-host.pdf")


def test_allows_public_domain():
    # example.com resolves to a public IP; no exception expected.
    # Skipped automatically when the test environment has no network access.
    pytest.importorskip("socket")
    try:
        _assert_public_url("https://example.com/policy.pdf")
    except UnsafePdfUrlError as exc:
        if "Could not resolve host" in str(exc):
            pytest.skip("no network access in this environment")
        raise
