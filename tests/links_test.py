import pytest
import requests
from pieces.urls import URLs
from typing import List, Tuple


def get_urls() -> List[Tuple[str, str]]:
    """Get all URLs from the URLs enum."""
    urls = []
    for name, member in URLs.__members__.items():
        urls.append((name, member.value))
    return urls


@pytest.mark.parametrize("url_name,url", get_urls())
def test_url_accessibility(url_name: str, url: str):
    """Test that each URL is accessible.
    
    Args:
        url_name: Name of the URL constant
        url: The actual URL to test
    """
    try:
        # Use GET with stream=True instead of HEAD as some servers don't support HEAD
        response = requests.get(url, timeout=10, allow_redirects=True, stream=True)
        response.close()  # Close the stream immediately
        
        # Assert that the status code indicates success (2xx or 3xx)
        assert response.status_code < 400, (
            f"{url_name} ({url}) returned status code {response.status_code}"
        )
    except requests.exceptions.Timeout:
        pytest.fail(f"{url_name} ({url}) timed out after 10 seconds")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"{url_name} ({url}) connection failed: {str(e)}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"{url_name} ({url}) request failed: {str(e)}")


@pytest.mark.skip(reason="This is an optional utility function for debugging")
def test_print_all_urls():
    """Utility test to print all URLs (useful for debugging)."""
    print("\nAll defined URLs:")
    for name, member in URLs.__members__.items():
        print(f"  {name}: {member.value}")
    assert True  # Always pass


def test_urls_enum_not_empty():
    """Test that the URLs enum contains at least one URL."""
    assert len(URLs.__members__) > 0, "URLs enum should contain at least one URL"


def test_all_urls_are_strings():
    """Test that all URL values are strings."""
    for name, member in URLs.__members__.items():
        assert isinstance(member.value, str), f"{name} value should be a string"
        assert len(member.value) > 0, f"{name} value should not be empty"


def test_all_urls_start_with_http():
    """Test that all URLs start with http:// or https://."""
    for name, member in URLs.__members__.items():
        url = member.value
        assert url.startswith(("http://", "https://")), (
            f"{name} URL should start with http:// or https://, got: {url}"
        )