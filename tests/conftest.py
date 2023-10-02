"""Test configuration."""
import pytest


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, list[tuple[str, str]]]:
    """VCR configuration for the tests.

    :return: A replacement for the Authorization header in cassettes.
    """
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [("Authorization", "DUMMY")],
    }
